from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.utils.audit import log_audit
from fastapi import Request
from datetime import date, datetime, timedelta

import json
import os
import uuid
import shutil
from .models import MensHealthIntake, MensHealthEntry, MensHealthPhoto, MensHealthStatus, MensHealthCalibration
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Body
from typing import Dict, Optional  # Add Dict to imports

router = APIRouter()


# ========== PYDANTIC SCHEMAS ==========

class IntakeAnswers(BaseModel):
    main_concerns: List[str]
    other_concern_text: Optional[str] = None
    impact_level: int
    
    # Size & Girth branch
    measured_before: Optional[bool] = None
    size_concern_impact: Optional[List[str]] = None
    
    # Erectile Dysfunction branch
    ed_frequency: Optional[str] = None
    morning_erections: Optional[str] = None
    ed_duration_months: Optional[int] = None
    
    # Premature Ejaculation branch
    ielt_minutes: Optional[str] = None
    pe_techniques_tried: Optional[List[str]] = None
    pe_distress_level: Optional[int] = None
    
    # Low Testosterone branch
    low_t_symptoms: Optional[List[str]] = None
    t_tested_before: Optional[bool] = None
    
    # Peyronie's branch
    has_curvature: Optional[str] = None
    curvature_pain: Optional[str] = None
    curvature_angle_known: Optional[int] = None
    
    # Performance Anxiety branch
    anxiety_triggers: Optional[List[str]] = None
    anxiety_avoidance: Optional[bool] = None


class DailyEntryRequest(BaseModel):
    submission_date: str
    conditions_selected: List[str]
    condition_data: Dict[str, Any]
    photo_ids: Optional[List[int]] = None


# ========== RECOMMENDATION ENGINE ==========

def generate_recommendations(answers: IntakeAnswers) -> Dict[str, Any]:
    results = {
        "size_concern": {"recommended": False, "confidence": 0, "reasons": []},
        "erectile_dysfunction": {"recommended": False, "confidence": 0, "reasons": []},
        "premature_ejaculation": {"recommended": False, "confidence": 0, "reasons": []},
        "low_testosterone": {"recommended": False, "confidence": 0, "reasons": []},
        "peyronies": {"recommended": False, "confidence": 0, "reasons": []},
        "performance_anxiety": {"recommended": False, "confidence": 0, "reasons": []}
    }
    
    # Size & Girth
    if "size_concern" in answers.main_concerns:
        results["size_concern"]["recommended"] = True
        results["size_concern"]["confidence"] = 0.80
        results["size_concern"]["reasons"].append("You reported concerns about penis size")
    
    # Erectile Dysfunction
    if "erectile_difficulty" in answers.main_concerns:
        confidence = 50
        reasons = ["Difficulty with erections reported"]
        if answers.ed_frequency in ["most_of_the_time", "always"]:
            confidence += 30
            reasons.append("Frequent difficulty")
        if answers.morning_erections in ["rarely", "never"]:
            confidence += 20
            reasons.append("Absent morning erections suggest physical cause")
        results["erectile_dysfunction"]["recommended"] = True
        results["erectile_dysfunction"]["confidence"] = min(0.95, confidence / 100)
        results["erectile_dysfunction"]["reasons"] = reasons
    
    # Premature Ejaculation
    if "premature_ejaculation" in answers.main_concerns:
        confidence = 50
        reasons = ["Ejaculation timing concerns reported"]
        if answers.ielt_minutes in ["less_30_seconds", "30_seconds_1_minute"]:
            confidence += 30
            reasons.append("IELT less than 1 minute")
        if answers.pe_distress_level and answers.pe_distress_level >= 7:
            confidence += 20
            reasons.append("High distress level")
        results["premature_ejaculation"]["recommended"] = True
        results["premature_ejaculation"]["confidence"] = min(0.95, confidence / 100)
        results["premature_ejaculation"]["reasons"] = reasons
    
    # Low Testosterone
    if "low_testosterone" in answers.main_concerns:
        confidence = 40
        reasons = ["Low testosterone symptoms reported"]
        if answers.low_t_symptoms:
            symptom_count = len(answers.low_t_symptoms)
            confidence += min(30, symptom_count * 10)
            reasons.append(f"{symptom_count} symptoms reported")
        results["low_testosterone"]["recommended"] = True
        results["low_testosterone"]["confidence"] = min(0.95, confidence / 100)
        results["low_testosterone"]["reasons"] = reasons
    
    # Peyronie's Disease
    if "peyronies" in answers.main_concerns:
        confidence = 60
        reasons = ["Peyronie's disease symptoms reported"]
        if answers.has_curvature == "yes_noticeable":
            confidence += 20
            reasons.append("Noticeable curvature")
        if answers.curvature_pain == "yes_always" or answers.curvature_pain == "yes_sometimes":
            confidence += 20
            reasons.append("Pain with erection")
        results["peyronies"]["recommended"] = True
        results["peyronies"]["confidence"] = min(0.95, confidence / 100)
        results["peyronies"]["reasons"] = reasons
    
    # Performance Anxiety
    if "performance_anxiety" in answers.main_concerns:
        results["performance_anxiety"]["recommended"] = True
        results["performance_anxiety"]["confidence"] = 0.75
        results["performance_anxiety"]["reasons"].append("Performance anxiety reported")
    
    return results


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
        existing_intake = db.query(MensHealthIntake).filter(
            MensHealthIntake.patient_id == current_user.id,
            MensHealthIntake.is_active == True
        ).first()
        
        if existing_intake:
            existing_intake.is_active = False
        
        recommendations = generate_recommendations(answers)
        
        intake = MensHealthIntake(
            patient_id=current_user.id,
            answers=answers.dict(),
            recommendations=recommendations,
            is_active=True
        )
        
        db.add(intake)
        db.commit()
        db.refresh(intake)
        
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE',
            resource_type='MENS_HEALTH_INTAKE',
            resource_id=intake.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "intake_id": intake.id,
            "recommendations": recommendations,
            "message": "Intake saved successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving intake: {str(e)}")


@router.post("/entries")
def create_daily_entry(
    entry: DailyEntryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create daily entry for selected conditions"""
    
    try:
        submission_date = datetime.strptime(entry.submission_date, "%Y-%m-%d").date()
        
        existing_entry = db.query(MensHealthEntry).filter(
            and_(
                MensHealthEntry.patient_id == current_user.id,
                MensHealthEntry.submission_date == submission_date
            )
        ).first()
        
        status = MensHealthStatus.GOOD
        condition_data = entry.condition_data
        
        # Check for urgent flags
        if "erectile_dysfunction" in condition_data:
            ehs = condition_data["erectile_dysfunction"].get("erection_hardness_score", 0)
            if ehs <= 1:
                status = MensHealthStatus.URGENT
            elif ehs <= 2:
                status = MensHealthStatus.MONITOR
        
        if "premature_ejaculation" in condition_data:
            ielt = condition_data["premature_ejaculation"].get("ielt_seconds", 60)
            if ielt < 30:
                status = MensHealthStatus.MONITOR
        
        if "peyronies" in condition_data:
            pain = condition_data["peyronies"].get("pain_level", 0)
            if pain >= 7:
                status = MensHealthStatus.URGENT
        
        patient_name = current_user.name or f"Patient_{current_user.id}"
        
        if existing_entry:
            existing_entry.conditions_selected = entry.conditions_selected
            existing_entry.condition_data = condition_data
            existing_entry.status = status
            existing_entry.photo_ids = entry.photo_ids
            existing_entry.updated_at = func.now()
            db.commit()
            db.refresh(existing_entry)
            response_entry = existing_entry
        else:
            new_entry = MensHealthEntry(
                patient_id=current_user.id,
                patient_name=patient_name,
                submission_date=submission_date,
                conditions_selected=entry.conditions_selected,
                condition_data=condition_data,
                status=status,
                photo_ids=entry.photo_ids
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            response_entry = new_entry
        
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE' if not existing_entry else 'UPDATE',
            resource_type='MENS_HEALTH_ENTRY',
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
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(MensHealthEntry).filter(
        MensHealthEntry.patient_id == patient_id
    )
    
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(MensHealthEntry.submission_date >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(MensHealthEntry.submission_date <= end)
    
    if condition:
        query = query.filter(
            MensHealthEntry.conditions_selected.astext.contains(condition)
        )
    
    entries = query.order_by(MensHealthEntry.submission_date.desc()).all()
    
    return {
        "patient_id": patient_id,
        "total_entries": len(entries),
        "entries": [
            {
                "id": e.id,
                "submission_date": e.submission_date.isoformat(),
                "conditions_selected": e.conditions_selected,
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
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        submission_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    entry = db.query(MensHealthEntry).filter(
        and_(
            MensHealthEntry.patient_id == patient_id,
            MensHealthEntry.submission_date == submission_date
        )
    ).first()
    
    if not entry:
        return {"exists": False, "message": "No entry found for this date"}
    
    return {
        "exists": True,
        "id": entry.id,
        "submission_date": entry.submission_date.isoformat(),
        "conditions_selected": entry.conditions_selected,
        "condition_data": entry.condition_data,
        "status": entry.status.value,
        "photo_ids": entry.photo_ids
    }


@router.post("/photos")
async def upload_photo(
    file: UploadFile = File(...),
    condition: str = Form(...),
    entry_id: Optional[int] = Form(None),
    consent_shared: bool = Form(False),
    notes: Optional[str] = Form(None),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a photo for size measurement or Peyronie's tracking"""
    
    try:
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed")
        
        upload_dir = f"uploads/mens_health/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        base_url = str(request.base_url).rstrip('/')
        photo_url = f"{base_url}/uploads/mens_health/{current_user.id}/{unique_filename}"
        
        photo = MensHealthPhoto(
            patient_id=current_user.id,
            entry_id=entry_id,
            condition=condition,
            photo_url=photo_url,
            thumbnail_url=photo_url,
            notes=notes,
            consent_shared=consent_shared
        )
        
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        if entry_id:
            entry = db.query(MensHealthEntry).filter(
                and_(
                    MensHealthEntry.id == entry_id,
                    MensHealthEntry.patient_id == current_user.id
                )
            ).first()
            if entry:
                current_photo_ids = entry.photo_ids or []
                if photo.id not in current_photo_ids:
                    current_photo_ids.append(photo.id)
                    entry.photo_ids = current_photo_ids
                    db.commit()
        
        return {
            "id": photo.id,
            "photo_url": photo_url,
            "consent_shared": consent_shared,
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
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(MensHealthPhoto).filter(
        MensHealthPhoto.patient_id == patient_id
    )
    
    if condition:
        query = query.filter(MensHealthPhoto.condition == condition)
    
    photos = query.order_by(MensHealthPhoto.taken_at.desc()).all()
    
    # Only return photos that user consented to share (for doctors)
    if current_user.role.value == "doctor":
        photos = [p for p in photos if p.consent_shared]
    
    return {
        "patient_id": patient_id,
        "total_photos": len(photos),
        "photos": [
            {
                "id": p.id,
                "condition": p.condition,
                "photo_url": p.photo_url,
                "taken_at": p.taken_at.isoformat(),
                "notes": p.notes,
                "metadata": str(p.metadata) if p.metadata else None
            }
            for p in photos
        ]
    }


@router.get("/conditions")
def get_available_conditions():
    return {
        "conditions": [
            {"id": "size_concern", "name": "Size & Girth", "icon": "📏", "color": "#3b82f6"},
            {"id": "erectile_dysfunction", "name": "Erectile Dysfunction", "icon": "⚠️", "color": "#ef4444"},
            {"id": "premature_ejaculation", "name": "Premature Ejaculation", "icon": "⏱️", "color": "#f59e0b"},
            {"id": "low_testosterone", "name": "Low Testosterone", "icon": "⚡", "color": "#8B5CF6"},
            {"id": "peyronies", "name": "Peyronie's Disease", "icon": "📐", "color": "#10b981"},
            {"id": "performance_anxiety", "name": "Performance Anxiety", "icon": "😰", "color": "#ec4899"}
        ]
    }

 
  



@router.get("/entries")
def get_all_entries(
    patient_id: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all men's sexual health entries.
    Doctors can see all patients. Patients can only see their own.
    """
    try:
        query = db.query(MensHealthEntry)
        
        # Role-based filtering
        if current_user.role.value != "admin" and current_user.role.value != "doctor":
            # Regular patient can only see their own entries
            query = query.filter(MensHealthEntry.patient_id == current_user.id)
        elif patient_id:
            # Filter by specific patient if provided
            query = query.filter(MensHealthEntry.patient_id == patient_id)
        
        entries = query.order_by(MensHealthEntry.submission_date.desc()).all()
        
        result_entries = []
        for entry in entries:
            # Fetch photo URLs from photo_ids
            photo_urls = []
            if entry.photo_ids and len(entry.photo_ids) > 0:
                photos = db.query(MensHealthPhoto).filter(MensHealthPhoto.id.in_(entry.photo_ids)).all()
                photo_urls = [p.photo_url for p in photos]
            
            result_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date.isoformat(),
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "conditions_selected": entry.conditions_selected,
                "condition_data": entry.condition_data,
                "status": entry.status.value if hasattr(entry.status, 'value') else str(entry.status),
                "photo_ids": entry.photo_ids,
                "photo_urls": photo_urls,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
            })
        
        # Add audit log
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='READ',
            resource_type='MENS_HEALTH_ENTRY',
            patient_id=patient_id or current_user.id,
            status='success',
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None
        )
        
        return {
            "success": True,
            "entries": result_entries
        }
        
    except Exception as e:
        print(f"❌ Error in GET /entries: {str(e)}")
        return {"success": False, "error": str(e)}







@router.get("/intake/active")
def get_active_intake(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    intake = db.query(MensHealthIntake).filter(
        MensHealthIntake.patient_id == current_user.id,
        MensHealthIntake.is_active == True
    ).first()
    
    if not intake:
        return {"has_intake": False}
    
    # Extract recommended conditions
    recommendations = intake.recommendations
    conditions = [cond for cond, data in recommendations.items() if data.get("recommended")]
    
    # Get condition names for display
    condition_names = []
    for cond in conditions:
        names = {
            "size_concern": "Size & Girth",
            "erectile_dysfunction": "Erectile Dysfunction",
            "premature_ejaculation": "Premature Ejaculation",
            "low_testosterone": "Low Testosterone",
            "peyronies": "Peyronie's Disease",
            "performance_anxiety": "Performance Anxiety"
        }
        if cond in names:
            condition_names.append(names[cond])
    
    return {
        "has_intake": True,
        "intake_id": intake.id,
        "conditions": conditions,
        "condition_names": condition_names,
        "answers": intake.answers
        # REMOVE THIS LINE: "created_at": intake.created_at.isoformat() if intake.created_at else None
    }