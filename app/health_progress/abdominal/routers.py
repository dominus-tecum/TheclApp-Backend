from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from . import schemas, services
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_abdominal_service(db: Session = Depends(get_db)) -> services.AbdominalProgressService:
    return services.AbdominalProgressService(db)

@router.post("/abdominal-entries", response_model=schemas.AbdominalEntryResponse)
async def create_abdominal_entry(
    entry_data: dict,  # ✅ CHANGED: Accept raw JSON instead of Pydantic schema
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    """
    Create a new abdominal surgery progress entry from mobile app JSON data
    """
    try:
        logger.info(f"📝 Creating abdominal progress entry for patient {entry_data.get('patient_id')}")
        
        # Check for existing entry
        if abdominal_service.check_existing_entry(entry_data.get('patient_id'), entry_data.get('submission_date')):
            raise HTTPException(
                status_code=400, 
                detail=f"Abdominal progress entry already exists for patient {entry_data.get('patient_id')} on {entry_data.get('submission_date')}"
            )
        
        # Create entry with raw JSON data
        db_entry = abdominal_service.create_entry(entry_data)
        
        # Prepare response
        response_data = schemas.AbdominalEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at.isoformat()
        )
        
        logger.info(f"✅ Abdominal progress entry created successfully for patient {entry_data.get('patient_id')}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating abdominal progress entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create abdominal progress entry: {str(e)}")

@router.get("/abdominal-entries/patient/{patient_id}")
async def get_patient_abdominal_entries(
    patient_id: int,
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    """
    Get all abdominal progress entries for a specific patient
    """
    try:
        entries = abdominal_service.get_patient_entries(patient_id)
        return {
            "patient_id": patient_id,
            "entries": entries,
            "count": len(entries)
        }
    except Exception as e:
        logger.error(f"❌ Error fetching abdominal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch abdominal progress entries")

@router.get("/abdominal-entries/check/{patient_id}/{date}")
async def check_abdominal_entry_exists(
    patient_id: int,
    date: str,
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    """
    Check if an abdominal entry exists for a patient on a specific date
    """
    try:
        exists = abdominal_service.check_existing_entry(patient_id, date)
        return {"exists": exists}
    except Exception as e:
        logger.error(f"❌ Error checking abdominal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check abdominal entry")

@router.get("/abdominal-entries")
async def get_all_abdominal_entries(
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    """
    Get all abdominal progress entries for the dashboard
    """
    try:
        entries = abdominal_service.get_all_entries()
        
        # Format the response for the dashboard
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "count": len(formatted_entries)
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching all abdominal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch abdominal entries")


@router.get("/abdominal/entries")
async def get_all_abdominal_entries():
    """Get all abdominal surgery entries"""
    query = "SELECT * FROM abdominal_surgery_entries ORDER BY submission_date DESC, created_at DESC"
    entries = await database.fetch_all(query)
    return {"entries": entries}







# Add this endpoint AFTER your existing routes
@router.post("/fix-missing-table")
async def fix_missing_table(
    db: Session = Depends(get_db)  # Use your existing get_db dependency
):
    """
    TEMPORARY: Create missing abdominal_entries table
    Call once: curl -X POST https://theclapp-backend.onrender.com/api/progress/abdominal-entries/fix-missing-table
    Then delete this endpoint
    """
    try:
        # SQLite CREATE TABLE
        sql = text("""
            CREATE TABLE IF NOT EXISTS abdominal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                submission_date TEXT NOT NULL,
                common_data TEXT,
                condition_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(patient_id, submission_date)
            )
        """)
        
        db.execute(sql)
        db.commit()
        
        return {
            "success": True,
            "message": "SQLite table 'abdominal_entries' created",
            "note": "Delete this endpoint after use"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "already exists" in error_msg:
            return {"success": True, "message": "Table already exists"}
        return {"success": False, "error": error_msg}













