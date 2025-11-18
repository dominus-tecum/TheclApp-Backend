from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from . import services, schemas

# ✅ ROUTER MUST BE DEFINED FIRST
router = APIRouter(prefix="/bariatric-entries", tags=["Bariatric Progress"])

def get_bariatric_service(db: Session = Depends(get_db)):
    return services.BariatricProgressService(db)

# ✅ ENDPOINT 1: Check specific entry (consistent with burn care pattern)
@router.get("/{patient_id}/{date}")
async def check_bariatric_entry(
    patient_id: str,
    date: date,
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    """
    Check if bariatric entry exists for specific patient and date
    """
    try:
        exists = bariatric_service.check_existing_entry(patient_id, date)
        return {"exists": exists, "patient_id": patient_id, "date": date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking bariatric entry: {str(e)}")

# ✅ ENDPOINT 2: Get all entries for dashboard
@router.get("")
async def get_all_bariatric_entries(
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    """
    Get ALL bariatric entries for dashboard
    """
    try:
        entries = bariatric_service.get_all_entries()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "urgency_status": entry.urgency_status,
                "conditionType": "bariatric",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "condition_type": "bariatric"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bariatric entries: {str(e)}")

# ✅ ENDPOINT 3: Create/update entry (YOUR EXACT LOGIC PRESERVED)
@router.post("", response_model=schemas.BariatricEntryResponse)
async def create_bariatric_entry(
    entry_data: schemas.BariatricEntryCreate,
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    """
    Create NEW bariatric progress entry OR REPLACE existing same-day entry
    """
    try:
        print("📥 BARIATRIC: RAW DATA RECEIVED - ALL FIELDS:")
        raw_data = entry_data.dict()
        for field, value in raw_data.items():
            print(f"   {field}: {value}")
        
        # ✅ REQUIRED FIELD VALIDATION
        patient_id = raw_data.get('patientId') or raw_data.get('patient_id')
        if not patient_id:
            raise HTTPException(status_code=422, detail="patientId is required")
        
        patient_name = raw_data.get('patientName') or raw_data.get('patient_name') or "Unknown Patient"
        
        submission_date = raw_data.get('submissionDate') or raw_data.get('submission_date')
        if not submission_date:
            raise HTTPException(status_code=422, detail="submissionDate is required")
        
        # ✅ CHECK FOR EXISTING ENTRY - Allow replacement for same date
        existing_entry = bariatric_service.check_existing_entry(patient_id, submission_date)
        if existing_entry:
            print(f"🔄 BARIATRIC: Replacing existing entry for {submission_date}")
            # Delete existing entry to replace it (same date replacement)
            bariatric_service.delete_entry(existing_entry.id)
        
        # BUILD COMMON DATA - use whatever exists
        common_data = {}
        common_fields = [
            'bloodPressureSystolic', 'bloodPressureDiastolic', 'energyLevel', 
            'sleepHours', 'sleepQuality', 'medications', 'symptoms', 'notes',
            'weight'
        ]
        
        for field in common_fields:
            if field in raw_data and raw_data[field] is not None:
                common_data[field] = raw_data[field]
        
        # BUILD CONDITION DATA - bariatric specific
        condition_data = {}
        condition_fields = [
            'weightChange', 'foodIntake', 'proteinIntake', 'fluidIntake',
            'exerciseLevel', 'nauseaLevel', 'painLevel', 'activityLevel', 'status'
        ]
        
        for field in condition_fields:
            if field in raw_data and raw_data[field] is not None:
                condition_data[field] = raw_data[field]
        
        # Ensure required nested structures
        if 'medications' not in common_data:
            common_data['medications'] = {}
        if 'symptoms' not in common_data:
            common_data['symptoms'] = {}
        
        db_data = {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "submission_date": submission_date,
            "urgency_status": entry_data.urgencyStatus,
            "common_data": common_data,
            "condition_data": condition_data
        }
        
        print("🔧 BARIATRIC: Final data for DB:", db_data)
        
        db_entry = bariatric_service.create_entry(db_data)
        
        return schemas.BariatricEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BARIATRIC POST Error: {str(e)}")
        import traceback
        print(f"🔍 BARIATRIC Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create bariatric entry: {str(e)}")