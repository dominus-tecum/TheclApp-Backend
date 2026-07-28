from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime

from app.database import get_db
from app.models import User
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    try:
        # Decode the JWT token using your settings
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Role-based dependencies
async def get_current_patient(
    current_user: User = Depends(get_current_user)
):
    """Require patient role"""
    if not current_user.is_patient():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )
    return current_user

async def get_current_doctor(
    current_user: User = Depends(get_current_user)
):
    """Require doctor role"""
    if not current_user.is_doctor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    """Require admin role"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_visible_patient_ids(current_user: dict, db: Session):
    """
    Get list of patient IDs a user can see based on their role.
    Returns:
    - None: User can see ALL patients in their organization (Clinic Admin)
    - []: User can see NO patients (Doctor with no assigned patients)
    - [1,2,3]: User can see ONLY these patients (Doctor with assigned patients)
    """
    from app.models import PatientDoctorAssignment
    
    # Super admin cannot see patient data
    if current_user.is_super_admin:
        return []
    
    # Clinic admin sees all patients in their organization
    if current_user.role.value == 'admin':
        return None  # None means "all patients in org"
    
    # Doctor sees only assigned patients
    if current_user.role.value == 'doctor':
        assignments = db.query(PatientDoctorAssignment.patient_id).filter(
            PatientDoctorAssignment.doctor_id == current_user.id,
            PatientDoctorAssignment.end_date == None
        ).all()
        return [a[0] for a in assignments]  # Returns list of patient IDs, empty list if none
    
    # Patients see only themselves (will implement later)
    if current_user.role.value == 'patient':
        return [current_user.id]
    
    # Default: no access
    return []    