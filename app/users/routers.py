from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()

# Pydantic model for user response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    status: Optional[str] = 'approved'
    is_active: bool

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    total: int
    pending: int
    approved: int

# ========== ADMIN ENDPOINTS ==========

@router.get("/", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users - Admin only"""
    users = db.query(User).all()
    return users

@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user statistics - Admin only"""
    total = db.query(User).count()
    
    # Check if status column exists
    try:
        pending = db.query(User).filter(User.status == 'pending').count()
        approved = db.query(User).filter(User.status == 'approved').count()
    except:
        # If status column doesn't exist yet
        pending = 0
        approved = total
    
    return UserStatsResponse(total=total, pending=pending, approved=approved)

@router.put("/{user_id}/approve")
def approve_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a pending user - Admin only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if status column exists
    if hasattr(user, 'status'):
        user.status = 'approved'
        db.commit()
    else:
        # If status column doesn't exist, add it first
        from sqlalchemy import Column, String
        user.__table__.append_column(Column('status', String, default='approved'))
        user.status = 'approved'
        db.commit()
    
    return {"message": "User approved successfully"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a user - Admin only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow admin to delete themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# ========== EXISTING ENDPOINTS (Updated for real DB) ==========

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

@router.put("/{user_id}")
def update_user(
    user_id: int, 
    update: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a user - Admin only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return {"id": user.id, "username": user.username, "email": user.email}