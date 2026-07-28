from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from . import schemas, services
import logging
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User, UserRole  # ← ADD UserRole
from fastapi import APIRouter, HTTPException, Depends, Request  # ← Add Request
from app.utils.audit import log_audit  # ← Add this

logger = logging.getLogger(__name__)
router = APIRouter()

def get_abdominal_service(db: Session = Depends(get_db)) -> services.AbdominalProgressService:
    return services.AbdominalProgressService(db)

@router.post("/abdominal-entries", response_model=schemas.AbdominalEntryResponse)
async def create_abdominal_entry(
    entry_data: dict,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    try:
        if str(entry_data.get('patient_id')) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        logger.info(f"📝 Creating abdominal progress entry for patient {entry_data.get('patient_id')}")
        
        if abdominal_service.check_existing_entry(entry_data.get('patient_id'), entry_data.get('submission_date')):
            raise HTTPException(
                status_code=400, 
                detail=f"Abdominal progress entry already exists for patient {entry_data.get('patient_id')} on {entry_data.get('submission_date')}"
            )
        
        db_entry = abdominal_service.create_entry(entry_data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=abdominal_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='ABDOMINAL_ENTRY',
            patient_id=int(entry_data.get('patient_id')),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data
        )
        
        response_data = schemas.AbdominalEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            photo_urls=db_entry.photo_urls if hasattr(db_entry, 'photo_urls') else [],
            created_at=db_entry.created_at.isoformat()
        )
        
        logger.info(f"✅ Abdominal progress entry created successfully for patient {entry_data.get('patient_id')}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating abdominal progress entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create abdominal progress entry: {str(e)}")




@router.get("/abdominal-entries/patient/{patient_id}")
async def get_patient_abdominal_entries(
    patient_id: int,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = abdominal_service.get_patient_entries(patient_id)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=abdominal_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ABDOMINAL_ENTRIES',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "patient_id": patient_id,
            "entries": entries,
            "count": len(entries)
        }
    except Exception as e:
        logger.error(f"❌ Error fetching abdominal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch abdominal progress entries")



@router.get("/abdominal-entries/check/{patient_id}/{date}")
async def check_abdominal_entry_exists(
    patient_id: int,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entry = abdominal_service.get_entry_by_patient_and_date(patient_id, date)
        exists = entry is not None
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=abdominal_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ABDOMINAL_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "entry_id": entry.id if entry else None}
    except Exception as e:
        logger.error(f"❌ Error checking abdominal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check abdominal entry")

@router.get("/abdominal-entries")
async def get_all_abdominal_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    try:
        entries = abdominal_service.get_all_entries()
                # ========== ROLE-BASED ACCESS CONTROL ==========
        if current_user.role == UserRole.DOCTOR:
            from app.models import PatientDoctorAssignment
            assignments = abdominal_service.db.query(PatientDoctorAssignment.patient_id).filter(
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
            db=abdominal_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='ABDOMINAL_ENTRIES',
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
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "count": len(formatted_entries)
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching all abdominal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch abdominal entries")

@router.get("/abdominal/entries")
async def get_all_abdominal_entries_alt(
    current_user: User = Depends(get_current_user),  # ← ADD THIS
):
    """Get all abdominal surgery entries"""
    # This endpoint needs database connection - you may want to remove or fix it
    return {"entries": []}

@router.post("/abdominal-entries")
async def create_abdominal_entry_alt(
    entry_data: dict,
    current_user: User = Depends(get_current_user),  # ← ADD THIS
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    # ← ADD THIS VERIFICATION
    if str(entry_data.get('patient_id')) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        print("🔍 RECEIVED DATA:", entry_data)
        print("🔍 KEYS:", entry_data.keys())
        
        if 'common_data' in entry_data:
            print("🔍 COMMON_DATA:", entry_data['common_data'])
            print("🔍 COMMON_DATA KEYS:", entry_data['common_data'].keys())
        
        db_entry = abdominal_service.create_entry(entry_data)
        
        return {
            "id": db_entry.id,
            "patient_id": db_entry.patient_id,
            "patient_name": db_entry.patient_name,
            "submission_date": db_entry.submission_date,
            "common_data": db_entry.common_data,
            "condition_data": db_entry.condition_data,
            "photo_urls": db_entry.photo_urls if hasattr(db_entry, 'photo_urls') else [],
            "created_at": db_entry.created_at.isoformat()
        }
    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/abdominal-entries/{entry_id}")
async def update_abdominal_entry(
    entry_id: int,
    entry_data: dict,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    abdominal_service: services.AbdominalProgressService = Depends(get_abdominal_service)
):
    existing_entry = abdominal_service.get_entry(entry_id)
    if not existing_entry or str(existing_entry.patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        logger.info(f"📝 Updating abdominal progress entry {entry_id}")
        
        # ✅ LOG OLD VALUE BEFORE UPDATE
        old_value = {
            "common_data": existing_entry.common_data,
            "condition_data": existing_entry.condition_data
        }
        
        updated_entry = abdominal_service.update_entry(entry_id, entry_data)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=abdominal_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='UPDATE',
            resource_type='ABDOMINAL_ENTRY',
            resource_id=entry_id,
            patient_id=existing_entry.patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            old_value=old_value,
            new_value=entry_data
        )
        
        return {
            "id": updated_entry.id,
            "patient_id": updated_entry.patient_id,
            "patient_name": updated_entry.patient_name,
            "submission_date": updated_entry.submission_date,
            "common_data": updated_entry.common_data,
            "condition_data": updated_entry.condition_data,
            "photo_urls": updated_entry.photo_urls if hasattr(updated_entry, 'photo_urls') else [],
            "created_at": updated_entry.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error updating abdominal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")