from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas

router = APIRouter(prefix="/urological", tags=["Urological Progress"])

def get_urological_service(db: Session = Depends(get_db)):
    return services.UrologicalProgressService(db)

@router.post("/entries", response_model=schemas.UrologicalEntryResponse)
async def create_urological_entry(
    entry_data: schemas.UrologicalEntryCreate,
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    """
    Create a new urological surgery progress entry
    """
    try:
        print("📥 UROLOGICAL: Received POST data:", entry_data.dict())
        
        service_data = {
            'patient_id': entry_data.patient_id,
            'patient_name': entry_data.patient_name,
            'submission_date': entry_data.submission_date,
            'surgery_type': entry_data.surgery_type,
            'common_data': entry_data.common_data.dict(),
            'condition_data': entry_data.condition_data.dict()
        }
        
        db_entry = urological_service.create_entry(service_data)
        
        return schemas.UrologicalEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            surgery_type=db_entry.surgery_type,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at
        )
        
    except Exception as e:
        print("❌ UROLOGICAL POST Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create urological progress entry: {str(e)}")

@router.get("/entries")
async def get_all_urological_entries(
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    """
    Get ALL urological surgery entries
    """
    try:
        print("🔍 UROLOGICAL: Fetching all entries")
        entries = urological_service.get_all_entries()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "surgery_type": entry.surgery_type,
                "submission_date": entry.submission_date,
                "conditionType": "urological",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        print(f"✅ UROLOGICAL: Retrieved {len(entries)} entries")
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "urological"
        }
        
    except Exception as e:
        print(f"❌ UROLOGICAL: Error retrieving all entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving urological entries: {str(e)}")

@router.get("/entries/{patient_id}/{date}")
async def check_urological_entry(
    patient_id: int, 
    date: str,
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    """
    Check if urological entry exists for patient on specific date
    """
    try:
        print(f"🔍 UROLOGICAL: Checking entry for patient {patient_id} on {date}")
        exists = urological_service.check_existing_entry(patient_id, date)
        return {"exists": exists}
        
    except Exception as e:
        print(f"❌ UROLOGICAL: Error checking entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking urological entry: {str(e)}")