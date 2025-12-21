# app/health_progress/cardiac/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas

# ✅ Define router FIRST
router = APIRouter(prefix="/cardiac", tags=["Cardiac Progress"])

def get_cardiac_service(db: Session = Depends(get_db)):
    return services.CardiacProgressService(db)

@router.post("/entries", response_model=schemas.CardiacEntryResponse)
async def create_cardiac_entry(
    entry_data: schemas.CardiacEntryCreate,
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    """
    Create a new cardiac surgery progress entry
    """
    try:
        print("📥 CARDIAC: Received POST data:", entry_data.dict())
        
        # Convert flat structure to nested structure for database
        db_data = {
            "patient_id": entry_data.patientId,
            "patient_name": entry_data.patientName,
            "submission_date": entry_data.submissionDate,
            "common_data": {
                "temperature": entry_data.temperature,
                "bloodPressureSystolic": entry_data.bloodPressureSystolic,
                "bloodPressureDiastolic": entry_data.bloodPressureDiastolic,
                "heartRate": entry_data.heartRate,
                "respiratoryRate": entry_data.respiratoryRate,
                "oxygenSaturation": entry_data.oxygenSaturation,
                "painLevel": entry_data.painLevel
            },
            "condition_data": {
                "cardiacRhythm": entry_data.cardiacRhythm,
                "rhythmStable": entry_data.rhythmStable,
                "breathingEffort": entry_data.breathingEffort,
                "oxygenTherapy": entry_data.oxygenTherapy,
                "oxygenFlow": entry_data.oxygenFlow,
                "incentiveSpirometer": entry_data.incentiveSpirometer,
                "coughEffectiveness": entry_data.coughEffectiveness,
                "hasChestTube": entry_data.hasChestTube,
                "chestTubeOutput": entry_data.chestTubeOutput,
                "chestDrainColor": entry_data.chestDrainColor,
                "chestDrainConsistency": entry_data.chestDrainConsistency,
                "urineOutput": entry_data.urineOutput,
                "fluidBalance": entry_data.fluidBalance,
                "sternalWoundCondition": entry_data.sternalWoundCondition,
                "graftWoundCondition": entry_data.graftWoundCondition,
                "woundDischargeType": entry_data.woundDischargeType,
                "woundTenderness": entry_data.woundTenderness,
                "consciousnessLevel": entry_data.consciousnessLevel,
                "orientation": entry_data.orientation,
                "limbMovement": entry_data.limbMovement,
                "mobilityLevel": entry_data.mobilityLevel,
                "ambulationDistance": entry_data.ambulationDistance,
                "painLocation": entry_data.painLocation,
                "moodState": entry_data.moodState,
                "sleepQuality": entry_data.sleepQuality,
                "additionalNotes": entry_data.additionalNotes,
                "status": entry_data.status
            }
        }
        
        db_entry = cardiac_service.create_entry(db_data)
        
        return schemas.CardiacEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=str(db_entry.submission_date),  # ✅ Convert to string
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at.isoformat()
        )
        
    except Exception as e:
        print("❌ CARDIAC POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create cardiac progress entry: {str(e)}")

@router.get("/entries")
async def get_all_cardiac_entries(
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    """
    Get ALL cardiac surgery entries
    """
    try:
        entries = cardiac_service.get_all_entries()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "conditionType": "cardiac",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "cardiac"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cardiac entries: {str(e)}")

@router.get("/entries/{patient_id}/{date}")
async def check_cardiac_entry(
    patient_id: int,
    date: str,
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    """
    Check if cardiac entry exists for specific patient and date
    """
    try:
        exists = cardiac_service.check_existing_entry(patient_id, date)
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking cardiac entry: {str(e)}")

@router.get("/entries/patient/{patient_id}")
async def get_patient_cardiac_entries(
    patient_id: int,
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    """
    Get all cardiac entries for a specific patient
    """
    try:
        entries = cardiac_service.get_patient_entries(patient_id)
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
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
        raise HTTPException(status_code=500, detail=f"Error retrieving patient cardiac entries: {str(e)}")















        from sqlalchemy import text

@router.post("/fix-missing-table")
async def fix_missing_cardiac_table(
    db: Session = Depends(get_db)
):
    """
    TEMPORARY: Create missing cardiac_surgery_entries table
    Call once: curl -X POST https://theclapp-backend.onrender.com/api/health-progress/cardiac/fix-missing-table
    Then delete this endpoint
    """
    try:
        # SQLite CREATE TABLE for cardiac
        sql = text("""
            CREATE TABLE IF NOT EXISTS cardiac_surgery_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                surgery_type TEXT DEFAULT 'cardiac',
                submission_date TEXT NOT NULL,
                common_data TEXT,
                condition_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(patient_id, submission_date)
            )
        """)
        
        db.execute(sql)
        db.commit()
        
        return {
            "success": True,
            "message": "SQLite table 'cardiac_surgery_entries' created",
            "note": "Delete this endpoint after use"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "already exists" in error_msg:
            return {"success": True, "message": "Table already exists"}
        return {"success": False, "error": error_msg}