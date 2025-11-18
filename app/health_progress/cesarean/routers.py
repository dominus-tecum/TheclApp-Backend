from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas  # ✅ Import schemas

router = APIRouter(prefix="/cesarean", tags=["Cesarean Progress"])

def get_cesarean_service(db: Session = Depends(get_db)):
    return services.CesareanProgressService(db)

@router.post("/entries", response_model=schemas.CesareanEntryResponse)
async def create_cesarean_entry(
    entry_data: schemas.CesareanEntryCreate,  # ✅ Use schema instead of dict
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    """
    Create a new cesarean section progress entry
    """
    try:
        print("📥 Received POST data:", entry_data.dict())
        db_entry = cesarean_service.create_entry(entry_data.dict())
        
        # ✅ Return using schema
        return schemas.CesareanEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at.isoformat()
        )
        
    except Exception as e:
        print("❌ POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create cesarean progress entry: {str(e)}")

@router.get("/entries")
async def get_all_cesarean_entries(
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    """
    Get ALL cesarean section entries
    """
    try:
        entries = cesarean_service.get_all_entries()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "conditionType": "cesarean",  # For frontend
                "common_data": entry.common_data,      # ✅ Direct from JSON column
                "condition_data": entry.condition_data, # ✅ Direct from JSON column
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "cesarean"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cesarean entries: {str(e)}")