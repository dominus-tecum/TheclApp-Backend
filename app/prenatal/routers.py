from sqlalchemy.orm import Session
from datetime import date
from app.organization.dependencies import get_current_organization
from app.models import Organization
from app.database import get_db
from app.prenatal.models import PrenatalEntry
from app.prenatal.schemas import PrenatalCreate, PrenatalResponse, PrenatalCheckResponse
from app.prenatal.services import PrenatalService
from app.dependencies import get_current_user
from app.models import User, PatientProfile, UserRole  # ← ADD UserRole HERE
from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.audit import log_audit


router = APIRouter()

@router.post("/entries", response_model=PrenatalResponse)
async def create_prenatal_entry(
    entry: PrenatalCreate,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if entry.patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print("🚨 Received prenatal entry:", entry.dict())
    result = PrenatalService.create_prenatal_entry(db=db, entry=entry, organization_id=org.id)
    print("🚨 Entry saved with ID:", result.id)

           # ✅ CONVERT DATE AND DATETIME TO STRINGS FOR AUDIT LOG
    entry_dict = entry.dict()
    if 'submission_date' in entry_dict and entry_dict['submission_date']:
        entry_dict['submission_date'] = str(entry_dict['submission_date'])
    if 'submitted_at' in entry_dict and entry_dict['submitted_at']:
        entry_dict['submitted_at'] = str(entry_dict['submitted_at'])
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='CREATE',
        resource_type='PRENATAL_ENTRY',
        patient_id=int(entry.patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value=entry_dict
    )
    
    return result

@router.get("/entries/{patient_id}/{date}", response_model=PrenatalCheckResponse)
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
    
    existing_entry = PrenatalService.check_existing_entry(db, patient_id, date, org.id)
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='PRENATAL_ENTRY',
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return PrenatalCheckResponse(
        exists=existing_entry is not None,
        entry_id=existing_entry.id if existing_entry else None
    )

@router.get("/patient/{patient_id}")
async def get_patient_info(
    patient_id: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == int(patient_id)).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='PRENATAL_PATIENT_INFO',
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "patient_id": patient.user_id,
        "patient_name": patient.name,
        "edd": patient.edd,
        "lmp": patient.lmp,
        "high_risk": patient.high_risk or False
    }

@router.get("/entries")
async def get_all_prenatal_entries(
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
        if current_user.role.value == UserRole.DOCTOR.value:
            from app.models import PatientDoctorAssignment
            assignments = db.query(PatientDoctorAssignment.patient_id).filter(
                PatientDoctorAssignment.doctor_id == current_user.id,
                PatientDoctorAssignment.end_date == None
            ).all()
            patient_ids = [a[0] for a in assignments]
            
            # Get entries and filter by assigned patients
            entries = PrenatalService.get_all_prenatal_entries(db, org.id)
            if patient_ids:
                entries = [e for e in entries if int(e.patient_id) in patient_ids]
            else:
                entries = []
        else:
            entries = PrenatalService.get_all_prenatal_entries(db, org.id)
        
        # ✅ ADD AUDIT LOG (YOUR EXISTING CODE - with .get() changes)
        log_audit(
            db=db,
            user_id=current_user.id,  # ← CHANGED
            username=current_user.username,  # ← CHANGED
            user_role=current_user.role.value,  # ← CHANGED
            action='READ',
            resource_type='PRENATAL_ENTRIES',
            patient_id=int(current_user.id),  # ← CHANGED
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
                "condition_type": entry.condition_type,
                "status": entry.status,
                "gestational_age": entry.gestational_age,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "maternal_temperature": entry.maternal_temperature,
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "maternal_heart_rate": entry.maternal_heart_rate,
                "respiratory_rate": entry.respiratory_rate,
                "oxygen_saturation": entry.oxygen_saturation,
                "weight": entry.weight,
                "edema": entry.edema,
                "edema_location": entry.edema_location,
                "headache": entry.headache,
                "visual_disturbances": entry.visual_disturbances,
                "epigastric_pain": entry.epigastric_pain,
                "nausea_level": entry.nausea_level,
                "vomiting_episodes": entry.vomiting_episodes,
                "fetal_movement": entry.fetal_movement,
                "movement_count": entry.movement_count,
                "movement_duration": entry.movement_duration,
                "contractions": entry.contractions,
                "contraction_frequency": entry.contraction_frequency,
                "contraction_duration": entry.contraction_duration,
                "contraction_intensity": entry.contraction_intensity,
                "vaginal_bleeding": entry.vaginal_bleeding,
                "bleeding_color": entry.bleeding_color,
                "fluid_leak": entry.fluid_leak,
                "fluid_color": entry.fluid_color,
                "fluid_amount": entry.fluid_amount,
                "urinary_frequency": entry.urinary_frequency,
                "dysuria": entry.dysuria,
                "urinary_incontinence": entry.urinary_incontinence,
                "appetite": entry.appetite,
                "heartburn": entry.heartburn,
                "constipation": entry.constipation,
                "medications_taken": entry.medications_taken,
                "missed_medications": entry.missed_medications,
                "additional_notes": entry.additional_notes,
                "high_risk": entry.high_risk
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "condition_type": "prenatal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prenatal entries: {str(e)}")


@router.get("/entries/patient/{patient_id}")
async def get_patient_prenatal_entries(
    patient_id: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        entries = db.query(PrenatalEntry).filter(
            PrenatalEntry.patient_id == patient_id,
            PrenatalEntry.organization_id == org.id
        ).all()
        
        # ✅ ADD AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='PRENATAL_ENTRIES',
            patient_id=int(patient_id),
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
                "condition_type": entry.condition_type,
                "status": entry.status,
                "gestational_age": entry.gestational_age,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                # ... rest of your fields
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient entries: {str(e)}")

@router.put("/patient/{patient_id}/lmp")
async def update_patient_lmp(
    patient_id: str,
    lmp: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Restore the authorization check
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == int(patient_id)).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    from datetime import datetime, timedelta
    lmp_date = datetime.strptime(lmp, "%Y-%m-%d")
    edd_date = lmp_date + timedelta(days=280)
    edd = edd_date.strftime("%Y-%m-%d")
    
    patient.lmp = lmp
    patient.edd = edd
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='UPDATE',
        resource_type='PRENATAL_LMP',
        patient_id=current_user.id,
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"lmp": lmp, "edd": edd}
    )
    
    return {"lmp": lmp, "edd": edd} 