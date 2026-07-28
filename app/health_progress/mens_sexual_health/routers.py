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
from app.models import User, UserRole
from app.organization.dependencies import get_current_organization
from app.models import Organization
import json
import os
import uuid
import shutil
from .models import MensHealthIntake, MensHealthEntry, MensHealthPhoto, MensHealthStatus, MensHealthCalibration, MensHealthReport
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Body
from typing import Dict, Optional  # Add Dict to 
import cv2
import numpy as np


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

# ========== COMPATIBILITY DATA GENERATOR ==========

def generate_compatibility_data(length_cm: float, girth_cm: float = None):
    zones = [
        {
            "depth_range": "<10 cm",
            "percentage": "15%",
            "reaches": length_cm >= 10,
            "zone": "Cervix Area",
            "explanation": "The cervix is the narrow opening at the top of the vagina. Hitting it can be painful for many women. Study shows 15% of women has a depth less than 10cm.",
            "tip": "Let her control depth. Avoid deep thrusting."
        },
        {
            "depth_range": "10-12 cm",
            "percentage": "35%",
            "reaches": length_cm >= 10,
            "zone": "A-Spot Zone",
            "explanation": "The A-spot (anterior fornix) is a highly erogenous zone. Many women can orgasm from A-spot stimulation. 35% of women has a vaginal depth of 10-12cm",
            "tip": "Doggy style angled up works best."
        },
        {
            "depth_range": "12-14 cm",
            "percentage": "35%",
            "reaches": length_cm >= 12,
            "zone": "Posterior Fornix",
            "explanation": "The deepest part of the vagina, located behind the cervix. Stimulation here can produce deep, intense pleasure. Study shows 35% of women has a depth from 12-14cm.",
            "tip": "Missionary with pillow under hips is ideal."
        },
        {
            "depth_range": ">14 cm",
            "percentage": "15%",
            "reaches": length_cm >= 14,
            "zone": "Full Stimulation",
            "explanation": "You can stimulate both A-spot and G-spot simultaneously. The G-spot is located 5-8 cm inside on the front wall.",
            "tip": "Focus on angle, not depth. Cowgirl gives her control."
        }
    ]
    
    zones_reached = sum(1 for z in zones if z["reaches"])
    percentage_reached = (zones_reached / len(zones)) * 100
    
    return {
        "length_cm": length_cm,
        "girth_cm": girth_cm,
        "zones": zones,
        "summary": {
            "percentage_reached": round(percentage_reached, 1),
            "can_reach_aspot": length_cm >= 10,
            "can_reach_deepest": length_cm >= 12,
            "can_reach_full": length_cm >= 14
        }
    }    


# ========== ENDPOINTS ==========

@router.post("/intake")
def save_intake(
    answers: IntakeAnswers,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
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
            organization_id=org.id,
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
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
                organization_id=org.id,
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(MensHealthEntry).filter(
        MensHealthEntry.patient_id == patient_id,
        MensHealthEntry.organization_id == org.id
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

    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_ENTRY',
        patient_id=patient_id,
        status='success',
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get('user-agent') if request else None
    )
    
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
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
            MensHealthEntry.submission_date == submission_date,
            MensHealthEntry.organization_id == org.id
        )
    ).first()
    
    if not entry:
        return {"exists": False, "message": "No entry found for this date"}

    # ✅ ADD AUDIT LOG
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_ENTRY',
        resource_id=entry.id,
        patient_id=patient_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
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
            organization_id=org.id,
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

        # ✅ ADD AUDIT LOG HERE
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE',
            resource_type='MENS_HEALTH_PHOTO',
            resource_id=photo.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None,
            new_value={"condition": condition, "consent_shared": consent_shared}
        )
        
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    if patient_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(MensHealthPhoto).filter(
        MensHealthPhoto.patient_id == patient_id,
        MensHealthPhoto.organization_id == org.id 
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
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """
    Get all men's sexual health entries.
    Doctors can see all patients. Patients can only see their own.
    """
    try:
        query = db.query(MensHealthEntry).filter(
            MensHealthEntry.organization_id == org.id  # ← ADD
        )

        
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
    request: Request,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    # If user_id is provided and current user is doctor, get that user's intake
    if user_id is not None:
        if current_user.role.value not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        target_user_id = user_id
    else:
        target_user_id = current_user.id
    
    intake = db.query(MensHealthIntake).filter(
        MensHealthIntake.patient_id == target_user_id,
        MensHealthIntake.is_active == True,
        MensHealthIntake.organization_id == org.id
    ).first()
    
    if not intake:
        return {"has_intake": False}
    
    # Parse recommendations if it's a string
    recommendations = intake.recommendations
    if isinstance(recommendations, str):
        import json
        recommendations = json.loads(recommendations)
    
    conditions = []
    condition_names = []
    
    # Handle both formats
    if "conditions" in recommendations:
        rec_data = recommendations["conditions"]
    else:
        rec_data = recommendations
    
    names = {
        "size_concern": "Size & Girth",
        "erectile_dysfunction": "Erectile Dysfunction",
        "premature_ejaculation": "Premature Ejaculation",
        "low_testosterone": "Low Testosterone",
        "peyronies": "Peyronie's Disease",
        "performance_anxiety": "Performance Anxiety"
    }
    
    for cond, data in rec_data.items():
        if isinstance(data, dict) and data.get("recommended"):
            conditions.append(cond)
            if cond in names:
                condition_names.append(names[cond])
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_INTAKE',
        resource_id=intake.id if intake else None,
        patient_id=target_user_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "has_intake": True,
        "intake_id": intake.id,
        "conditions": conditions,
        "condition_names": condition_names,
        "answers": intake.answers  # ← Returns full answers
    }



@router.get("/intake/{patient_id}")
def get_patient_intake(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    # Doctor only
    if current_user.role.value != UserRole.DOCTOR.value:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    # Same logic as /intake/active but for specific patient
    intake = db.query(MensHealthIntake).filter(
        MensHealthIntake.patient_id == patient_id,
        MensHealthIntake.is_active == True,
        MensHealthIntake.organization_id == org.id
    ).first()
    
    if not intake:
        return {"has_intake": False}
    
    recommendations = intake.recommendations
    if isinstance(recommendations, str):
        import json
        recommendations = json.loads(recommendations)
    
    conditions = []
    condition_names = []
    
    if "conditions" in recommendations:
        rec_data = recommendations["conditions"]
    else:
        rec_data = recommendations
    
    names = {
        "size_concern": "Size & Girth",
        "erectile_dysfunction": "Erectile Dysfunction",
        "premature_ejaculation": "Premature Ejaculation",
        "low_testosterone": "Low Testosterone",
        "peyronies": "Peyronie's Disease",
        "performance_anxiety": "Performance Anxiety"
    }
    
    for cond, data in rec_data.items():
        if isinstance(data, dict) and data.get("recommended"):
            conditions.append(cond)
            if cond in names:
                condition_names.append(names[cond])
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_INTAKE',
        resource_id=intake.id,
        patient_id=patient_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "has_intake": True,
        "intake_id": intake.id,
        "patient_id": intake.patient_id,
        "completed_at": intake.completed_at,
        "conditions": conditions,
        "condition_names": condition_names,
        "answers": intake.answers
    }




@router.get("/approval-status")
def get_approval_status(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),org: Organization = Depends(get_current_organization)):
    intake = db.query(MensHealthIntake).filter(
        MensHealthIntake.patient_id == current_user.id,
        MensHealthIntake.is_active == True,
        MensHealthIntake.organization_id == org.id
    ).first()

    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_APPROVAL_STATUS',
        patient_id=current_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    if not intake:
        return {"status": "not_submitted"}
    
    if hasattr(intake, 'approved') and intake.approved:
        return {"status": "approved"}
    else:
        return {"status": "pending"}

@router.get("/pending-users")
def get_pending_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    if current_user.role.value != UserRole.DOCTOR.value:
            raise HTTPException(status_code=403, detail="Doctor access required")
    
    pending = []
    
    intakes = db.query(MensHealthIntake).filter(
        MensHealthIntake.is_active == True,
        MensHealthIntake.approved == False,
        MensHealthIntake.organization_id == org.id
    ).all()
    
    for intake in intakes:
        user = db.query(User).filter(User.id == intake.patient_id).first()
        if user:
            pending.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "submitted_at": intake.completed_at.isoformat() if intake.completed_at else None,
                "conditions": intake.recommendations if intake.recommendations else {}
            })
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='READ',
        resource_type='MENS_HEALTH_PENDING_USERS',
        patient_id=None,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"pending_count": len(pending)}
    )
    
    return pending

@router.put("/approve/{user_id}")
def approve_intake(
    user_id: int,
    request: Request, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_organization)
):
    if current_user.role.value != UserRole.DOCTOR.value:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    # Find active intake for this user (like Women's Health does)
    intake = db.query(MensHealthIntake).filter(
        MensHealthIntake.patient_id == user_id,
        MensHealthIntake.is_active == True,
        MensHealthIntake.organization_id == org.id
    ).first()
    
    if not intake:
        raise HTTPException(status_code=404, detail="No active intake found for this user")
    
    intake.approved = True
    intake.approved_at = datetime.now()
    db.commit()

    # ✅ ADD AUDIT LOG HERE
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action='UPDATE',
        resource_type='MENS_HEALTH_INTAKE',
        resource_id=intake.id,
        patient_id=user_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        
    )
    
    return {"message": f"Intake approved for user {user_id}"}    

# ========== REPORT ENDPOINTS ==========

@router.post("/reports/share/{patient_id}")
def share_report(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Doctor shares a compatibility report with patient"""
    
    if current_user.role.value != UserRole.DOCTOR.value:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    patient = db.query(User).filter(
        User.id == patient_id,
        User.organization_id == org.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    entry = db.query(MensHealthEntry).filter(
        MensHealthEntry.patient_id == patient_id,
        MensHealthEntry.organization_id == org.id
    ).order_by(MensHealthEntry.submission_date.desc()).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="No entries found for this patient")
    
    size_data = entry.condition_data.get("size_concern", {})
    length_cm = float(size_data.get("length_cm", 0))
    girth_cm = float(size_data.get("girth_cm", 0)) if size_data.get("girth_cm") else None
    
    if length_cm == 0:
        raise HTTPException(status_code=400, detail="No size measurement found")
    
    compatibility_data = generate_compatibility_data(length_cm, girth_cm)
    
    existing_report = db.query(MensHealthReport).filter(
        MensHealthReport.patient_id == patient_id,
        MensHealthReport.status == "shared"
    ).first()
    
    if existing_report:
        existing_report.status = "expired"
        existing_report.expires_at = datetime.now()
        db.commit()
    
    report = MensHealthReport(
        patient_id=patient_id,
        doctor_id=current_user.id,
        organization_id=org.id,
        report_type="compatibility",
        length_cm=length_cm,
        girth_cm=girth_cm,
        compatibility_data=compatibility_data,
        status="draft"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    report.status = "shared"
    report.shared_at = datetime.now()
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='CREATE',
        resource_type='MENS_HEALTH_REPORT',
        resource_id=report.id,
        patient_id=patient_id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={
            "report_type": "compatibility",
            "status": "shared",
            "length_cm": length_cm
        }
    )
    
    return {
        "message": "Report shared with patient",
        "report_id": report.id,
        "status": report.status
    }


@router.get("/reports/pending")
def get_pending_report(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Patient checks if there's a new report waiting"""
    
    report = db.query(MensHealthReport).filter(
        MensHealthReport.patient_id == current_user.id,
        MensHealthReport.status == "shared",
        MensHealthReport.organization_id == org.id
    ).first()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='MENS_HEALTH_REPORT',
        patient_id=current_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    if not report:
        return {
            "has_report": False,
            "report_id": None,
            "report_type": None,
            "shared_at": None
        }
    
    return {
        "has_report": True,
        "report_id": report.id,
        "report_type": report.report_type,
        "shared_at": report.shared_at
    }


@router.get("/reports/{report_id}")
def get_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Patient views their report"""
    
    report = db.query(MensHealthReport).filter(
        MensHealthReport.id == report_id,
        MensHealthReport.patient_id == current_user.id,
        MensHealthReport.organization_id == org.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status == "expired":
        raise HTTPException(status_code=410, detail="Report has expired")
    
    if report.status == "draft":
        raise HTTPException(status_code=403, detail="Report not yet shared")
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='MENS_HEALTH_REPORT',
        resource_id=report.id,
        patient_id=current_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "id": report.id,
        "report_type": report.report_type,
        "status": report.status,
        "length_cm": report.length_cm,
        "girth_cm": report.girth_cm,
        "compatibility_data": report.compatibility_data,
        "shared_at": report.shared_at,
        "viewed_at": report.viewed_at,
        "created_at": report.created_at
    }


@router.put("/reports/{report_id}/mark-read")
def mark_report_read(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Patient marks report as read"""
    
    report = db.query(MensHealthReport).filter(
        MensHealthReport.id == report_id,
        MensHealthReport.patient_id == current_user.id,
        MensHealthReport.organization_id == org.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status == "viewed":
        return {"message": "Report already marked as read"}
    
    report.status = "viewed"
    report.viewed_at = datetime.now()
    db.commit()
    
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='UPDATE',
        resource_type='MENS_HEALTH_REPORT',
        resource_id=report.id,
        patient_id=current_user.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"status": "viewed"}
    )
    
    return {"message": "Report marked as read", "status": report.status}    




@router.post("/calibrate")
async def calibrate_grid(
    file: UploadFile = File(...),
    card_type: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """
    Calibrate using 1 Birr coin detection.
    Returns pixels per cm for accurate measurement.
    """
    try:
        # Save the image temporarily
        upload_dir = f"uploads/calibration/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Known size of 1 Birr coin in cm (approximate diameter)
        COIN_SIZE_CM = 2.8
        
        # Read image with OpenCV
        img = cv2.imread(file_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect circles (coin) using Hough Circle Transform
        circles = cv2.HoughCircles(
            gray, 
            cv2.HOUGH_GRADIENT, 
            dp=1, 
            minDist=50,
            param1=50, 
            param2=30, 
            minRadius=20, 
            maxRadius=150
        )
        
        grid_size_pixels = None
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            # Use the first detected circle
            (x, y, r) = circles[0]
            diameter_pixels = r * 2
            grid_size_pixels = diameter_pixels / COIN_SIZE_CM
            print(f"✅ Coin detected: diameter = {diameter_pixels} pixels, {grid_size_pixels} px/cm")
        else:
            # Fallback: try alternative detection method
            print("⚠️ No circle detected, trying alternative detection...")
            
            # Try using edge detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find circular contours
            for contour in contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.7:  # Good circle approximation
                        (x, y), radius = cv2.minEnclosingCircle(contour)
                        if 20 < radius < 150:  # Reasonable coin size
                            diameter_pixels = radius * 2
                            grid_size_pixels = diameter_pixels / COIN_SIZE_CM
                            print(f"✅ Coin detected via contour: {grid_size_pixels} px/cm")
                            break
        
        # If still no detection, use default
        if grid_size_pixels is None or grid_size_pixels <= 0:
            print("⚠️ Coin not detected, using default calibration")
            grid_size_pixels = 50.0  # Default fallback
        
        # Save calibration to database
        calibration = MensHealthCalibration(
            patient_id=current_user.id,
            organization_id=org.id,
            grid_size_pixels=grid_size_pixels,
            card_type=card_type,
            is_active=True
        )
        db.add(calibration)
        db.commit()
        db.refresh(calibration)
        
        # Delete inactive calibrations for this patient
        db.query(MensHealthCalibration).filter(
            MensHealthCalibration.patient_id == current_user.id,
            MensHealthCalibration.id != calibration.id
        ).update({"is_active": False})
        db.commit()
        
        # Audit log
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            action='CREATE',
            resource_type='MENS_HEALTH_CALIBRATION',
            resource_id=calibration.id,
            patient_id=current_user.id,
            status='success',
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None,
            new_value={"grid_size_pixels": grid_size_pixels, "card_type": card_type}
        )
        
        return {
            "success": True,
            "grid_size_pixels": grid_size_pixels,
            "message": "Calibration successful"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Calibration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calibration error: {str(e)}")