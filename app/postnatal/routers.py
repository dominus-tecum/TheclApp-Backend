from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.postnatal.models import PostnatalEntry, PostnatalProfile
from app.postnatal.schemas import PostnatalCreate, PostnatalResponse, PostnatalCheckResponse, PostnatalProfileCreate, PostnatalProfileResponse
from app.postnatal.services import PostnatalService
from app.dependencies import get_current_user  # ← ADD THIS
from app.organization.dependencies import get_current_organization
from app.models import Organization

from fastapi import APIRouter, Depends, HTTPException, Request  # ← Add Request
from app.utils.audit import log_audit  # ← Add this
from app.models import User, PatientProfile  # ← ADD PatientProfile here

router = APIRouter()

@router.post("/profile", response_model=PostnatalProfileResponse)
async def create_postnatal_profile(
    profile: PostnatalProfileCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if profile.patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print("🚨 Received postnatal profile:", profile.dict())
    result = PostnatalService.create_or_update_profile(db=db, patient_id=profile.patient_id, profile_data=profile, organization_id=org.id)
    print("🚨 Profile saved with ID:", result.id)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='CREATE',
        resource_type='POSTNATAL_PROFILE',
        patient_id=int(profile.patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value=profile.dict()
    )
    
    return result

@router.get("/profile", response_model=PostnatalProfileResponse)
async def get_postnatal_profile(
    patient_id: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    profile = PostnatalService.get_profile(db, patient_id, org.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='POSTNATAL_PROFILE',
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return profile

@router.post("/entries", response_model=PostnatalResponse)
async def create_postnatal_entry(
    entry: PostnatalCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if entry.patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print("🚨 Received postnatal entry:", entry.dict())
    result = PostnatalService.create_postnatal_entry(db=db, entry=entry, organization_id=org.id)
    print("🚨 Entry saved with ID:", result.id)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='CREATE',
        resource_type='POSTNATAL_ENTRY',
        patient_id=int(entry.patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value=entry.dict()
    )
    
    return result

@router.get("/entries/{patient_id}/{date}", response_model=PostnatalCheckResponse)
async def check_existing_entry(
    patient_id: str,
    date: date,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing_entry = PostnatalService.check_existing_entry(db, patient_id, date, org.id)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='POSTNATAL_ENTRY',
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return PostnatalCheckResponse(
        exists=existing_entry is not None,
        entry_id=existing_entry.id if existing_entry else None
    )

@router.get("/entries")
async def get_all_postnatal_entries(
    request: Request,
    current_user: User = Depends(get_current_user),  # ← CHANGED: User to dict
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    try:
        # ← ADDED: Super admin check
        if current_user.is_super_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # ← ADDED: Doctor filter
        if current_user.role.value == 'doctor':
            from app.models import PatientDoctorAssignment
            assignments = db.query(PatientDoctorAssignment.patient_id).filter(
                PatientDoctorAssignment.doctor_id == current_user.id,
                PatientDoctorAssignment.end_date == None
            ).all()
            patient_ids = [a[0] for a in assignments]
            
            entries = PostnatalService.get_all_postnatal_entries(db, org.id)
            if patient_ids:
                entries = [e for e in entries if int(e.patient_id) in patient_ids]
            else:
                entries = []
        else:
            entries = PostnatalService.get_all_postnatal_entries(db, org.id)
        
        # ✅ ADD AUDIT LOG (YOUR EXISTING CODE - with .get() changes)
        log_audit(
            db=db,
            user_id=current_user.id,  # ← CHANGED
            username=current_user.username,  # ← CHANGED
            user_role=current_user.role.value,  # ← CHANGED
            action='READ',
            resource_type='POSTNATAL_ENTRIES',
            patient_id=current_user.id,  # ← CHANGED
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
                "infant_name": entry.infant_name,
                "submission_date": entry.submission_date,
                "condition_type": entry.condition_type,
                "status": entry.status,
                "days_postpartum": entry.days_postpartum,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "maternal_temperature": entry.maternal_temperature,
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "maternal_heart_rate": entry.maternal_heart_rate,
                "sleep_hours": entry.sleep_hours,
                "pain_level": entry.pain_level,
                "pain_location": entry.pain_location,
                "perineal_pain": entry.perineal_pain,
                "uterine_pain": entry.uterine_pain,
                "nipple_pain": entry.nipple_pain,
                "c_section_pain": entry.c_section_pain,
                "lochia_flow": entry.lochia_flow,
                "lochia_color": entry.lochia_color,
                "lochia_odor": entry.lochia_odor,
                "healing_progress": entry.healing_progress,
                "perineal_tear": entry.perineal_tear,
                "incision_redness": entry.incision_redness,
                "incision_discharge": entry.incision_discharge,
                "breastfeeding_status": entry.breastfeeding_status,
                "breast_engorgement": entry.breast_engorgement,
                "nipple_condition": entry.nipple_condition,
                "milk_supply": entry.milk_supply,
                "feeding_method": entry.feeding_method,
                "feeding_frequency": entry.feeding_frequency,
                "feeding_duration": entry.feeding_duration,
                "latching_quality": entry.latching_quality,
                "baby_blues_symptoms": entry.baby_blues_symptoms,
                "maternal_energy": entry.maternal_energy,
                "appetite": entry.appetite,
                "bowel_movement": entry.bowel_movement,
                "urinary_frequency": entry.urinary_frequency,
                "incontinence": entry.incontinence,
                "baby_feeding_frequency": entry.baby_feeding_frequency,
                "baby_urination_frequency": entry.baby_urination_frequency,
                "baby_bowel_movement_frequency": entry.baby_bowel_movement_frequency,
                "baby_weight_gain": entry.baby_weight_gain,
                "wet_diapers": entry.wet_diapers,
                "soiled_diapers": entry.soiled_diapers,
                "stool_color": entry.stool_color,
                "stool_consistency": entry.stool_consistency,
                "infant_temperature": entry.infant_temperature,
                "infant_heart_rate": entry.infant_heart_rate,
                "jaundice_level": entry.jaundice_level,
                "umbilical_cord": entry.umbilical_cord,
                "skin_condition": entry.skin_condition,
                "infant_alertness": entry.infant_alertness,
                "sleep_pattern": entry.sleep_pattern,
                "crying_level": entry.crying_level,
                "medication_adherence": entry.medication_adherence,
                "missed_medications": entry.missed_medications,
                "additional_notes": entry.additional_notes,
                "additional_concerns": entry.additional_concerns
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "condition_type": "postnatal"
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/patient/{patient_id}/delivery-date")
async def update_delivery_date(
    patient_id: str,
    delivery_date: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == int(patient_id)).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient.delivery_date = delivery_date
    db.commit()

    # ✅ ADD AUDIT LOG HERE (no old_value needed)
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='UPDATE',
        resource_type='POSTNATAL_PROFILE',
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"delivery_date": delivery_date}
    )
    
    return {"delivery_date": delivery_date}  


@router.delete("/entries/{entry_id}")
def delete_postnatal_entry(
    entry_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    entry = db.query(PostnatalEntry).filter(
        PostnatalEntry.id == entry_id,
        PostnatalEntry.organization_id == org.id 
        ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='DELETE',
        resource_type='POSTNATAL_ENTRY',
        resource_id=entry_id,
        patient_id=entry.patient_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Entry deleted"}          