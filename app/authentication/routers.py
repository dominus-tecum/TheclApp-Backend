from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, PatientProfile, Organization, PatientDoctorAssignment, UserRole
from .schemas import UserRegister, UserLogin, UserRead
from .service import create_user 
from .auth import create_access_token, get_current_user, authenticate_user
from jose import jwt
from app.core.config import settings  # ✅ IMPORT SETTINGS
from app.utils.audit import log_audit



router = APIRouter(tags=["Authentication"])

# In-memory storage for refresh tokens
REFRESH_TOKENS = {}

# Helper function to create refresh tokens
def create_refresh_token(username: str, user_id: int):
    """Create a refresh token valid for 7 days"""
    expire = datetime.utcnow() + timedelta(days=7)
    refresh_token = jwt.encode(
        {
            "sub": username,
            "user_id": user_id,
            "type": "refresh",
            "exp": expire
        },
        settings.JWT_SECRET_KEY,  # ✅ USE SAME SECRET KEY
        algorithm=settings.ALGORITHM  # ✅ USE SAME ALGORITHM
    )
    
    # Store it in memory
    REFRESH_TOKENS[refresh_token] = {
        "user_id": user_id,
        "username": username,
        "expires_at": expire
    }
    
    return refresh_token



@router.post("/register", response_model=UserRead)
def register(user: UserRegister, request: Request, db: Session = Depends(get_db)):
    print(f"🔍 REGISTER - Full received data: {user.dict()}")
    print(f"🔍 REGISTER - organization_id: {user.organization_id}")
    print("=" * 50)
    print("🔍 REGISTER - Received data:")
    print(f"   username: {user.username}")
    print(f"   email: {user.email}")
    print(f"   organization_id: {user.organization_id}")
    print(f"   organization_id type: {type(user.organization_id)}")
    print("=" * 50)


    print(f"🔍 REGISTER - Received: {user.dict()}")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        print("❌ REGISTER - Email already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        print("❌ REGISTER - Username already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="Invalid organization")

    created_user = create_user(db, user, user.organization_id)
    print(f"✅ REGISTER - User created: {created_user.id}, {created_user.email}, {created_user.username}")
    created_user.status = 'pending'
    db.commit()
    
    # CREATE PATIENT PROFILE
    existing_patient = db.query(PatientProfile).filter(PatientProfile.user_id == created_user.id).first()
    if not existing_patient:
        new_patient = PatientProfile(
            user_id=created_user.id,
            name=user.name or created_user.name or user.username,
            email=user.email,
            phone_number=user.phone_number,
            high_risk=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        print(f"✅ Patient profile created with ID: {new_patient.id}")
    else:
        print(f"⚠️ Patient profile already exists: {existing_patient.id}")

    # ========== DOCTOR ASSIGNMENT BLOCK - CORRECTED ==========
    # Assign patient to selected doctor (if doctor_id provided)
    if user.doctor_id:
        print(f"🔍 Attempting to assign patient to doctor_id: {user.doctor_id}")
        
        # Verify doctor exists and belongs to same organization
        doctor = db.query(User).filter(
            User.id == user.doctor_id,
            User.role == UserRole.DOCTOR,
            User.organization_id == user.organization_id
        ).first()
        
        if doctor:
            # Create the assignment record
            assignment = PatientDoctorAssignment(
                patient_id=created_user.id,
                doctor_id=user.doctor_id,
                assigned_date=datetime.now(),
                reason="Patient selected during registration"
            )
            db.add(assignment)
            db.commit()
            print(f"✅ Patient assigned to doctor ID: {user.doctor_id} (Dr. {doctor.name})")
            
            # Audit log for doctor assignment
            log_audit(
                db=db,
                user_id=created_user.id,
                username=created_user.username,
                user_role=created_user.role.value,
                action='ASSIGN',
                resource_type='DOCTOR_ASSIGNMENT',
                patient_id=created_user.id,
                status='success',
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                new_value={"doctor_id": user.doctor_id, "reason": "Patient selected during registration"}
            )
        else:
            print(f"⚠️ Doctor ID {user.doctor_id} not found or invalid (not a doctor or wrong organization)")
    # ========== END OF DOCTOR ASSIGNMENT BLOCK ==========

    # Audit log for registration
    log_audit(
        db=db,
        user_id=created_user.id,
        username=created_user.username,
        user_role=created_user.role.value,
        action='REGISTER',
        resource_type='USER',
        resource_id=created_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"organization_id": user.organization_id, "doctor_id": user.doctor_id if user.doctor_id else None}
    )
    
    return created_user


@router.post("/login")
def login(
    user: UserLogin, 
    request: Request,  # ← ADD THIS
    db: Session = Depends(get_db)
):
    print(f"🔍 LOGIN - Attempt: {user.email}")
    
    authenticated_user = authenticate_user(db, user.email, user.password)
    
    if not authenticated_user:
        # ✅ ADD THIS AUDIT LOG
        log_audit(
            db=db,
            username=user.email,
            action='LOGIN_FAILED',
            resource_type='AUTH',
            status='failed',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        print("❌ LOGIN - Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # ✅ STATUS CHECK - BLOCK PENDING/REJECTED/INACTIVE USERS
    print(f"🔍 LOGIN - User status: {authenticated_user.status}")
    
    if authenticated_user.status == 'pending':
        # ✅ ADD THIS AUDIT LOG
        log_audit(
            db=db,
            user_id=authenticated_user.id,
            username=authenticated_user.username,
            action='LOGIN_DENIED',
            resource_type='AUTH',
            status='denied',
            purpose='PENDING_APPROVAL',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        print("❌ LOGIN - Account pending approval")
        raise HTTPException(
            status_code=403, 
            detail="Account pending approval. Please wait for admin verification."
        )
    
    if authenticated_user.status == 'rejected':
        # ✅ ADD THIS AUDIT LOG
        log_audit(
            db=db,
            user_id=authenticated_user.id,
            username=authenticated_user.username,
            action='LOGIN_DENIED',
            resource_type='AUTH',
            status='denied',
            purpose='REJECTED',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        print("❌ LOGIN - Account rejected")
        raise HTTPException(
            status_code=403, 
            detail="Account registration was rejected. Please contact support."
        )
    
    if authenticated_user.status == 'inactive':
        # ✅ ADD THIS AUDIT LOG
        log_audit(
            db=db,
            user_id=authenticated_user.id,
            username=authenticated_user.username,
            action='LOGIN_DENIED',
            resource_type='AUTH',
            status='denied',
            purpose='INACTIVE',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        print("❌ LOGIN - Account inactive")
        raise HTTPException(
            status_code=403, 
            detail="Account is deactivated. Please contact support."
        )
    
    # ✅ SUCCESSFUL LOGIN - ADD THIS AUDIT LOG
    log_audit(
        db=db,
        user_id=authenticated_user.id,
        username=authenticated_user.username,
        user_role=authenticated_user.role.value,
        action='LOGIN_SUCCESS',
        resource_type='AUTH',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    print(f"✅ LOGIN - Success for: {authenticated_user.email}, {authenticated_user.role}")
    
    # Create tokens (your existing code)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": authenticated_user.username}, 
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        username=authenticated_user.username,
        user_id=authenticated_user.id
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "username": authenticated_user.username,
            "email": authenticated_user.email,
            "role": authenticated_user.role,
            "name": authenticated_user.name,
            "phone_number": authenticated_user.phone_number,
            "status": authenticated_user.status,
            "organization_id": authenticated_user.organization_id
        }
    }
    
    if authenticated_user.status == 'inactive':
        print("❌ LOGIN - Account inactive")
        raise HTTPException(
            status_code=403, 
            detail="Account is deactivated. Please contact support."
        )
    
    # Only approved users reach here
    print(f"✅ LOGIN - Success for: {authenticated_user.email}, {authenticated_user.role}")
    
    # 1. Create access token (30 minutes)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": authenticated_user.username}, 
        expires_delta=access_token_expires
    )
    
    # 2. Create refresh token (7 days)
    refresh_token = create_refresh_token(
        username=authenticated_user.username,
        user_id=authenticated_user.id
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "username": authenticated_user.username,
            "email": authenticated_user.email,
            "role": authenticated_user.role,
            "name": authenticated_user.name,
            "phone_number": authenticated_user.phone_number,
            "status": authenticated_user.status  # ← IMPORTANT: Send status to frontend
        }
    }
@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    Get new access token using refresh token
    """
    print(f"🔍 REFRESH - Attempt with token: {refresh_token[:20]}...")
    
    # Check if token exists
    if refresh_token not in REFRESH_TOKENS:
        print("❌ REFRESH - Token not found in storage")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_data = REFRESH_TOKENS[refresh_token]
    
    # Check if expired
    if datetime.utcnow() > token_data["expires_at"]:
        del REFRESH_TOKENS[refresh_token]  # Clean up expired token
        print("❌ REFRESH - Token expired")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Create new access token (30 minutes)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": token_data["username"]}, 
        expires_delta=access_token_expires
    )
    
    print(f"✅ REFRESH - New access token created for: {token_data['username']}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }

@router.get("/me", response_model=UserRead)
def get_current_user_info(
    request: Request,
    current_user: dict = Depends(get_current_user),  # ← CHANGE User to dict
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.get('id')).first()  # ← use .get('id')
    
    # ✅ AUDIT LOG
    log_audit(
        db=db,
        user_id=user.id,
        username=user.username,
        user_role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        action='READ',
        resource_type='USER_PROFILE',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "name": user.name,
        "phone_number": user.phone_number,
        "status": user.status,
        "is_super_admin": getattr(user, 'is_super_admin', False)
    }


from pydantic import BaseModel
from typing import Dict

class ConsentData(BaseModel):
    consents: Dict[str, bool]
    consent_version: str
    device_info: str

@router.post("/save-consent")
async def save_consent(
    consent_data: ConsentData,  # ← This makes it read from body, not query
    request: Request,
    db: Session = Depends(get_db)
):
    from app.models import AuditLog
    from datetime import datetime
    
    # Store in session for now (user not yet registered)
    request.session['pending_consent'] = consent_data.dict()
    
    # Log the consent action
    audit = AuditLog(
        action="consent_given",
        resource_type="consent_form",
        ip_address=request.client.host,
        user_agent=consent_data.device_info,
        created_at=datetime.now()
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Consent recorded"}

@router.post("/update-super-admin")
def update_super_admin(
    email: str = Body(None),
    password: str = Body(None),
    username: str = Body(None),
    organization_id: int = Body(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update super admin account - Only existing super admin can use this"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # SECURITY: Only existing super admin can access
    if not current_user.get('is_super_admin'):
        raise HTTPException(status_code=403, detail="Super admin only")
    
    # Get the super admin user (usually the one making the request)
    admin_user = db.query(User).filter(User.id == current_user.get('id')).first()
    
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    # Update fields if provided
    if email:
        admin_user.email = email
    if username:
        admin_user.username = username
    if password:
        admin_user.password_hash = pwd_context.hash(password)
    
    # Ensure super admin flag stays true
    admin_user.is_super_admin = True
    admin_user.role = UserRole.ADMIN
    admin_user.status = 'approved'
    
    db.commit()
    db.refresh(admin_user)
    
    return {
        "message": "Super admin updated successfully",
        "user": {
            "id": admin_user.id,
            "email": admin_user.email,
            "username": admin_user.username,
            "is_super_admin": admin_user.is_super_admin
        }
    } 


@router.post("/create-super-admin-temp")
def create_super_admin_temp(
    email: str = Body(...),
    password: str = Body(...),
    username: str = Body(...),
    db: Session = Depends(get_db)
):
    """TEMPORARY - Create super admin"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        existing.is_super_admin = True
        existing.role = UserRole.ADMIN
        existing.status = 'approved'
        existing.organization_id = None  # ← Also add this for existing users
        db.commit()
        return {"message": "Existing user upgraded to super admin"}
    
    hashed = pwd_context.hash(password)
    new_admin = User(
        username=username,
        email=email,
        password_hash=hashed,
        role=UserRole.ADMIN,
        is_super_admin=True,
        organization_id=None,  # ← CHANGED from 1 to None
        status='approved',
        name=username
    )
    db.add(new_admin)
    db.commit()
    
    return {"message": "Super admin created", "user_id": new_admin.id}     