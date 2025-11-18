# app/health_progress/hypertension/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.health_progress.hypertension.models import HypertensionEntry

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

# POST /api/health-progress/hypertension/entries
@router.post("/entries")
async def create_hypertension_entry(data: dict, db: Session = Depends(get_db_session)):
    """Create a new hypertension entry"""
    try:
        print("📥 Creating hypertension entry:", data)
        
        # Create entry with flat data structure from frontend
        db_entry = HypertensionEntry(
            patient_id=data.get('patient_id'),
            patient_name=data.get('patient_name'),
            submission_date=data.get('submission_date'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            energy_level=data.get('energy_level'),
            sleep_hours=data.get('sleep_hours'),
            sleep_quality=data.get('sleep_quality'),
            medications=data.get('medications'),
            symptoms=data.get('symptoms'),
            notes=data.get('notes'),
            status=data.get('status'),
            condition_type=data.get('condition_type')
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return {
            "message": "Hypertension entry created successfully",
            "id": db_entry.id,
            "patient_id": db_entry.patient_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

# GET /api/health-progress/hypertension/entries
@router.get("/entries")
async def get_all_hypertension_entries(db: Session = Depends(get_db_session)):
    """Get all hypertension entries"""
    try:
        entries = db.query(HypertensionEntry).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "status": entry.status,
                    "condition_type": entry.condition_type,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None
                }
                for entry in entries
            ],
            "total": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")

# GET /api/health-progress/hypertension/entries/{patient_id}/{date}
@router.get("/entries/{patient_id}/{date}")
async def get_hypertension_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Get specific hypertension entry for patient and date"""
    try:
        entry = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id,
            HypertensionEntry.submission_date == date
        ).first()
        
        if not entry:
            return {
                "exists": False,
                "data": None,
                "patient_id": patient_id,
                "date": date
            }
        
        return {
            "exists": True,
            "data": {
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "energy_level": entry.energy_level,
                "sleep_hours": entry.sleep_hours,
                "sleep_quality": entry.sleep_quality,
                "medications": entry.medications,
                "symptoms": entry.symptoms,
                "notes": entry.notes,
                "status": entry.status,
                "condition_type": entry.condition_type,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

# GET /api/health-progress/hypertension/check/{patient_id}/{date}
@router.get("/check/{patient_id}/{date}")
async def check_hypertension_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Check if hypertension entry exists"""
    try:
        exists = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id,
            HypertensionEntry.submission_date == date
        ).first() is not None
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")

# GET /api/health-progress/hypertension/patient/{patient_id}
@router.get("/patient/{patient_id}")
async def get_patient_hypertension_entries(patient_id: int, db: Session = Depends(get_db_session)):
    """Get all hypertension entries for a patient"""
    try:
        entries = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id
        ).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "status": entry.status,
                    "condition_type": entry.condition_type,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None
                }
                for entry in entries
            ],
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patient entries: {str(e)}")