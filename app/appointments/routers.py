from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# Dummy in-memory storage for demonstration
appointments_db = {}

@router.get("/")
def get_appointments():
    return {"message": "List of appointments"}

# ------------------------------ NEW ENDPOINTS ------------------------------

# Appointment update model
class AppointmentUpdate(BaseModel):
    appointment_time: Optional[datetime]
    reason: Optional[str]
    status: Optional[str]

@router.put("/{appointment_id}", summary="Update an appointment")
def update_appointment(appointment_id: int, update: AppointmentUpdate):
    if appointment_id not in appointments_db:
        raise HTTPException(status_code=404, detail="Appointment not found")
    stored = appointments_db[appointment_id]
    update_data = update.dict(exclude_unset=True)
    stored.update(update_data)
    appointments_db[appointment_id] = stored
    return {"id": appointment_id, **stored}

@router.delete("/{appointment_id}", summary="Delete an appointment")
def delete_appointment(appointment_id: int):
    if appointment_id not in appointments_db:
        raise HTTPException(status_code=404, detail="Appointment not found")
    del appointments_db[appointment_id]
    return {"message": "Appointment deleted"}

# ------------------------------ ADD THIS POST ENDPOINT ------------------------------

class AppointmentCreate(BaseModel):
    appointment_time: datetime
    reason: str
    status: Optional[str] = "pending"

@router.post("/", summary="Create an appointment")
def create_appointment(appointment: AppointmentCreate):
    # Simple id generation
    appointment_id = len(appointments_db) + 1
    appointments_db[appointment_id] = appointment.dict()
    return {"id": appointment_id, **appointments_db[appointment_id]}