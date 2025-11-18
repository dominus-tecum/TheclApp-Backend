from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from .models import GeneralHealthEntry
from . import services, schemas

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_general_service(db: Session = Depends(get_db)):
    return services.GeneralProgressService(db)

@router.post("/entries", response_model=schemas.GeneralEntryResponse)
async def create_general_entry(
    data: dict,
    service: services.GeneralProgressService = Depends(get_general_service)
):
    """Create a new general health entry with flattened structure"""
    try:
        print("🎯 GENERAL ROUTER: Creating entry with flattened data structure")
        print("🔍 RECEIVED RAW DATA:", data)
        
        # ✅ Use service to handle the data mapping and creation
        db_entry = service.create_entry(data)
        
        # ✅ Return the response with proper FLATTENED structure
        return schemas.GeneralEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            status=db_entry.status,
            
            # General health specific fields (flattened)
            health_trend=db_entry.health_trend,
            overall_wellbeing=db_entry.overall_wellbeing,
            primary_symptom_severity=db_entry.primary_symptom_severity,
            primary_symptom_description=db_entry.primary_symptom_description,
            notes=db_entry.notes,
            
            condition_type=db_entry.condition_type,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status
        )
        
    except Exception as e:
        print(f"❌ GENERAL ROUTER: Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

@router.get("/entries")
async def get_all_general_entries(db: Session = Depends(get_db_session)):
    """Get all general health entries"""
    try:
        entries = db.query(GeneralHealthEntry).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    
                    # General health specific fields (flattened)
                    "health_trend": entry.health_trend,
                    "overall_wellbeing": entry.overall_wellbeing,
                    "primary_symptom_severity": entry.primary_symptom_severity,
                    "primary_symptom_description": entry.primary_symptom_description,
                    "notes": entry.notes,
                    
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
async def get_general_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Get specific general health entry for patient and date"""
    try:
        entry = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id,
            GeneralHealthEntry.submission_date == date
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
                
                # General health specific fields (flattened)
                "health_trend": entry.health_trend,
                "overall_wellbeing": entry.overall_wellbeing,
                "primary_symptom_severity": entry.primary_symptom_severity,
                "primary_symptom_description": entry.primary_symptom_description,
                "notes": entry.notes,
                
                "condition_type": entry.condition_type,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "urgency_status": entry.urgency_status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

@router.get("/check/{patient_id}/{date}")
async def check_general_entry(patient_id: int, date: str, db: Session = Depends(get_db_session)):
    """Check if general health entry exists"""
    try:
        exists = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id,
            GeneralHealthEntry.submission_date == date
        ).first() is not None
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")

@router.get("/patient/{patient_id}")
async def get_patient_general_entries(patient_id: int, db: Session = Depends(get_db_session)):
    """Get all general health entries for a patient"""
    try:
        entries = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id
        ).all()
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    
                    # General health specific fields (flattened)
                    "health_trend": entry.health_trend,
                    "overall_wellbeing": entry.overall_wellbeing,
                    "primary_symptom_severity": entry.primary_symptom_severity,
                    "primary_symptom_description": entry.primary_symptom_description,
                    "notes": entry.notes,
                    
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