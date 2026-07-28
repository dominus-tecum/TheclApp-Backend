from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Organization
from app.models import User
from app.authentication.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from app.utils.audit import log_audit
from datetime import datetime
import base64

router = APIRouter(prefix="/api/organization", tags=["Organization"])

class OrganizationCreate(BaseModel):
    name: str
    license_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_status: str = "trial"
    allowed_modules: List[str] = []
    type: Optional[str] = "hospital"  # ← ADD THIS

class OrganizationUpdate(BaseModel):
    name: str
    license_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_status: str = "trial"
    allowed_modules: List[str] = []


@router.get("/settings")
async def get_org_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's organization module settings"""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user or not user.organization_id:
        return {"allowed_modules": []}
    
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    
    if not org:
        return {"allowed_modules": []}
    
    return {
        "organization_id": org.id,
        "organization_name": org.name,
        "allowed_modules": org.allowed_modules or []
    }


@router.get("/organizations/{org_id}/modules")
async def get_org_modules(
    org_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='ORGANIZATION_MODULES',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {"allowed_modules": org.allowed_modules or []}


@router.put("/organizations/{org_id}/modules")
async def update_org_modules(
    org_id: int,
    data: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_modules = org.allowed_modules or []
    org.allowed_modules = data.get("allowed_modules", [])
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='UPDATE',
        resource_type='ORGANIZATION_MODULES',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        old_value={"allowed_modules": old_modules},
        new_value={"allowed_modules": org.allowed_modules}
    )
    
    return {"message": "Updated", "allowed_modules": org.allowed_modules}


@router.get("/organizations/{org_id}")
async def get_organization(
    org_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='ORGANIZATION',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "id": org.id,
        "name": org.name,
        "license_number": org.license_number,
        "email": org.email,
        "phone": org.phone,
        "address": org.address,
        "subscription_status": org.subscription_status,
        "allowed_modules": org.allowed_modules or []
    }


@router.post("/organizations")
async def create_organization(
    org_data: OrganizationCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")

            # ✅ ADD THIS DUPLICATE CHECK RIGHT HERE
    if org_data.license_number:
        existing_org = db.query(Organization).filter(
            Organization.license_number == org_data.license_number
        ).first()
        
        if existing_org:
            raise HTTPException(
                status_code=400, 
                detail=f"License number '{org_data.license_number}' is already registered to organization '{existing_org.name}'"
            )
    
    new_org = Organization(
        name=org_data.name,
        license_number=org_data.license_number,
        email=org_data.email,
        phone=org_data.phone,
        address=org_data.address,
        subscription_status=org_data.subscription_status,
        allowed_modules=org_data.allowed_modules,
        type=org_data.type
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

        # ========== ADD THIS BLOCK ==========
    # If this is a pharmacy, also create record in pharmacies table
    if org_data.type == 'pharmacy':
        from app.pharmacy.models import Pharmacy
        from datetime import datetime
        new_pharmacy = Pharmacy(
            id=new_org.id,  # Same ID as organization
            name=new_org.name,
            phone_number=new_org.phone,
            address=new_org.address,
            is_active=True,
            created_at=datetime.now()
        )
        db.add(new_pharmacy)
        db.commit()
    # ========== END OF ADDED BLOCK ==========
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='CREATE',
        resource_type='ORGANIZATION',
        resource_id=new_org.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value=org_data.dict()
    )
    
    return {"id": new_org.id, "message": "Organization created"}


@router.put("/organizations/{org_id}")
async def update_organization(
    org_id: int,
    org_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_active = org.is_active
    
    # Update only fields that are provided
    if 'name' in org_data:
        org.name = org_data['name']
    if 'license_number' in org_data:
        org.license_number = org_data['license_number']
    if 'email' in org_data:
        org.email = org_data['email']
    if 'phone' in org_data:
        org.phone = org_data['phone']
    if 'address' in org_data:
        org.address = org_data['address']
    if 'subscription_status' in org_data:
        org.subscription_status = org_data['subscription_status']
    if 'allowed_modules' in org_data:
        org.allowed_modules = org_data['allowed_modules']
    if 'is_active' in org_data:
        org.is_active = org_data['is_active']
    
    db.commit()
    
    # ✅ AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='UPDATE',
        resource_type='ORGANIZATION',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        old_value={"is_active": old_active},
        new_value={"is_active": org.is_active}
    )
    
    return {"message": "Organization updated"}


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_data = {
        "name": org.name,
        "license_number": org.license_number,
        "allowed_modules": org.allowed_modules
    }
    
    db.delete(org)
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='DELETE',
        resource_type='ORGANIZATION',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        old_value=old_data
    )
    
    return {"message": "Organization deleted"}


@router.get("/organizations")
async def get_all_organizations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    type: Optional[str] = None
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    query = db.query(Organization)
    if type:
        query = query.filter(Organization.type == type)
    orgs = query.all()
    
    # ✅ AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='ORGANIZATIONS_LIST',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return [{
        "id": o.id,
        "name": o.name,
        "license_number": o.license_number, 
        "email": o.email,
        "phone": o.phone,
        "address": o.address,
        "subscription_status": o.subscription_status, 
        "allowed_modules": o.allowed_modules or [],
        "type": o.type or "hospital",
        "is_active": o.is_active  # ← ADD THIS
    } for o in orgs]

@router.get("/public-organizations")
async def get_public_organizations(db: Session = Depends(get_db)):
    """Get list of active organizations for registration (no auth required)"""
    orgs = db.query(Organization).filter(
        Organization.is_active == True,
        Organization.subscription_status.in_(['active', 'trial'])
    ).all()
    
    return [{"id": o.id, "name": o.name} for o in orgs]  


@router.get("/doctors/by-organization")
def get_doctors_by_organization(
    organization_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all active doctors in an organization (no auth required for registration)"""
    from app.models import User, UserRole
    
    doctors = db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.organization_id == organization_id,
        User.is_active == True,
        User.status == 'approved'
    ).all()
    
    return {
        "doctors": [
            {
                "id": d.id,
                "name": d.name,
                "specialization": d.specialization,
                "department": d.department,
                "experience_years": d.experience_years,
                "profile_image": base64.b64encode(d.profile_image).decode('utf-8') if d.profile_image else None
            }
            for d in doctors
        ]
    }    

@router.get("/organizations")
async def get_all_organizations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    type: Optional[str] = None
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    query = db.query(Organization)
    
    if type:
        query = query.filter(Organization.type == type)
    
    orgs = query.all()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='ORGANIZATIONS_LIST',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return [{
        "id": o.id,
        "name": o.name,
        "license_number": o.license_number, 
        "email": o.email,
        "phone": o.phone,
        "address": o.address,
        "subscription_status": o.subscription_status, 
        "allowed_modules": o.allowed_modules or [],
        "type": o.type or "hospital"
    } for o in orgs]

@router.post("/organizations/bulk-delete")
async def bulk_delete_organizations(
    data: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin only")
    
    org_ids = data.get('organization_ids', [])
    deleted_count = 0
    failed_ids = []
    
    for org_id in org_ids:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if org:
            org.deleted_at = datetime.now()
            deleted_count += 1
        else:
            failed_ids.append(org_id)
    
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='BULK_DELETE',
        resource_type='ORGANIZATION',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"deleted_count": deleted_count, "failed_ids": failed_ids}
    )
    
    return {"message": f"Deleted {deleted_count} organizations", "deleted_count": deleted_count, "failed_ids": failed_ids}    