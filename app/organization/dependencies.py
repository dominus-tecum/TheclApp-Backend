from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.models import Organization
from app.authentication.auth import get_current_user

async def get_current_organization(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Organization:
    """Get current user's organization and verify access"""
    
    # Get user from database
    user = db.query(User).filter(User.id == int(current_user.get('id'))).first()
    
    if not user:
        raise HTTPException(status_code=403, detail="User not found")
    
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="No organization assigned")
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    
    if not org:
        raise HTTPException(status_code=403, detail="Organization not found")
    
    if not org.is_active:
        raise HTTPException(status_code=403, detail="Organization is inactive")
    
    # Check subscription status (skip for admin users)
    if current_user.get('role') != 'admin':
        if org.subscription_status not in ['active', 'trial']:
            raise HTTPException(status_code=403, detail="Subscription expired")
    
    return org
    
async def get_org_module_settings(
    org: Organization = Depends(get_current_organization)
) -> dict:
    """Get organization's module access settings"""
    return {
        "id": org.id,
        "name": org.name,
        "allowed_modules": org.allowed_modules or []
    }
