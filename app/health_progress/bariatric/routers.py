from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request  # ← Add Request
from app.utils.audit import log_audit  # ← Add this

# ✅ ROUTER MUST BE DEFINED FIRST
router = APIRouter(prefix="/bariatric-entries", tags=["Bariatric Progress"])

def get_bariatric_service(db: Session = Depends(get_db)):
    return services.BariatricProgressService(db)

# ✅ ENDPOINT 1: Check specific entry
@router.get("/{patient_id}/{date}")
async def check_bariatric_entry(
    patient_id: str,
    date: date,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = bariatric_service.check_existing_entry(patient_id, date)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=bariatric_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='BARIATRIC_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking bariatric entry: {str(e)}")

# ✅ ENDPOINT 2: Get all entries for dashboard

@router.get("")
async def get_all_bariatric_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    try:
        entries = bariatric_service.get_all_entries()
        #entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=bariatric_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='BARIATRIC_ENTRIES',
            patient_id=int(current_user.id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
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
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "condition_type": "bariatric"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bariatric entries: {str(e)}")

        
# ✅ ENDPOINT 3: Create entry

@router.post("", response_model=schemas.BariatricEntryResponse)
async def create_bariatric_entry(
    entry_data: schemas.BariatricEntryCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    bariatric_service: services.BariatricProgressService = Depends(get_bariatric_service)
):
    """
    Create NEW bariatric progress entry OR REPLACE existing same-day entry
    """
    try:
        print("📥 BARIATRIC: RAW DATA RECEIVED - ALL FIELDS:")
        raw_data = entry_data.dict()
        print("📋 ALL RAW DATA KEYS:", list(raw_data.keys()))
        for field, value in raw_data.items():
            print(f"   {field}: {value}")
        
        # ✅ REQUIRED FIELD VALIDATION
        patient_id = raw_data.get('patientId') or raw_data.get('patient_id')
        if not patient_id:
            raise HTTPException(status_code=422, detail="patientId is required")
        
        # ← ADD THIS VERIFICATION
        if patient_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
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
        
        # BUILD COMMON DATA - ALL fields from frontend
        common_data = {}
        common_fields = [
            'temperature', 'bloodPressureSystolic', 'bloodPressureDiastolic',
            'heartRate', 'respiratoryRate', 'oxygenSaturation', 'painLevel',
            'painLocation', 'fluidIntake', 'fluidTypes', 'urineOutput', 'urineColor',
            'waterGoalMet', 'nauseaLevel', 'vomitingEpisodes', 'abdominalPain',
            'abdominalDistension', 'bloating', 'woundCondition', 'woundDischargeType',
            'woundTenderness', 'hasDrain', 'drainOutput', 'drainColor', 'breathingEffort',
            'oxygenTherapy', 'oxygenFlow', 'mobilityLevel', 'ambulationFrequency',
            'physiotherapySessions', 'dietStage', 'proteinIntake', 'moodState',
            'motivationLevel', 'cravings', 'additionalNotes'
        ]

        for field in common_fields:
            if field in raw_data and raw_data[field] is not None:
                common_data[field] = raw_data[field]

        # BUILD CONDITION DATA
        condition_data = {}
        condition_fields = [
            'status', 'painLevel', 'nauseaLevel', 'vomitingEpisodes',
            'abdominalPain', 'abdominalDistension', 'bloating', 'woundCondition',
            'woundDischargeType', 'woundTenderness', 'hasDrain', 'drainOutput',
            'drainColor', 'breathingEffort', 'oxygenTherapy', 'oxygenFlow',
            'mobilityLevel', 'ambulationFrequency', 'physiotherapySessions',
            'dietStage', 'proteinIntake', 'waterGoalMet', 'moodState',
            'motivationLevel', 'cravings', 'weightChange', 'foodIntake', 'fluidIntake',
            'exerciseLevel', 'activityLevel'
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
            "condition_data": condition_data,
            "photo_urls": raw_data.get('photo_urls', [])
        }
        
        print("🔧 BARIATRIC: Final data for DB:", db_data)
        
        db_entry = bariatric_service.create_entry(db_data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=bariatric_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='BARIATRIC_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=db_data
        )
        
        return schemas.BariatricEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            photo_urls=db_entry.photo_urls if hasattr(db_entry, 'photo_urls') else [],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BARIATRIC POST Error: {str(e)}")
        import traceback
        print(f"🔍 BARIATRIC Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create bariatric entry: {str(e)}")