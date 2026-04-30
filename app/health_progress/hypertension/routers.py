# app/health_progress/hypertension/routers.py
from sqlalchemy.orm import Session
from app.database import get_db
from app.health_progress.hypertension.models import HypertensionEntry
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

# POST /api/health-progress/hypertension/entries
@router.post("/entries")
async def create_hypertension_entry(
    data: dict,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    try:
        patient_id = data.get('patient_id')
        if patient_id and str(patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 Creating/updating hypertension entry:", data)
        
        existing_entry = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == data.get('patient_id'),
            HypertensionEntry.submission_date == data.get('submission_date')
        ).first()
        
        if existing_entry:
            print(f"🔄 Updating existing entry ID: {existing_entry.id}")
            existing_entry.blood_pressure_systolic = data.get('blood_pressure_systolic')
            existing_entry.blood_pressure_diastolic = data.get('blood_pressure_diastolic')
            existing_entry.energy_level = data.get('energy_level')
            existing_entry.sleep_hours = data.get('sleep_hours')
            existing_entry.sleep_quality = data.get('sleep_quality')
            existing_entry.medications = data.get('medications')
            existing_entry.symptoms = data.get('symptoms')
            existing_entry.notes = data.get('notes')
            existing_entry.status = data.get('status')
            existing_entry.condition_type = data.get('condition_type', 'hypertension')
            
            db.commit()
            db.refresh(existing_entry)
            
            # ✅ ADD AUDIT LOG FOR UPDATE
            log_audit(
                db=db,
                user_id=current_user.id,
                username=current_user.username,
                user_role=current_user.role.value,
                action='UPDATE',
                resource_type='HYPERTENSION_ENTRY',
                patient_id=int(patient_id),
                status='success',
                purpose='TREATMENT',
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                new_value=data
            )
            
            return {
                "message": "Hypertension entry updated successfully",
                "id": existing_entry.id,
                "patient_id": existing_entry.patient_id
            }
        else:
            db_entry = HypertensionEntry(
                patient_id=data.get('patient_id'),
                patient_name=data.get('patient_name'),
                submission_date=data.get('submission_date'),
                blood_pressure_systolic=data.get('blood_pressure_systolic'),
                blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
                energy_level=data.get('energy_level'),
                sleep_hours=data.get('sleep_hours'),
                sleep_quality=data.get('sleep_quality'),
                medications=data.get('medications'),
                symptoms=data.get('symptoms'),
                notes=data.get('notes'),
                status=data.get('status'),
                condition_type=data.get('condition_type', 'hypertension')
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            
            # ✅ ADD AUDIT LOG FOR CREATE
            log_audit(
                db=db,
                user_id=current_user.id,
                username=current_user.username,
                user_role=current_user.role.value,
                action='CREATE',
                resource_type='HYPERTENSION_ENTRY',
                patient_id=int(patient_id),
                status='success',
                purpose='TREATMENT',
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                new_value=data
            )
            
            return {
                "message": "Hypertension entry created successfully",
                "id": db_entry.id,
                "patient_id": db_entry.patient_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create/update entry: {str(e)}")


# GET /api/health-progress/hypertension/entries
@router.get("/entries")
async def get_all_hypertension_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    try:
        entries = db.query(HypertensionEntry).all()
        entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='HYPERTENSION_ENTRIES',
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
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "status": entry.status,
                    "condition_type": entry.condition_type,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None
                }
                for entry in entries
            ],
            "total": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")


# GET /api/health-progress/hypertension/entries/{patient_id}/{date}

@router.get("/entries/{patient_id}/{date}")
async def get_hypertension_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entry = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id,
            HypertensionEntry.submission_date == date
        ).first()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='HYPERTENSION_ENTRY',
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
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "energy_level": entry.energy_level,
                "sleep_hours": entry.sleep_hours,
                "sleep_quality": entry.sleep_quality,
                "medications": entry.medications,
                "symptoms": entry.symptoms,
                "notes": entry.notes,
                "status": entry.status,
                "condition_type": entry.condition_type,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

# GET /api/health-progress/hypertension/check/{patient_id}/{date}

@router.get("/check/{patient_id}/{date}")
async def check_hypertension_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id,
            HypertensionEntry.submission_date == date
        ).first() is not None
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='HYPERTENSION_ENTRY_CHECK',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check entry: {str(e)}")


# GET /api/health-progress/hypertension/patient/{patient_id}
@router.get("/patient/{patient_id}")
async def get_patient_hypertension_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = db.query(HypertensionEntry).filter(
            HypertensionEntry.patient_id == patient_id
        ).all()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='HYPERTENSION_ENTRIES',
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
                    "blood_pressure_systolic": entry.blood_pressure_systolic,
                    "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                    "energy_level": entry.energy_level,
                    "sleep_hours": entry.sleep_hours,
                    "sleep_quality": entry.sleep_quality,
                    "medications": entry.medications,
                    "symptoms": entry.symptoms,
                    "notes": entry.notes,
                    "status": entry.status,
                    "condition_type": entry.condition_type,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None
                }
                for entry in entries
            ],
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patient entries: {str(e)}")