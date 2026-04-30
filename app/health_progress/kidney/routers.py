# app/health_progress/kidney/routers.py
from sqlalchemy.orm import Session
from app.database import get_db
from .models import KidneyEntry
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_kidney_service(db: Session = Depends(get_db)):
    return services.KidneyProgressService(db)

@router.post("/entries", response_model=schemas.KidneyEntryResponse)
async def create_kidney_entry(
    data: dict,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    service: services.KidneyProgressService = Depends(get_kidney_service)
):
    try:
        patient_id = data.get('patient_id') or data.get('patientId')
        if patient_id and str(patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("🎯 KIDNEY ROUTER: Creating entry with flattened data structure")
        print("🔍 RECEIVED RAW DATA:", data)
        
        db_entry = service.create_entry(data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='KIDNEY_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=data
        )
        
        return schemas.KidneyEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            status=db_entry.status,
            blood_pressure_systolic=db_entry.blood_pressure_systolic,
            blood_pressure_diastolic=db_entry.blood_pressure_diastolic,
            energy_level=db_entry.energy_level,
            sleep_hours=db_entry.sleep_hours,
            sleep_quality=db_entry.sleep_quality,
            medications=db_entry.medications,
            symptoms=db_entry.symptoms,
            notes=db_entry.notes,
            weight=db_entry.weight,
            swelling_level=db_entry.swelling_level,
            urine_output=db_entry.urine_output,
            fluid_intake=db_entry.fluid_intake,
            breathing_difficulty=db_entry.breathing_difficulty,
            fatigue_level=db_entry.fatigue_level,
            nausea_level=db_entry.nausea_level,
            itching_level=db_entry.itching_level,
            condition_type=db_entry.condition_type,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ KIDNEY ROUTER: Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

@router.get("/entries")
async def get_all_kidney_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    try:
        entries = db.query(KidneyEntry).all()
        entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='KIDNEY_ENTRIES',
            patient_id=int(current_user.id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "weight": entry.weight,
                    "swelling_level": entry.swelling_level,
                    "urine_output": entry.urine_output,
                    "fluid_intake": entry.fluid_intake,
                    "breathing_difficulty": entry.breathing_difficulty,
                    "fatigue_level": entry.fatigue_level,
                    "nausea_level": entry.nausea_level,
                    "itching_level": entry.itching_level,
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
async def get_kidney_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entry = db.query(KidneyEntry).filter(
            KidneyEntry.patient_id == patient_id,
            KidneyEntry.submission_date == date
        ).first()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='KIDNEY_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
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
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "energy_level": entry.energy_level,
                "sleep_hours": entry.sleep_hours,
                "sleep_quality": entry.sleep_quality,
                "medications": entry.medications,
                "symptoms": entry.symptoms,
                "notes": entry.notes,
                "weight": entry.weight,
                "swelling_level": entry.swelling_level,
                "urine_output": entry.urine_output,
                "fluid_intake": entry.fluid_intake,
                "breathing_difficulty": entry.breathing_difficulty,
                "fatigue_level": entry.fatigue_level,
                "nausea_level": entry.nausea_level,
                "itching_level": entry.itching_level,
                "condition_type": entry.condition_type,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "urgency_status": entry.urgency_status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")


@router.get("/check/{patient_id}/{date}")
async def check_kidney_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = db.query(KidneyEntry).filter(
            KidneyEntry.patient_id == patient_id,
            KidneyEntry.submission_date == date
        ).first() is not None
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='KIDNEY_ENTRY_CHECK',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")


@router.get("/patient/{patient_id}")
async def get_patient_kidney_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = db.query(KidneyEntry).filter(
            KidneyEntry.patient_id == patient_id
        ).all()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='KIDNEY_ENTRIES',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "patient_id": entry.patient_id,
                    "patient_name": entry.patient_name,
                    "submission_date": entry.submission_date,
                    "status": entry.status,
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "weight": entry.weight,
                    "swelling_level": entry.swelling_level,
                    "urine_output": entry.urine_output,
                    "fluid_intake": entry.fluid_intake,
                    "breathing_difficulty": entry.breathing_difficulty,
                    "fatigue_level": entry.fatigue_level,
                    "nausea_level": entry.nausea_level,
                    "itching_level": entry.itching_level,
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