from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from .models import CancerEntry
from . import services, schemas

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_cancer_service(db: Session = Depends(get_db)):
    return services.CancerProgressService(db)

@router.post("/entries", response_model=schemas.CancerEntryResponse)
async def create_cancer_entry(
    data: dict,  # ✅ Accept raw dict like kidney
    service: services.CancerProgressService = Depends(get_cancer_service)
):
    """Create a new cancer entry with flattened structure"""
    try:
        print("🎯 CANCER ROUTER: Creating entry with flattened data structure")
        print("🔍 RECEIVED RAW DATA:", data)
        
        # ✅ Use service to handle the data mapping and creation
        db_entry = service.create_entry(data)
        
        # ✅ Return the response with proper FLATTENED structure
        return schemas.CancerEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            status=db_entry.status,
            
            # Common data (flattened)
            blood_pressure_systolic=db_entry.blood_pressure_systolic,
            blood_pressure_diastolic=db_entry.blood_pressure_diastolic,
            energy_level=db_entry.energy_level,
            sleep_hours=db_entry.sleep_hours,
            sleep_quality=db_entry.sleep_quality,
            medications=db_entry.medications,
            symptoms=db_entry.symptoms,
            notes=db_entry.notes,
            
            # Cancer-specific fields (flattened)
            pain_level=db_entry.pain_level,
            pain_location=db_entry.pain_location,
            side_effects=db_entry.side_effects,
            
            condition_type=db_entry.condition_type,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status
        )
        
    except Exception as e:
        print(f"❌ CANCER ROUTER: Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

@router.get("/entries")
async def get_all_cancer_entries(db: Session = Depends(get_db_session)):
    """Get all cancer entries"""
    try:
        entries = db.query(CancerEntry).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    
                    # Common data (flattened)
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    
                    # Cancer-specific fields (flattened)
                    "pain_level": entry.pain_level,
                    "pain_location": entry.pain_location,
                    "side_effects": entry.side_effects,
                    
                    "condition_type": entry.condition_type,
                    "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                    "urgency_status": entry.urgency_status
                }
                for entry in entries
            ],
            "total": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")

@router.get("/entries/{patient_id}/{date}")
async def get_cancer_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Get specific cancer entry for patient and date"""
    try:
        entry = db.query(CancerEntry).filter(
            CancerEntry.patient_id == patient_id,
            CancerEntry.submission_date == date
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
                "status": entry.status,
                
                # Common data (flattened)
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "energy_level": entry.energy_level,
                "sleep_hours": entry.sleep_hours,
                "sleep_quality": entry.sleep_quality,
                "medications": entry.medications,
                "symptoms": entry.symptoms,
                "notes": entry.notes,
                
                # Cancer-specific fields (flattened)
                "pain_level": entry.pain_level,
                "pain_location": entry.pain_location,
                "side_effects": entry.side_effects,
                
                "condition_type": entry.condition_type,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "urgency_status": entry.urgency_status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

@router.get("/check/{patient_id}/{date}")
async def check_cancer_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Check if cancer entry exists"""
    try:
        exists = db.query(CancerEntry).filter(
            CancerEntry.patient_id == patient_id,
            CancerEntry.submission_date == date
        ).first() is not None
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")

@router.get("/patient/{patient_id}")
async def get_patient_cancer_entries(patient_id: int, db: Session = Depends(get_db_session)):
    """Get all cancer entries for a patient"""
    try:
        entries = db.query(CancerEntry).filter(
            CancerEntry.patient_id == patient_id
        ).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    
                    # Common data (flattened)
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    
                    # Cancer-specific fields (flattened)
                    "pain_level": entry.pain_level,
                    "pain_location": entry.pain_location,
                    "side_effects": entry.side_effects,
                    
                    "condition_type": entry.condition_type,
                    "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                    "urgency_status": entry.urgency_status
                }
                for entry in entries
            ],
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patient entries: {str(e)}")