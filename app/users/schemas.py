from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: str | None = None
    password: str | None = None