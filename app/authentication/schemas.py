from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models import UserRole

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.PATIENT
    
    # COMMON FIELDS FOR ALL USERS
    name: Optional[str] = None
    phone_number: Optional[str] = None
    emirates_id: Optional[str] = None
    passport_number: Optional[str] = None
    
    # STAFF-SPECIFIC FIELDS
    specialization: Optional[str] = None
    department: Optional[str] = None
    organization_id: int
    doctor_id: Optional[int] = None  # ← ADD THIS

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    
    # COMMON FIELDS FOR ALL USERS
    name: Optional[str] = None
    phone_number: Optional[str] = None
    emirates_id: Optional[str] = None
    passport_number: Optional[str] = None
    
    # STAFF-SPECIFIC FIELDS
    specialization: Optional[str] = None
    department: Optional[str] = None
    
    # Status fields
    status: Optional[str] = "pending"  # 'pending' or 'approved'
    is_super_admin: bool = False

    model_config = {
        "from_attributes": True
    }