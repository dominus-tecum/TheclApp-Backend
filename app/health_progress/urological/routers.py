from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user  # ← ADD THIS
from app.models import User, UserRole  # ← ADD UserRole
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit

router = APIRouter(prefix="/urological", tags=["Urological Progress"])

def get_urological_service(db: Session = Depends(get_db)):
    return services.UrologicalProgressService(db)

@router.post("/entries", response_model=schemas.UrologicalEntryResponse)
async def create_urological_entry(
    entry_data: schemas.UrologicalEntryCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    try:
        if str(entry_data.patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 UROLOGICAL: Received POST data:", entry_data.dict())


               # ✅ CHECK FOR EXISTING ENTRY
        existing_entry = urological_service.get_entry_by_patient_and_date(
            entry_data.patient_id, 
            entry_data.submission_date
        )
        
        service_data = {
            'patient_id': entry_data.patient_id,
            'patient_name': entry_data.patient_name,
            'submission_date': entry_data.submission_date,
            'surgery_type': entry_data.surgery_type,
            'common_data': entry_data.common_data.dict(),
            'condition_data': entry_data.condition_data.dict(),
            'photo_urls': entry_data.photo_urls if hasattr(entry_data, 'photo_urls') else []
        }
        
        if existing_entry:
            # UPDATE existing entry
            db_entry = urological_service.update_entry(existing_entry.id, service_data)
            action = 'UPDATE'
            print(f"🔄 Updated existing entry ID: {db_entry.id}")
        else:
            # CREATE new entry
            db_entry = urological_service.create_entry(service_data)
            action = 'CREATE'
            print(f"🆕 Created new entry ID: {db_entry.id}")
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=urological_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='UROLOGICAL_ENTRY',
            patient_id=int(entry_data.patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data.dict()
        )
        
        return schemas.UrologicalEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            surgery_type=db_entry.surgery_type,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            photo_urls=db_entry.photo_urls if hasattr(db_entry, 'photo_urls') else [],
            created_at=db_entry.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ UROLOGICAL POST Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create urological progress entry: {str(e)}")

@router.get("/entries")
async def get_all_urological_entries(
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    try:
        print("🔍 UROLOGICAL: Fetching all entries")
        entries = urological_service.get_all_entries()
        # ========== ROLE-BASED ACCESS CONTROL ==========
        if current_user.role == UserRole.DOCTOR:
            from app.models import PatientDoctorAssignment
            assignments = urological_service.db.query(PatientDoctorAssignment.patient_id).filter(
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
            db=urological_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='UROLOGICAL_ENTRIES',
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
                "conditionType": "urological",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        print(f"✅ UROLOGICAL: Retrieved {len(entries)} entries")
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "urological"
        }
        
    except Exception as e:
        print(f"❌ UROLOGICAL: Error retrieving all entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving urological entries: {str(e)}")

@router.get("/entries/{patient_id}/{date}")
async def check_urological_entry(
    patient_id: int, 
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    urological_service: services.UrologicalProgressService = Depends(get_urological_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        print(f"🔍 UROLOGICAL: Checking entry for patient {patient_id} on {date}")
        exists = urological_service.check_existing_entry(patient_id, date)
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=urological_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='UROLOGICAL_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists}
        
    except Exception as e:
        print(f"❌ UROLOGICAL: Error checking entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking urological entry: {str(e)}")