from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Appointment
from app.appointments.schemas import AppointmentCreate, AppointmentOut
from app.models import User  # <-- Updated import

router = APIRouter()

# Create appointment
@router.post("/", response_model=AppointmentOut)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Validate user existence
    user = db.query(User).filter(User.id == appointment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# List all appointments
@router.get("/", response_model=List[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return appointments