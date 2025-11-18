from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Prescription
from app.schemas import PrescriptionCreate, PrescriptionOut

router = APIRouter(tags=["Prescriptions"])

@router.post("/", response_model=PrescriptionOut)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    try:
        db_prescription = Prescription(**prescription.dict())
        db.add(db_prescription)
        db.commit()
        db.refresh(db_prescription)
        return db_prescription
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[PrescriptionOut])
def get_prescriptions(db: Session = Depends(get_db)):
    return db.query(Prescription).all()

@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(prescription_id: int, updated: PrescriptionCreate, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    for key, value in updated.dict().items():
        setattr(prescription, key, value)
    db.commit()
    db.refresh(prescription)
    return prescription

@router.delete("/{prescription_id}")
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(prescription)
    db.commit()
    return {"detail": "Prescription deleted successfully"}
