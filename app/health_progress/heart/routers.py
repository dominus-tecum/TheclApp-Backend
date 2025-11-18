# app/health_progress/heart/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.health_progress.heart.models import HeartEntry

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

# POST /api/health-progress/heart/entries
@router.post("/entries")
async def create_heart_entry(data: dict, db: Session = Depends(get_db_session)):
    """Create a new heart disease entry"""
    try:
        print("📥 Creating heart entry:", data)
        
        # Create entry with flat data structure
        db_entry = HeartEntry(
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
            chest_pain_level=data.get('chest_pain_level'),
            pain_location=data.get('pain_location'),
            weight=data.get('weight'),
            swelling_level=data.get('swelling_level'),
            breathing_difficulty=data.get('breathing_difficulty'),
            condition_type=data.get('condition_type')
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return {
            "message": "Heart disease entry created successfully",
            "id": db_entry.id,
            "patient_id": db_entry.patient_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

# GET /api/health-progress/heart/entries
@router.get("/entries")
async def get_all_heart_entries(db: Session = Depends(get_db_session)):
    """Get all heart disease entries"""
    try:
        entries = db.query(HeartEntry).all()
        
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
                    "chest_pain_level": entry.chest_pain_level,
                    "pain_location": entry.pain_location,
                    "weight": entry.weight,
                    "swelling_level": entry.swelling_level,
                    "breathing_difficulty": entry.breathing_difficulty,
                    "condition_type": entry.condition_type,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None
                }
                for entry in entries
            ],
            "total": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")

# GET /api/health-progress/heart/entries/{patient_id}/{date}
@router.get("/entries/{patient_id}/{date}")
async def get_heart_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Get specific heart disease entry for patient and date"""
    try:
        entry = db.query(HeartEntry).filter(
            HeartEntry.patient_id == patient_id,
            HeartEntry.submission_date == date
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
                "chest_pain_level": entry.chest_pain_level,
                "pain_location": entry.pain_location,
                "weight": entry.weight,
                "swelling_level": entry.swelling_level,
                "breathing_difficulty": entry.breathing_difficulty,
                "condition_type": entry.condition_type,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

# GET /api/health-progress/heart/check/{patient_id}/{date}
@router.get("/check/{patient_id}/{date}")
async def check_heart_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Check if heart disease entry exists"""
    try:
        exists = db.query(HeartEntry).filter(
            HeartEntry.patient_id == patient_id,
            HeartEntry.submission_date == date
        ).first() is not None
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")

# GET /api/health-progress/heart/patient/{patient_id}
@router.get("/patient/{patient_id}")
async def get_patient_heart_entries(patient_id: int, db: Session = Depends(get_db_session)):
    """Get all heart disease entries for a patient"""
    try:
        entries = db.query(HeartEntry).filter(
            HeartEntry.patient_id == patient_id
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
                    "chest_pain_level": entry.chest_pain_level,
                    "pain_location": entry.pain_location,
                    "weight": entry.weight,
                    "swelling_level": entry.swelling_level,
                    "breathing_difficulty": entry.breathing_difficulty,
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