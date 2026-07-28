from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from . import services, schemas
from app.dependencies import get_current_user
from app.models import User, UserRole
from app.utils.audit import log_audit

router = APIRouter(prefix="/cesarean", tags=["Cesarean Progress"])

def get_cesarean_service(db: Session = Depends(get_db)):
    return services.CesareanProgressService(db)

# ✅ ENDPOINT 1: CREATE ENTRY
@router.post("/entries", response_model=schemas.CesareanEntryResponse)
async def create_cesarean_entry(
    entry_data: schemas.CesareanEntryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    try:
        patient_id = entry_data.dict().get('patient_id') or entry_data.dict().get('patientId')
        if patient_id and str(patient_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        print("📥 Received POST data:", entry_data.dict())
        db_entry = cesarean_service.create_entry(entry_data.dict())
        
        log_audit(
            db=cesarean_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='CESAREAN_ENTRY',
            patient_id=int(patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=entry_data.dict()
        )
        
        return schemas.CesareanEntryResponse(
            id=db_entry.id,
            patient_id=db_entry.patient_id,
            patient_name=db_entry.patient_name,
            submission_date=db_entry.submission_date,
            common_data=db_entry.common_data,
            condition_data=db_entry.condition_data,
            photo_urls=db_entry.photo_urls if hasattr(db_entry, 'photo_urls') else [],
            created_at=db_entry.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print("❌ POST Error details:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create cesarean progress entry: {str(e)}")

# ✅ ENDPOINT 2: GET ALL ENTRIES FOR DASHBOARD
@router.get("/entries")
async def get_all_cesarean_entries(
    request: Request,
    current_user: User = Depends(get_current_user),
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    try:
        entries = cesarean_service.get_all_entries()
        # ========== ROLE-BASED ACCESS CONTROL ==========
        if current_user.role == UserRole.DOCTOR:
            from app.models import PatientDoctorAssignment
            assignments = cesarean_service.db.query(PatientDoctorAssignment.patient_id).filter(
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
        
        log_audit(
            db=cesarean_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CESAREAN_ENTRIES',
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
                "conditionType": "cesarean",
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "surgery_type": "cesarean"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cesarean entries: {str(e)}")

# ✅ ENDPOINT 3: CHECK EXISTING ENTRY BY PATIENT AND DATE
@router.get("/entries/{patient_id}/{date}")
async def check_cesarean_entry(
    patient_id: int,
    date: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        exists = cesarean_service.check_existing_entry(patient_id, date)
        
        log_audit(
            db=cesarean_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CESAREAN_ENTRY',
            patient_id=patient_id,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {"exists": exists, "patient_id": patient_id, "date": date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking cesarean entry: {str(e)}")

# ✅ ENDPOINT 4: GET ALL ENTRIES FOR A SPECIFIC PATIENT
@router.get("/entries/patient/{patient_id}")
async def get_patient_cesarean_entries(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    cesarean_service: services.CesareanProgressService = Depends(get_cesarean_service)
):
    if str(patient_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = cesarean_service.get_patient_entries(patient_id)
        
        log_audit(
            db=cesarean_service.db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CESAREAN_ENTRIES',
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
                "photo_urls": entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient cesarean entries: {str(e)}")