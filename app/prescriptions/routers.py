from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Prescription
from app.schemas import PrescriptionCreate, PrescriptionOut
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=PrescriptionOut)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = Prescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

@router.get("/", response_model=list[PrescriptionOut])
def get_prescriptions(db: Session = Depends(get_db)):
    prescriptions = db.query(Prescription).all()
    return prescriptions

@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

# ---------------- NEW ENDPOINTS BELOW THIS LINE ----------------

class PrescriptionUpdate(BaseModel):
    medication: Optional[str]
    dosage: Optional[str]
    issued_date: Optional[datetime]
    user_id: Optional[int]
    doctor_id: Optional[int]

@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(
    prescription_id: int,
    update: PrescriptionUpdate,
    db: Session = Depends(get_db)
):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prescription, key, value)
    db.commit()
    db.refresh(prescription)
    return prescription

@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db)
):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(prescription)
    db.commit()
    return {"message": "Prescription deleted"}