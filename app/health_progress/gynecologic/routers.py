from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

# ✅ DEFINE ROUTER FIRST - THIS MUST COME BEFORE ANY @router DECORATORS
router = APIRouter(prefix="/gynecologic", tags=["Gynecologic Progress"])

def get_gynecologic_service(db: Session = Depends(get_db)):
    return services.GynecologicProgressService(db)

# ✅ NOW USE THE ROUTER DECORATOR (AFTER router IS DEFINED)
@router.post("/entries", response_model=schemas.GynecologicEntryResponse)
async def create_gynecologic_entry(
    entry_data: schemas.GynecologicEntryCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    gynecologic_service: services.GynecologicProgressService = Depends(get_gynecologic_service)
):
    try:
        if str(entry_data.patientId) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 Received POST data:", entry_data.dict())
        
        service_data = {
            'patient_id': entry_data.patientId,
            'patient_name': entry_data.patientName,
            'submission_date': entry_data.submissionDate,
            'surgery_type': entry_data.surgeryType,
            'photo_urls': entry_data.photo_urls if hasattr(entry_data, 'photo_urls') else [],
            'common_data': {
                'temperature': entry_data.temperature,
                'bloodPressureSystolic': entry_data.bloodPressureSystolic,
                'bloodPressureDiastolic': entry_data.bloodPressureDiastolic,
                'heartRate': entry_data.heartRate,
                'respiratoryRate': entry_data.respiratoryRate,
                'oxygenSaturation': entry_data.oxygenSaturation,
                'painLevel': entry_data.painLevel,
                'painLocation': entry_data.painLocation
            },
            'condition_data': {
                'bleedingAmount': entry_data.bleedingAmount,
                'dischargeColor': entry_data.dischargeColor,
                'dischargeOdor': entry_data.dischargeOdor,
                'dischargeConsistency': entry_data.dischargeConsistency,
                'clotsPresent': entry_data.clotsPresent,
                'clotSize': entry_data.clotSize,
                'urinaryFrequency': entry_data.urinaryFrequency,
                'urinaryRetention': entry_data.urinaryRetention,
                'hasCatheter': entry_data.hasCatheter,
                'catheterOutput': entry_data.catheterOutput,
                'catheterPatency': entry_data.catheterPatency,
                'dysuria': entry_data.dysuria,
                'nauseaLevel': entry_data.nauseaLevel,
                'vomitingEpisodes': entry_data.vomitingEpisodes,
                'abdominalDistension': entry_data.abdominalDistension,
                'bowelSounds': entry_data.bowelSounds,
                'flatusPassed': entry_data.flatusPassed,
                'bowelMovement': entry_data.bowelMovement,
                'bowelMovementType': entry_data.bowelMovementType,
                'woundCondition': entry_data.woundCondition,
                'woundDischargeType': entry_data.woundDischargeType,
                'woundTenderness': entry_data.woundTenderness,
                'hasDrain': entry_data.hasDrain,
                'drainOutput': entry_data.drainOutput,
                'drainColor': entry_data.drainColor,
                'drainConsistency': entry_data.drainConsistency,
                'mobilityLevel': entry_data.mobilityLevel,
                'ambulationFrequency': entry_data.ambulationFrequency,
                'ambulationDistance': entry_data.ambulationDistance,
                'moodState': entry_data.moodState,
                'anxietyLevel': entry_data.anxietyLevel,
                'sleepQuality': entry_data.sleepQuality,
                'emotionalSupport': entry_data.emotionalSupport,
                'additionalNotes': entry_data.additionalNotes
            }
        }
        
        db_entry = gynecologic_service.create_entry(service_data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=gynecologic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='GYNECOLOGIC_ENTRY',
            patient_id=int(entry_data.patientId),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data.dict()
        )
        
        return schemas.GynecologicEntryResponse(
            id=db_entry.id,
            patientId=db_entry.patient_id,
            patientName=db_entry.patient_name,
            submissionDate=str(db_entry.submission_date),
            surgeryType=db_entry.surgery_type,
            submittedAt=entry_data.submittedAt,
            dayPostOp=entry_data.dayPostOp,
            status=entry_data.status,
            photo_urls=entry_data.photo_urls if hasattr(entry_data, 'photo_urls') else [],
            temperature=entry_data.temperature,
            bloodPressureSystolic=entry_data.bloodPressureSystolic,
            bloodPressureDiastolic=entry_data.bloodPressureDiastolic,
            heartRate=entry_data.heartRate,
            respiratoryRate=entry_data.respiratoryRate,
            oxygenSaturation=entry_data.oxygenSaturation,
            painLevel=entry_data.painLevel,
            painLocation=entry_data.painLocation,
            bleedingAmount=entry_data.bleedingAmount,
            dischargeColor=entry_data.dischargeColor,
            dischargeOdor=entry_data.dischargeOdor,
            dischargeConsistency=entry_data.dischargeConsistency,
            clotsPresent=entry_data.clotsPresent,
            clotSize=entry_data.clotSize,
            urinaryFrequency=entry_data.urinaryFrequency,
            urinaryRetention=entry_data.urinaryRetention,
            hasCatheter=entry_data.hasCatheter,
            catheterOutput=entry_data.catheterOutput,
            catheterPatency=entry_data.catheterPatency,
            dysuria=entry_data.dysuria,
            nauseaLevel=entry_data.nauseaLevel,
            vomitingEpisodes=entry_data.vomitingEpisodes,
            abdominalDistension=entry_data.abdominalDistension,
            bowelSounds=entry_data.bowelSounds,
            flatusPassed=entry_data.flatusPassed,
            bowelMovement=entry_data.bowelMovement,
            bowelMovementType=entry_data.bowelMovementType,
            woundCondition=entry_data.woundCondition,
            woundDischargeType=entry_data.woundDischargeType,
            woundTenderness=entry_data.woundTenderness,
            hasDrain=entry_data.hasDrain,
            drainOutput=entry_data.drainOutput,
            drainColor=entry_data.drainColor,
            drainConsistency=entry_data.drainConsistency,
            mobilityLevel=entry_data.mobilityLevel,
            ambulationFrequency=entry_data.ambulationFrequency,
            ambulationDistance=entry_data.ambulationDistance,
            moodState=entry_data.moodState,
            anxietyLevel=entry_data.anxietyLevel,
            sleepQuality=entry_data.sleepQuality,
            emotionalSupport=entry_data.emotionalSupport,
            additionalNotes=entry_data.additionalNotes,
            createdAt=db_entry.created_at.isoformat() if db_entry.created_at else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create gynecologic progress entry: {str(e)}")


@router.get("/entries")
async def get_all_gynecologic_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    gynecologic_service: services.GynecologicProgressService = Depends(get_gynecologic_service)
):
    try:
        entries = gynecologic_service.get_all_entries()
        #entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=gynecologic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GYNECOLOGIC_ENTRIES',
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
                "surgery_type": entry.surgery_type,
                "submission_date": entry.submission_date,
                "conditionType": "gynecologic",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "gynecologic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving gynecologic entries: {str(e)}")


@router.get("/entries/{patient_id}/{date}")
async def check_gynecologic_entry(
    patient_id: int, 
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    gynecologic_service: services.GynecologicProgressService = Depends(get_gynecologic_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = gynecologic_service.check_existing_entry(patient_id, date)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=gynecologic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GYNECOLOGIC_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking gynecologic entry: {str(e)}")