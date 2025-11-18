from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PrescriptionBase(BaseModel):
    medication: Optional[str]
    dosage: Optional[str]
    issued_date: Optional[datetime]

class PrescriptionCreate(PrescriptionBase):
    user_id: int
    doctor_id: int
    medication: str
    dosage: str
    issued_date: datetime

class PrescriptionOut(PrescriptionBase):
    id: int
    user_id: int
    doctor_id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "patient"

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
