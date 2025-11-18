# app/health_progress/orthopedic/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas  # ✅ Import schemas

router = APIRouter(prefix="/orthopedic", tags=["Orthopedic Progress"])

def get_orthopedic_service(db: Session = Depends(get_db)):
    return services.OrthopedicProgressService(db)

@router.post("/entries", response_model=schemas.OrthopedicEntryResponse)
async def create_orthopedic_entry(
    entry_data: schemas.OrthopedicEntryCreate,  # ✅ Use schema instead of dict
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    """
    Create a new orthopedic surgery progress entry
    """
    try:
        print("📥 ORTHOPEDIC Received POST data:", entry_data.dict())
        db_entry = orthopedic_service.create_entry(entry_data.dict())
        
        # ✅ Return using schema
        return schemas.OrthopedicEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at.isoformat()
        )
        
    except Exception as e:
        print("❌ ORTHOPEDIC POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create orthopedic progress entry: {str(e)}")

@router.get("/entries")
async def get_all_orthopedic_entries(
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    """
    Get ALL orthopedic surgery entries
    """
    try:
        entries = orthopedic_service.get_all_entries()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "conditionType": "orthopedic",  # For frontend
                "common_data": entry.common_data,      # ✅ Direct from JSON column
                "condition_data": entry.condition_data, # ✅ Direct from JSON column
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "orthopedic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orthopedic entries: {str(e)}")

@router.get("/entries/{patient_id}/{date}")
async def check_orthopedic_entry(
    patient_id: int,
    date: str,
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    """
    Check if an orthopedic entry exists for a patient on a specific date
    """
    try:
        exists = orthopedic_service.check_existing_entry(patient_id, date)
        return {"exists": exists}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking orthopedic entry: {str(e)}")

@router.get("/entries/patient/{patient_id}")
async def get_patient_orthopedic_entries(
    patient_id: int,
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    """
    Get all orthopedic entries for a specific patient
    """
    try:
        entries = orthopedic_service.get_patient_entries(patient_id)
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "conditionType": "orthopedic",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient orthopedic entries: {str(e)}")