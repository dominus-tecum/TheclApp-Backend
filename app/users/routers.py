from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models import User

router = APIRouter()

# Pydantic model for user response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# FIXED: Now returns real users from database
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all users from the database"""
    users = db.query(User).all()
    return users

# ------------------------------ EXISTING ENDPOINTS ------------------------------

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]
    full_name: Optional[str]
    is_active: Optional[bool]

@router.put("/{user_id}", summary="Update a user")
def update_user(user_id: int, update: UserUpdate):
    # Keeping your existing dummy implementation for now
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    stored = users_db[user_id]
    update_data = update.dict(exclude_unset=True)
    stored.update(update_data)
    users_db[user_id] = stored
    return {"id": user_id, **stored}

@router.delete("/{user_id}", summary="Delete a user")
def delete_user(user_id: int):
    # Keeping your existing dummy implementation for now
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return {"message": "User deleted"}

# Dummy in-memory storage for demonstration (keeping your existing)
users_db = {}