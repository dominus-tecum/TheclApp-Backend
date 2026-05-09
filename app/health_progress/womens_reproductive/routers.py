from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.utils.audit import log_audit
from .models import WomensHealthIntake, WomensHealthEntry, WomensHealthPhoto, WomensHealthStatus
import json
import os
import uuid
import shutil


router = APIRouter()


# ========== PYDANTIC SCHEMAS ==========

class IntakeAnswers(BaseModel):
    main_concerns: List[str]
    other_concern_text: Optional[str] = None
    
    # Vaginismus - flat fields
    finger_pain: Optional[str] = None
    pain_only_with_partner: Optional[str] = None
    pain_sensation: Optional[List[str]] = None
    
    # Endometriosis - flat fields
    endometriosis_pain_level: Optional[int] = None
    pain_between_periods: Optional[bool] = None
    bowel_pain: Optional[bool] = None
    bladder_pain: Optional[bool] = None
    pain_radiates_to: Optional[List[str]] = None
    pain_duration_months: Optional[int] = None
    missed_work_days: Optional[int] = None
    
    # STI - flat fields
    lesion_appearance: Optional[List[str]] = None
    sti_symptoms: Optional[List[str]] = None
    first_noticed_days: Optional[int] = None
    new_partner_last_3months: Optional[bool] = None
    previous_occurrence: Optional[bool] = None
    
    # Menopause - flat fields
    age: Optional[str] = None
    period_status: Optional[str] = None
    hot_flash_frequency: Optional[str] = None
    hot_flash_severity: Optional[int] = None
    other_menopause_symptoms: Optional[List[str]] = None
    
    # PCOS - flat fields
    cycle_frequency: Optional[str] = None
    jawline_acne: Optional[bool] = None
    facial_hair: Optional[bool] = None
    body_hair: Optional[bool] = None
    scalp_hair_thinning: Optional[bool] = None
    weight_difficulty: Optional[bool] = None


class RecommendationRequest(BaseModel):
    answers: IntakeAnswers


class RecommendationResponse(BaseModel):
    conditions: Dict[str, Dict[str, Any]]
    notes: str


class DailyEntryCommonData(BaseModel):
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: int = 5
    sleep_hours: float = 7
    sleep_quality: int = 3
    medications: Dict = {}
    symptoms: Dict = {}
    notes: str = ""


class DailyEntryRequest(BaseModel):
    submission_date: str
    conditions_selected: List[str]
    common_data: Optional[DailyEntryCommonData] = None  # ✅ Optional
    condition_data: Dict[str, Any]
    photo_ids: Optional[List[int]] = None


class DailyEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    conditions_selected: List[str]
    status: str
    submitted_at: str


# ========== RECOMMENDATION ENGINE ==========

def generate_recommendations(answers: IntakeAnswers) -> RecommendationResponse:
    results = {
        "vaginismus": {"recommended": False, "confidence": 0, "reasons": []},
        "endometriosis": {"recommended": False, "confidence": 0, "reasons": []},
        "sti": {"recommended": False, "confidence": 0, "reasons": []},
        "menopause": {"recommended": False, "confidence": 0, "reasons": []},
        "pcos": {"recommended": False, "confidence": 0, "reasons": []}
    }
    notes = []
    
    # Vaginismus
    if "pain_with_sex" in answers.main_concerns:
        if answers.finger_pain == "yes":
            results["vaginismus"]["recommended"] = True
            results["vaginismus"]["confidence"] = 0.92
            results["vaginismus"]["reasons"].append("Pain with finger insertion")
        elif answers.pain_only_with_partner == "yes":
            results["vaginismus"]["recommended"] = True
            results["vaginismus"]["confidence"] = 0.65
            results["vaginismus"]["reasons"].append("Pain only with partner")
    
    # Endometriosis
    if "painful_periods" in answers.main_concerns:
        confidence = 0
        reasons = []
        if answers.pain_between_periods:
            confidence += 35
            reasons.append("Pain between periods")
        if answers.bowel_pain:
            confidence += 30
            reasons.append("Pain with bowel movements")
        if answers.bladder_pain:
            confidence += 20
            reasons.append("Pain with urination")
        if answers.pain_duration_months and answers.pain_duration_months >= 6:
            confidence += 15
            reasons.append("Pain for 6+ months")
        if confidence >= 40:
            results["endometriosis"]["recommended"] = True
            results["endometriosis"]["confidence"] = min(0.95, confidence / 100)
            results["endometriosis"]["reasons"] = reasons
    
    # STI
    if "skin_changes" in answers.main_concerns:
        confidence = 50
        reasons = ["Genital skin changes reported"]
        if answers.lesion_appearance and "blisters" in answers.lesion_appearance:
            confidence += 30
            reasons.append("Blisters/sores visible")
        if answers.sti_symptoms and "burning" in answers.sti_symptoms:
            confidence += 10
            reasons.append("Burning sensation")
        if answers.new_partner_last_3months:
            confidence += 10
            reasons.append("New partner in last 3 months")
        results["sti"]["recommended"] = True
        results["sti"]["confidence"] = min(0.95, confidence / 100)
        results["sti"]["reasons"] = reasons
    
    # Menopause
    if "hot_flashes" in answers.main_concerns:
        confidence = 0
        reasons = []
        has_age_or_frequency = False
    
        if answers.hot_flash_frequency in ["daily", "several_daily", "hourly"]:
           confidence += 40
           reasons.append(f"Frequent hot flashes ({answers.hot_flash_frequency})")
           has_age_or_frequency = True
        if answers.period_status in ["irregular", "none_3_11months"]:
           confidence += 30
           reasons.append("Irregular or stopping periods")
        if answers.age in ["45_49", "50_54", "55_plus"]:
           confidence += 20
           reasons.append(f"Age {answers.age.replace('_', '-')}")
           has_age_or_frequency = True
        if answers.other_menopause_symptoms and "vaginal_dryness" in answers.other_menopause_symptoms:
           confidence += 10
           reasons.append("Vaginal dryness")
    
    # Require either frequent hot flashes OR age 45+ to recommend menopause
        if confidence >= 30 and has_age_or_frequency:
           results["menopause"]["recommended"] = True
           results["menopause"]["confidence"] = min(0.95, confidence / 100)
           results["menopause"]["reasons"] = reasons
    
    # PCOS
    if "irregular_periods" in answers.main_concerns:
        confidence = 0
        reasons = []
        if answers.cycle_frequency == "35_60_days":
            confidence += 30
            reasons.append("Cycles 35-60 days")
        elif answers.cycle_frequency == "60_plus_days":
            confidence += 40
            reasons.append("Cycles 60+ days")
        if answers.jawline_acne:
            confidence += 20
            reasons.append("Jawline acne")
        if answers.facial_hair:
            confidence += 25
            reasons.append("Unwanted facial hair")
        if answers.weight_difficulty:
            confidence += 15
            reasons.append("Difficulty losing weight")
        if confidence >= 40:
            results["pcos"]["recommended"] = True
            results["pcos"]["confidence"] = min(0.95, confidence / 100)
            results["pcos"]["reasons"] = reasons
    
    return RecommendationResponse(conditions=results, notes="\n".join(notes))


# ========== ENDPOINTS ==========

@router.post("/intake")
def save_intake(
    answers: IntakeAnswers,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save questionnaire answers and generate recommendations"""
    
    try:
        # Check if intake already exists for this patient
        existing_intake = db.query(WomensHealthIntake).filter(
            WomensHealthIntake.patient_id == current_user.id,
            WomensHealthIntake.is_active == True
        ).first()
        
        if existing_intake:
            # Deactivate old intake
            existing_intake.is_active = False
        
        # Generate recommendations
        recommendations = generate_recommendations(answers)
        
        # Create new intake
        intake = WomensHealthIntake(
            patient_id=current_user.id,
            answers=answers.dict(),
            recommendations=recommendations.dict(),
            is_active=True
        )
        
        db.add(intake)
        db.commit()
        db.refresh(intake)
        
        # Log audit
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE',
            resource_type='WOMENS_HEALTH_INTAKE',
            resource_id=intake.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "intake_id": intake.id,
            "recommendations": recommendations.dict(),
            "message": "Intake saved successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving intake: {str(e)}")


@router.post("/recommend")
def get_recommendations(
    answers: IntakeAnswers,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get condition recommendations without saving (for preview)"""
    
    recommendations = generate_recommendations(answers)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='WOMENS_HEALTH_RECOMMENDATIONS',
        patient_id=current_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return recommendations


@router.post("/entries")
def create_daily_entry(
    entry: DailyEntryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update daily entry for selected conditions"""
    
    try:
        # Parse submission date
        submission_date = datetime.strptime(entry.submission_date, "%Y-%m-%d").date()
        
        # Check if entry already exists for this date
        existing_entry = db.query(WomensHealthEntry).filter(
            and_(
                WomensHealthEntry.patient_id == current_user.id,
                WomensHealthEntry.submission_date == submission_date
            )
        ).first()
        
        # Calculate status based on conditions
        status = WomensHealthStatus.GOOD
        
        # Check for urgent flags in condition data
        condition_data = entry.condition_data
        
        # Vaginismus: pain > 8/10
        if "vaginismus" in condition_data:
            pain = condition_data["vaginismus"].get("pain_during_insertion", 0)
            if pain >= 8:
                status = WomensHealthStatus.URGENT
            elif pain >= 6:
                status = WomensHealthStatus.MONITOR
        
        # Endometriosis: pain > 8/10 or missed work
        if "endometriosis" in condition_data:
            pain = condition_data["endometriosis"].get("pain_level", 0)
            missed_work = condition_data["endometriosis"].get("missed_work", False)
            if pain >= 8 or missed_work:
                status = WomensHealthStatus.URGENT
            elif pain >= 6:
                status = WomensHealthStatus.MONITOR
        
        # STI: worsening condition
        if "sti" in condition_data:
            changed = condition_data["sti"].get("changed_since_last", "same")
            if changed == "worse":
                status = WomensHealthStatus.URGENT
        
        # Menopause: severe hot flashes
        if "menopause" in condition_data:
            severity = condition_data["menopause"].get("hot_flash_severity", 0)
            if severity >= 8:
                status = WomensHealthStatus.URGENT
            elif severity >= 6:
                status = WomensHealthStatus.MONITOR
        
        # PCOS: severe acne or cravings
        if "pcos" in condition_data:
            acne = condition_data["pcos"].get("acne_severity", 0)
            if acne >= 8:
                status = WomensHealthStatus.MONITOR
        
        patient_name = current_user.name or f"Patient_{current_user.id}"
        
        if existing_entry:
            # Update existing entry
            existing_entry.conditions_selected = entry.conditions_selected
            existing_entry.common_data = entry.common_data.dict()
            existing_entry.condition_data = condition_data
            existing_entry.status = status
            existing_entry.photo_ids = entry.photo_ids
            existing_entry.updated_at = func.now()
            
            db.commit()
            db.refresh(existing_entry)
            
            response_entry = existing_entry
        else:
            # Create new entry
            new_entry = WomensHealthEntry(
                patient_id=current_user.id,
                patient_name=patient_name,
                submission_date=submission_date,
                conditions_selected=entry.conditions_selected,
                common_data=entry.common_data.dict(),
                condition_data=condition_data,
                status=status,
                photo_ids=entry.photo_ids
            )
            
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            
            response_entry = new_entry
        
        # Log audit
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE' if not existing_entry else 'UPDATE',
            resource_type='WOMENS_HEALTH_ENTRY',
            resource_id=response_entry.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "id": response_entry.id,
            "submission_date": response_entry.submission_date.isoformat(),
            "status": response_entry.status.value,
            "message": "Entry saved successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving entry: {str(e)}")


@router.get("/entries/{patient_id}")
def get_patient_entries(
    patient_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    condition: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all entries for a patient with optional filters"""
    
    # Security check
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(WomensHealthEntry).filter(
        WomensHealthEntry.patient_id == patient_id
    )
    
    # Date filters
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(WomensHealthEntry.submission_date >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(WomensHealthEntry.submission_date <= end)
    
    # Condition filter (entries that include this condition)
    if condition:
        # JSON contains check for PostgreSQL
        query = query.filter(
            WomensHealthEntry.conditions_selected.astext.contains(condition)
        )
    
    entries = query.order_by(WomensHealthEntry.submission_date.desc()).all()
    
    # Log audit
    if request:
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='READ',
            resource_type='WOMENS_HEALTH_ENTRY',
            patient_id=patient_id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
    
    return {
        "patient_id": patient_id,
        "total_entries": len(entries),
        "entries": [
            {
                "id": e.id,
                "submission_date": e.submission_date.isoformat(),
                "conditions_selected": e.conditions_selected,
                "common_data": e.common_data,
                "condition_data": e.condition_data,
                "status": e.status.value,
                "photo_ids": e.photo_ids
            }
            for e in entries
        ]
    }


@router.get("/entries/{patient_id}/{date}")
def get_entry_by_date(
    patient_id: int,
    date: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get entry for a specific date"""
    
    # Security check
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        submission_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    entry = db.query(WomensHealthEntry).filter(
        and_(
            WomensHealthEntry.patient_id == patient_id,
            WomensHealthEntry.submission_date == submission_date
        )
    ).first()
    
    if not entry:
        return {"exists": False, "message": "No entry found for this date"}
    
    return {
        "exists": True,
        "id": entry.id,
        "submission_date": entry.submission_date.isoformat(),
        "conditions_selected": entry.conditions_selected,
        "common_data": entry.common_data,
        "condition_data": entry.condition_data,
        "status": entry.status.value,
        "photo_ids": entry.photo_ids
    }


@router.put("/entries/{entry_id}")
def update_entry(
    entry_id: int,
    entry: DailyEntryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing entry"""
    
    existing_entry = db.query(WomensHealthEntry).filter(
        and_(
            WomensHealthEntry.id == entry_id,
            WomensHealthEntry.patient_id == current_user.id
        )
    ).first()
    
    if not existing_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    try:
        submission_date = datetime.strptime(entry.submission_date, "%Y-%m-%d").date()
        
        # Calculate status (same logic as POST)
        status = WomensHealthStatus.GOOD
        condition_data = entry.condition_data
        
        if "vaginismus" in condition_data:
            pain = condition_data["vaginismus"].get("pain_during_insertion", 0)
            if pain >= 8:
                status = WomensHealthStatus.URGENT
            elif pain >= 6:
                status = WomensHealthStatus.MONITOR
        
        if "endometriosis" in condition_data:
            pain = condition_data["endometriosis"].get("pain_level", 0)
            if pain >= 8:
                status = WomensHealthStatus.URGENT
            elif pain >= 6:
                status = WomensHealthStatus.MONITOR
        
        existing_entry.submission_date = submission_date
        existing_entry.conditions_selected = entry.conditions_selected
        existing_entry.common_data = entry.common_data.dict()
        existing_entry.condition_data = condition_data
        existing_entry.status = status
        existing_entry.photo_ids = entry.photo_ids
        existing_entry.updated_at = func.now()
        
        db.commit()
        db.refresh(existing_entry)
        
        # Log audit
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='UPDATE',
            resource_type='WOMENS_HEALTH_ENTRY',
            resource_id=entry_id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "id": existing_entry.id,
            "submission_date": existing_entry.submission_date.isoformat(),
            "status": existing_entry.status.value,
            "message": "Entry updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating entry: {str(e)}")


@router.post("/photos")
async def upload_photo(
    file: UploadFile = File(...),
    condition: str = Form(...),
    entry_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a photo for STI or skin condition tracking"""
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed")
        
        # Create upload directory if not exists
        upload_dir = f"uploads/womens_health/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate URL
        base_url = str(request.base_url).rstrip('/')
        photo_url = f"{base_url}/uploads/womens_health/{current_user.id}/{unique_filename}"
        
        # Create thumbnail (simple resize using PIL if available)
        thumbnail_url = photo_url  # For now, use same URL
        
        # Save to database
        photo = WomensHealthPhoto(
            patient_id=current_user.id,
            entry_id=entry_id,
            condition=condition,
            photo_url=photo_url,
            thumbnail_url=thumbnail_url,
            notes=notes
        )
        
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        # If entry_id provided, update entry's photo_ids
        if entry_id:
            entry = db.query(WomensHealthEntry).filter(
                and_(
                    WomensHealthEntry.id == entry_id,
                    WomensHealthEntry.patient_id == current_user.id
                )
            ).first()
            
            if entry:
                current_photo_ids = entry.photo_ids or []
                if photo.id not in current_photo_ids:
                    current_photo_ids.append(photo.id)
                    entry.photo_ids = current_photo_ids
                    db.commit()
        
        # Log audit
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE',
            resource_type='WOMENS_HEALTH_PHOTO',
            resource_id=photo.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "id": photo.id,
            "photo_url": photo_url,
            "thumbnail_url": thumbnail_url,
            "message": "Photo uploaded successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")


@router.get("/photos/{patient_id}")
def get_patient_photos(
    patient_id: int,
    condition: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all photos for a patient"""
    
    # Security check
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(WomensHealthPhoto).filter(
        WomensHealthPhoto.patient_id == patient_id
    )
    
    if condition:
        query = query.filter(WomensHealthPhoto.condition == condition)
    
    photos = query.order_by(WomensHealthPhoto.taken_at.desc()).all()
    
    return {
        "patient_id": patient_id,
        "total_photos": len(photos),
        "photos": [
            {
                "id": p.id,
                "condition": p.condition,
                "photo_url": p.photo_url,
                "thumbnail_url": p.thumbnail_url,
                "taken_at": p.taken_at.isoformat(),
                "notes": p.notes
            }
            for p in photos
        ]
    }


@router.get("/report/{patient_id}")
def generate_doctor_report(
    patient_id: int,
    start_date: str,
    end_date: str,
    condition: str,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a report for the doctor"""
    
    # Security check
    if patient_id != current_user.id and current_user.role.value != "admin" and current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get entries in date range
    entries = db.query(WomensHealthEntry).filter(
        and_(
            WomensHealthEntry.patient_id == patient_id,
            WomensHealthEntry.submission_date >= start,
            WomensHealthEntry.submission_date <= end,
            WomensHealthEntry.conditions_selected.astext.contains(condition)
        )
    ).order_by(WomensHealthEntry.submission_date).all()
    
    if not entries:
        return {
            "message": "No entries found for the specified period",
            "condition": condition,
            "date_range": {"start": start_date, "end": end_date}
        }
    
    # Extract condition-specific data
    condition_data_list = []
    for entry in entries:
        if entry.condition_data and condition in entry.condition_data:
            data_point = {
                "date": entry.submission_date.isoformat(),
                "data": entry.condition_data[condition]
            }
            condition_data_list.append(data_point)
    
    # Generate summary based on condition
    summary = {}
    
    if condition == "vaginismus":
        sizes = [d["data"].get("dilator_size", 0) for d in condition_data_list]
        pains = [d["data"].get("pain_during_insertion", 0) for d in condition_data_list]
        summary = {
            "total_entries": len(entries),
            "starting_dilator_size": sizes[0] if sizes else 0,
            "current_dilator_size": sizes[-1] if sizes else 0,
            "starting_pain": pains[0] if pains else 0,
            "current_pain": pains[-1] if pains else 0,
            "progress": "improving" if sizes and pains and sizes[-1] > sizes[0] and pains[-1] < pains[0] else "monitor"
        }
    
    elif condition == "endometriosis":
        pains = [d["data"].get("pain_level", 0) for d in condition_data_list]
        missed_work = sum(1 for d in condition_data_list if d["data"].get("missed_work", False))
        summary = {
            "total_entries": len(entries),
            "average_pain": sum(pains) / len(pains) if pains else 0,
            "max_pain": max(pains) if pains else 0,
            "days_missed_work": missed_work,
            "needs_doctor_visit": missed_work >= 3 or (pains and max(pains) >= 7)
        }
    
    elif condition == "sti":
        changes = [d["data"].get("changed_since_last", "same") for d in condition_data_list]
        summary = {
            "total_entries": len(entries),
            "worsening_count": sum(1 for c in changes if c == "worse"),
            "improving_count": sum(1 for c in changes if c == "improved"),
            "needs_doctor_visit": any(c == "worse" for c in changes)
        }
    
    elif condition == "menopause":
        hot_flashes = [d["data"].get("hot_flash_count", 0) for d in condition_data_list]
        severities = [d["data"].get("hot_flash_severity", 0) for d in condition_data_list]
        summary = {
            "total_entries": len(entries),
            "average_hot_flashes_per_day": sum(hot_flashes) / len(hot_flashes) if hot_flashes else 0,
            "average_severity": sum(severities) / len(severities) if severities else 0,
            "severe_cases": sum(1 for s in severities if s >= 7)
        }
    
    elif condition == "pcos":
        cycles = [d["data"].get("cycle_day", 0) for d in condition_data_list]
        acnes = [d["data"].get("acne_severity", 0) for d in condition_data_list]
        summary = {
            "total_entries": len(entries),
            "average_cycle_day": sum(cycles) / len(cycles) if cycles else 0,
            "average_acne": sum(acnes) / len(acnes) if acnes else 0
        }
    
    # Log audit
    if request:
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='READ',
            resource_type='WOMENS_HEALTH_REPORT',
            patient_id=patient_id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
    
    return {
        "patient_id": patient_id,
        "condition": condition,
        "date_range": {"start": start_date, "end": end_date},
        "summary": summary,
        "data_points": len(condition_data_list),
        "raw_data": condition_data_list if len(condition_data_list) <= 30 else "Too many data points, use filter"
    }


@router.get("/conditions")
def get_available_conditions():
    """Get list of available conditions for the tracker"""
    
    return {
        "conditions": [
            {
                "id": "vaginismus",
                "name": "Vaginismus",
                "description": "Pain with sex, difficulty with penetration",
                "icon": "female",
                "color": "#ec4899"
            },
            {
                "id": "endometriosis",
                "name": "Endometriosis",
                "description": "Severe period pain, pain between periods",
                "icon": "body",
                "color": "#dc2626"
            },
            {
                "id": "sti",
                "name": "STI / Genital Skin",
                "description": "Sores, warts, itching, unusual discharge",
                "icon": "warning",
                "color": "#f59e0b"
            },
            {
                "id": "menopause",
                "name": "Menopause",
                "description": "Hot flashes, night sweats, vaginal dryness",
                "icon": "thermometer",
                "color": "#8B5CF6"
            },
            {
                "id": "pcos",
                "name": "PCOS",
                "description": "Irregular periods, acne, facial hair",
                "icon": "alert-circle",
                "color": "#10b981"
            }
        ]
    }

@router.get("/entries")
def get_all_entries(
    patient_id: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all entries - admin sees all, patient sees their own"""
    
    query = db.query(WomensHealthEntry)
    
    # Filter by role
    if current_user.role.value == "admin":
        if patient_id:
            query = query.filter(WomensHealthEntry.patient_id == patient_id)
    else:
        query = query.filter(WomensHealthEntry.patient_id == current_user.id)
    
    entries = query.order_by(WomensHealthEntry.submission_date.desc()).all()
    
    # Format for dashboard compatibility
    result_entries = []
    for entry in entries:
        result_entries.append({
            "id": entry.id,
            "patient_id": entry.patient_id,
            "patient_name": entry.patient_name,
            "submission_date": entry.submission_date.isoformat(),
            "conditions_selected": entry.conditions_selected,
            "condition_data": entry.condition_data,
            "status": entry.status.value if hasattr(entry.status, 'value') else str(entry.status),
            "photo_ids": entry.photo_ids,
            "photo_urls": []
        })
    
    # Log audit
    if request:
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='READ',
            resource_type='WOMENS_HEALTH_ENTRY',
            patient_id=patient_id or current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
    
    return {
        "success": True,
        "entries": result_entries
    }

@router.get("/intake/active")
def get_active_intake(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    intake = db.query(WomensHealthIntake).filter(
        WomensHealthIntake.patient_id == current_user.id,
        WomensHealthIntake.is_active == True
    ).first()
    
    if not intake:
        return {"has_intake": False}
    
    # Parse recommendations if it's a string
    recommendations = intake.recommendations
    if isinstance(recommendations, str):
        import json
        recommendations = json.loads(recommendations)
    
    # Check the actual structure
    print("🔍 Recommendations structure:", type(recommendations))
    print("🔍 Recommendations content:", recommendations)
    
    conditions = []
    condition_names = []
    
    # The recommendations might be under a "conditions" key
    if "conditions" in recommendations:
        rec_data = recommendations["conditions"]
    else:
        rec_data = recommendations
    
    for cond, data in rec_data.items():
        if isinstance(data, dict) and data.get("recommended"):
            conditions.append(cond)
            names = {
                "vaginismus": "Vaginismus",
                "endometriosis": "Endometriosis", 
                "sti": "STI / Genital Skin",
                "menopause": "Menopause",
                "pcos": "PCOS"
            }
            if cond in names:
                condition_names.append(names[cond])
    
    return {
        "has_intake": True,
        "intake_id": intake.id,
        "conditions": conditions,
        "condition_names": condition_names
    }