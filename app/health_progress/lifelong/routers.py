from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter(prefix="/lifelong", tags=["Lifelong"])

def get_service(db: Session = Depends(get_db)):
    return services.LifelongService(db)

@router.post("/entries", response_model=schemas.LifelongEntryResponse)
async def create_entry(
    entry: schemas.LifelongEntryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: services.LifelongService = Depends(get_service)
):
    try:
        entry_dict = entry.dict()
        patient_id = entry_dict.get('patient_id')
        if patient_id and str(patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # ✅ Use the existing method that handles both create and update
        db_entry = service.create_or_update_entry(entry_dict)
        
        # Check if it was an update or create
        existing = service.get_entry_by_date(patient_id, entry_dict.get('submission_date'))
        action = 'UPDATE' if existing and existing.id == db_entry.id else 'CREATE'
        
        log_audit(
            db=service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action=action,
            resource_type='LIFELONG_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_dict
        )
        
        return schemas.LifelongEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            conditions_data=db_entry.conditions_data,
            status=db_entry.status,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def get_all_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    service: services.LifelongService = Depends(get_service)
):
    entries = service.get_all_entries()
    #entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=service.db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='LIFELONG_ENTRIES',
        patient_id=int(current_user.id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "entries": [
            {
                "id": e.id,
                "patient_id": e.patient_id,
                "patient_name": e.patient_name,
                "submission_date": e.submission_date,
                "common_data": e.common_data,
                "conditions_data": e.conditions_data,
                "status": e.status,
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat()
            }
            for e in entries
        ],
        "total": len(entries)
    }

@router.get("/entries/{patient_id}/{date}")
async def get_entry_by_date(
    patient_id: int, 
    date: str, 
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    service: services.LifelongService = Depends(get_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    entry = service.get_entry_by_date(patient_id, date)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=service.db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='LIFELONG_ENTRY',
        patient_id=patient_id,
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    if not entry:
        return {"exists": False}
    return {
        "exists": True,
        "data": {
            "id": entry.id,
            "patient_id": entry.patient_id,
            "patient_name": entry.patient_name,
            "submission_date": entry.submission_date,
            "common_data": entry.common_data,
            "conditions_data": entry.conditions_data,
            "status": entry.status
        }
    }

@router.get("/check/{patient_id}/{date}")
async def check_entry(
    patient_id: int, 
    date: str, 
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    service: services.LifelongService = Depends(get_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    exists = service.check_existing_entry(patient_id, date)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=service.db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='LIFELONG_ENTRY_CHECK',
        patient_id=patient_id,
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {"exists": exists, "patient_id": patient_id, "date": date}