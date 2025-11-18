from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    appointment_date: Optional[datetime] = None
    reason: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    user_id: int
    doctor_id: int
    appointment_date: datetime
    reason: str

class AppointmentOut(AppointmentBase):
    id: int
    user_id: int
    doctor_id: int

    class Config:
        orm_mode = True
