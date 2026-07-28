# app/health_progress/cardiac/routers.py
from sqlalchemy.orm import Session
from sqlalchemy import text 
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User, UserRole  # ← ADD UserRole
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

# ✅ Define router FIRST
router = APIRouter(prefix="/cardiac", tags=["Cardiac Progress"])

def get_cardiac_service(db: Session = Depends(get_db)):
    return services.CardiacProgressService(db)

@router.post("/entries", response_model=schemas.CardiacEntryResponse)
async def create_cardiac_entry(
    entry_data: schemas.CardiacEntryCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    try:
        if str(entry_data.patientId) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 CARDIAC: Received POST data:", entry_data.dict())
        
        db_data = {
            "patient_id": entry_data.patientId,
            "patient_name": entry_data.patientName,
            "submission_date": entry_data.submissionDate,
            "photo_urls": entry_data.photo_urls if hasattr(entry_data, 'photo_urls') else [],
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
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=cardiac_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='CARDIAC_ENTRY',
            patient_id=int(entry_data.patientId),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data.dict()
        )
        
        return schemas.CardiacEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=str(db_entry.submission_date),
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            created_at=db_entry.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ CARDIAC POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create cardiac progress entry: {str(e)}")

@router.get("/entries")
async def get_all_cardiac_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    try:
        entries = cardiac_service.get_all_entries()
        # ========== ROLE-BASED ACCESS CONTROL ==========
        if current_user.role == UserRole.DOCTOR:
            from app.models import PatientDoctorAssignment
            assignments = cardiac_service.db.query(PatientDoctorAssignment.patient_id).filter(
                PatientDoctorAssignment.doctor_id == current_user.id,
                PatientDoctorAssignment.end_date == None
            ).all()
            patient_ids = [a[0] for a in assignments]
            
            if not patient_ids:
                entries = []
            else:
                entries = [e for e in entries if int(e.patient_id) in patient_ids]
                
        elif current_user.role == UserRole.PATIENT:
            entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        # ========================================================

        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=cardiac_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CARDIAC_ENTRIES',
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
                "conditionType": "cardiac",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
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
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = cardiac_service.check_existing_entry(patient_id, date)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=cardiac_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CARDIAC_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking cardiac entry: {str(e)}")

@router.get("/entries/patient/{patient_id}")
async def get_patient_cardiac_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    cardiac_service: services.CardiacProgressService = Depends(get_cardiac_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = cardiac_service.get_patient_entries(patient_id)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=cardiac_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CARDIAC_ENTRIES',
            patient_id=patient_id,
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