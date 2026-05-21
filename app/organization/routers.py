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

router = APIRouter(prefix="/api/organization", tags=["Organization"])

class OrganizationCreate(BaseModel):
    name: str
    license_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_status: str = "trial"
    allowed_modules: List[str] = []

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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's organization module settings"""
    user = db.query(User).filter(User.id == current_user.get('id')).first()
    
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get('role') != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get('role') != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_modules = org.allowed_modules or []
    org.allowed_modules = data.get("allowed_modules", [])
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.get('is_super_admin'):
        raise HTTPException(status_code=403, detail="Super admin only")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.get('is_super_admin'):
        raise HTTPException(status_code=403, detail="Super admin only")
    
    new_org = Organization(
        name=org_data.name,
        license_number=org_data.license_number,
        email=org_data.email,
        phone=org_data.phone,
        address=org_data.address,
        subscription_status=org_data.subscription_status,
        allowed_modules=org_data.allowed_modules
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
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
    org_data: OrganizationUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.get('is_super_admin'):
        raise HTTPException(status_code=403, detail="Super admin only")
    
    old_org = db.query(Organization).filter(Organization.id == org_id).first()
    if not old_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_data = {
        "name": old_org.name,
        "license_number": old_org.license_number,
        "subscription_status": old_org.subscription_status,
        "allowed_modules": old_org.allowed_modules
    }
    
    old_org.name = org_data.name
    old_org.license_number = org_data.license_number
    old_org.email = org_data.email
    old_org.phone = org_data.phone
    old_org.address = org_data.address
    old_org.subscription_status = org_data.subscription_status
    old_org.allowed_modules = org_data.allowed_modules
    
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
        action='UPDATE',
        resource_type='ORGANIZATION',
        resource_id=org_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        old_value=old_data,
        new_value=org_data.dict()
    )
    
    return {"message": "Organization updated"}


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.get('is_super_admin'):
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
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.get('is_super_admin'):
        raise HTTPException(status_code=403, detail="Super admin only")
    
    orgs = db.query(Organization).all()
    
    log_audit(
        db=db,
        user_id=current_user.get('id'),
        username=current_user.get('username'),
        user_role=current_user.get('role'),
        action='READ',
        resource_type='ORGANIZATIONS_LIST',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return [{"id": o.id, "name": o.name, "license_number": o.license_number, 
             "email": o.email, "phone": o.phone, "address": o.address,
             "subscription_status": o.subscription_status, 
             "allowed_modules": o.allowed_modules or []} for o in orgs]

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
                "profile_image": d.profile_image
            }
            for d in doctors
        ]
    }    
