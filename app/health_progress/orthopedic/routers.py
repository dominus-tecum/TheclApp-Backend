# app/health_progress/orthopedic/routers.py
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User  # ← ADD THIS
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter(prefix="/orthopedic", tags=["Orthopedic Progress"])

def get_orthopedic_service(db: Session = Depends(get_db)):
    return services.OrthopedicProgressService(db)

@router.post("/entries", response_model=schemas.OrthopedicEntryResponse)
async def create_orthopedic_entry(
    entry_data: schemas.OrthopedicEntryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    try:
        if str(entry_data.patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 ORTHOPEDIC Received POST data:", entry_data.dict())
        
        # Check for existing entry
        existing_entry = orthopedic_service.get_entry_by_patient_and_date(
            entry_data.patient_id, 
            entry_data.submission_date
        )
        
        if existing_entry:
            db_entry = orthopedic_service.update_entry(existing_entry.id, entry_data.dict())
            action = 'UPDATE'
            print(f"🔄 Updated existing entry ID: {db_entry.id}")
        else:
            db_entry = orthopedic_service.create_entry(entry_data.dict())
            action = 'CREATE'
            print(f"🆕 Created new entry ID: {db_entry.id}")
        
        log_audit(
            db=orthopedic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action=action,
            resource_type='ORTHOPEDIC_ENTRY',
            patient_id=int(entry_data.patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data.dict()
        )
        
        return schemas.OrthopedicEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            photo_urls=db_entry.photo_urls,
            created_at=db_entry.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ ORTHOPEDIC POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create/update orthopedic progress entry: {str(e)}")
@router.get("/entries")
async def get_all_orthopedic_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    try:
        entries = orthopedic_service.get_all_entries()
        #entries = [e for e in entries if str(e.patient_id) == str(current_user.id)]
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=orthopedic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ORTHOPEDIC_ENTRIES',
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
                "conditionType": "orthopedic",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "orthopedic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orthopedic entries: {str(e)}")


@router.get("/entries/{patient_id}/{date}")
async def check_orthopedic_entry(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = orthopedic_service.check_existing_entry(patient_id, date)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=orthopedic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ORTHOPEDIC_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking orthopedic entry: {str(e)}")


@router.get("/entries/patient/{patient_id}")
async def get_patient_orthopedic_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    orthopedic_service: services.OrthopedicProgressService = Depends(get_orthopedic_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = orthopedic_service.get_patient_entries(patient_id)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=orthopedic_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ORTHOPEDIC_ENTRIES',
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
                "conditionType": "orthopedic",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient orthopedic entries: {str(e)}")