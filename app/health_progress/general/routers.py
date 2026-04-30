from sqlalchemy.orm import Session
from app.database import get_db
from .models import GeneralHealthEntry
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter()

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_general_service(db: Session = Depends(get_db)):
    return services.GeneralProgressService(db)

@router.post("/entries", response_model=schemas.GeneralEntryResponse)
async def create_general_entry(
    data: dict,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    service: services.GeneralProgressService = Depends(get_general_service)
):
    try:
        patient_id = data.get('patient_id') or data.get('patientId')
        if patient_id and str(patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("🎯 GENERAL ROUTER: Creating entry with flattened data structure")
        print("🔍 RECEIVED RAW DATA:", data)
        
        db_entry = service.create_entry(data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='GENERAL_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=data
        )
        
        return schemas.GeneralEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            status=db_entry.status,
            health_trend=db_entry.health_trend,
            overall_wellbeing=db_entry.overall_wellbeing,
            primary_symptom_severity=db_entry.primary_symptom_severity,
            primary_symptom_description=db_entry.primary_symptom_description,
            notes=db_entry.notes,
            condition_type=db_entry.condition_type,
            submitted_at=db_entry.submitted_at.isoformat() if db_entry.submitted_at else None,
            urgency_status=db_entry.urgency_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ GENERAL ROUTER: Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

@router.get("/entries")
async def get_all_general_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    try:
        entries = db.query(GeneralHealthEntry).all()
        #entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GENERAL_ENTRIES',
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
                    "health_trend": entry.health_trend,
                    "overall_wellbeing": entry.overall_wellbeing,
                    "primary_symptom_severity": entry.primary_symptom_severity,
                    "primary_symptom_description": entry.primary_symptom_description,
                    "notes": entry.notes,
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
async def get_general_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entry = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id,
            GeneralHealthEntry.submission_date == date
        ).first()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GENERAL_ENTRY',
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
                "health_trend": entry.health_trend,
                "overall_wellbeing": entry.overall_wellbeing,
                "primary_symptom_severity": entry.primary_symptom_severity,
                "primary_symptom_description": entry.primary_symptom_description,
                "notes": entry.notes,
                "condition_type": entry.condition_type,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "urgency_status": entry.urgency_status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

@router.get("/check/{patient_id}/{date}")
async def check_general_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id,
            GeneralHealthEntry.submission_date == date
        ).first() is not None
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GENERAL_ENTRY_CHECK',
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
async def get_patient_general_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = db.query(GeneralHealthEntry).filter(
            GeneralHealthEntry.patient_id == patient_id
        ).all()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='GENERAL_ENTRIES',
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
                    "health_trend": entry.health_trend,
                    "overall_wellbeing": entry.overall_wellbeing,
                    "primary_symptom_severity": entry.primary_symptom_severity,
                    "primary_symptom_description": entry.primary_symptom_description,
                    "notes": entry.notes,
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