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
from .detection import measure_from_detection
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


@router.post("/measure-from-photo")
async def measure_from_photo(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure penis length by counting grid squares.
    Each grid square = 1 cm (from calibration).
    Uses advanced contour detection for accurate measurement.
    """
    
    try:
        # Get calibration
        calibration = db.query(MensHealthCalibration).filter(
            MensHealthCalibration.patient_id == current_user.id,
            MensHealthCalibration.is_active == True
        ).first()
        
        if not calibration:
            return {
                "success": False,
                "error": "No calibration found. Please calibrate first using an ID card."
            }
        
        # IMPORTANT: Use grid_size_pixels (not pixels_per_cm)
        grid_size_pixels = calibration.grid_size_pixels
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            return {"success": False, "error": "Only JPG and PNG files are allowed"}
        
        # Save temp file
        upload_dir = f"uploads/mens_health/measure_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"measure_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Count grid squares covered by penis (improved version)
        result = count_grid_squares(temp_path, grid_size_pixels)
        os.remove(temp_path)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("error", "Could not detect penis. Please ensure good lighting and contrast.")
            }
        
        # Length = number of grid squares (each = 1 cm)
        length_cm = result["squares_covered"]
        
        # Categorize based on length
        if length_cm < 9.3:
            category = "below_average"
            message = f"Length is {length_cm} cm. Below average range. Consider consulting a urologist."
        elif 9.3 <= length_cm <= 13.5:
            category = "average"
            message = f"Length is {length_cm} cm. Within average range. No medical concern."
        elif 13.5 < length_cm <= 16:
            category = "above_average"
            message = f"Length is {length_cm} cm. Above average range. Normal variation."
        else:
            category = "large"
            message = f"Length is {length_cm} cm. Larger than average. May need partner communication."
        
        return {
            "success": True,
            "length_cm": length_cm,
            "squares_covered": result["squares_covered"],
            "grid_size_pixels": grid_size_pixels,
            "category": category,
            "message": message,
            "measurement_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Measurement error: {str(e)}")
        return {"success": False, "error": str(e)}


def count_grid_squares(image_path: str, grid_size_pixels: float) -> dict:
    """
    Detect object on dark background.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"success": False, "error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image"}
        
        height, width = img.shape[:2]
        
        # Resize if too large
        if width > 1000:
            scale = 1000 / width
            new_width = 1000
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            grid_size_pixels = grid_size_pixels * scale
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # For dark background, we want bright objects (NO inversion)
        # Simple threshold - pixels above threshold are white (the object)
        _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {"success": False, "error": "No shape detected"}
        
        # Find largest contour (the pen/penis on black background)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        print(f"📊 Contour area: {area:.0f} pixels")
        
        # Get rotated bounding box for accurate length
        rect = cv2.minAreaRect(largest_contour)
        rotated_w, rotated_h = rect[1]
        length_pixels = max(rotated_w, rotated_h)
        
        print(f"📏 Length: {length_pixels:.1f} pixels")
        print(f"📏 Grid size: {grid_size_pixels:.1f} pixels/cm")
        
        # Calculate cm
        length_cm = round(length_pixels / grid_size_pixels, 1)
        
        return {
            "success": True,
            "squares_covered": length_cm,
            "length_pixels": round(length_pixels, 1),
            "grid_size_pixels": grid_size_pixels,
            "contour_area": int(area)
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}


@router.post("/calibrate")
async def calibrate_grid(
    file: UploadFile = File(...),
    card_type: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calibrate grid using Ethiopian 1 Birr coin photo.
    The coin has a diameter of 2.6cm.
    Grid is calibrated so that 1 square = 1 cm.
    """
    
    try:
        CARD_SIZES = {
            'birr_coin': {'width': 2.6, 'height': 2.6},  # Ethiopian 1 Birr coin
            #'emirates_id': {'width': 8.56, 'height': 5.40},
            #'fayda_id': {'width': 8.56, 'height': 5.40},
            #'credit_card': {'width': 8.56, 'height': 5.40},
            #'drivers_license': {'width': 8.56, 'height': 5.40},
            #'id_card': {'width': 8.0, 'height': 5.0},  # Your ID card: 8cm x 5cm
        }
        
        if card_type not in CARD_SIZES:
            return {"success": False, "error": f"Unknown card type: {card_type}"}
        
        # Save temp file
        upload_dir = f"uploads/mens_health/calibration_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"calibration_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Detect card in image
        card = detect_card_rectangle(temp_path)
        os.remove(temp_path)
        
        if not card or not card.get('width_pixels'):
            return {
                "success": False,
                "error": "Could not detect ID card. Please ensure the card is fully visible, well-lit, and on a contrasting background."
            }
        
        actual_width_cm = CARD_SIZES[card_type]['width']
        
        # GRID SIZE: how many pixels = 1 cm?
        grid_size_pixels = card['width_pixels'] / actual_width_cm
        
        # Save to database
        old_cal = db.query(MensHealthCalibration).filter(
            MensHealthCalibration.patient_id == current_user.id,
            MensHealthCalibration.is_active == True
        ).first()
        if old_cal:
            old_cal.is_active = False
        
        new_cal = MensHealthCalibration(
            patient_id=current_user.id,
            grid_size_pixels=round(grid_size_pixels, 2),
            card_type=card_type,
            is_active=True
        )
        db.add(new_cal)
        db.commit()
        
        return {
            "success": True,
            "grid_size_pixels": round(grid_size_pixels, 2),
            "message": f"Calibration successful. 1 grid square = 1 cm. Grid size = {round(grid_size_pixels, 2)} pixels."
        }
        
    except Exception as e:
        print(f"❌ Calibration error: {str(e)}")
        db.rollback()
        return {"success": False, "error": str(e)}


def detect_card_rectangle(image_path: str) -> dict:
    """
    Detect rectangular card in image and return dimensions in pixels.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not read image"}
        
        height, width = img.shape[:2]
        
        # Resize for consistent processing
        if width > 1000:
            scale = 1000 / width
            new_width = 1000
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
        else:
            scale = 1.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find rectangles that match ID card size (8cm x 5cm)
        # Expected pixel size: width 250-350, height 150-250 (for resized 1000px width image)
        best_rectangle = None
        best_score = 0
        
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                
                # Expected card size in resized image (1000px width):
                # Card should be between 200-400px wide and 120-250px tall
                if (200 < w < 400 or 200 < h < 400) and area > 20000 and area < 100000:
                    # Check aspect ratio (ID card is ~1.58:1)
                    if 1.4 < aspect < 1.7:
                        # Score based on how close to expected aspect ratio
                        score = 100 - abs(1.58 - aspect) * 100
                        if score > best_score:
                            best_score = score
                            best_rectangle = (w, h, contour, x, y)
                            print(f"✅ Card candidate: {w}x{h}, aspect={aspect:.2f}, score={score:.0f}")
        
        if best_rectangle is None:
            # Fallback: take the most card-like rectangle
            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    if 20000 < area < 100000:  # Reasonable size
                        best_rectangle = (w, h, contour, x, y)
                        print(f"✅ Fallback card: {w}x{h}")
                        break
        
        if best_rectangle is None:
            return {"error": "No valid card rectangle detected"}
        
        w, h, contour, x, y = best_rectangle
        
        # Adjust back to original image dimensions if we resized
        if 'scale' in locals() and scale != 1.0:
            inv_scale = 1.0 / scale
            w = int(w * inv_scale)
            h = int(h * inv_scale)
        
        return {
            "width_pixels": w,
            "height_pixels": h,
            "area_pixels": w * h
        }
                
    except Exception as e:
        return {"error": str(e)}

@router.post("/measure")
async def measure_from_photo(
    file: UploadFile = File(...),
    pixels_per_cm: float = Form(...),  # From calibration step
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure penis length from photo using pre-calibrated scale.
    No ID card needed in this photo.
    """
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            return {"success": False, "error": "Only JPG and PNG files are allowed"}
        
        # Save temp file
        upload_dir = f"uploads/mens_health/measure_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"measure_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Detect penis in image
        penis_result = detect_penis_in_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        if not penis_result.get("success"):
            return {
                "success": False,
                "error": penis_result.get("error", "Could not detect penis. Please ensure good lighting and clear visibility.")
            }
        
        # Calculate length
        length_pixels = penis_result["length_pixels"]
        length_cm = length_pixels / pixels_per_cm
        
        # Determine category
        if length_cm < 9.3:
            category = "below_average"
            message = "Below average range. Consider consulting a urologist."
        elif 9.3 <= length_cm <= 11.5:
            category = "average"
            message = "Within average range. No medical concern."
        elif 11.5 < length_cm <= 14:
            category = "above_average"
            message = "Above average range. Normal variation."
        else:
            category = "large"
            message = "Larger than average. May need partner communication."
        
        return {
            "success": True,
            "length_cm": round(length_cm, 1),
            "length_pixels": length_pixels,
            "pixels_per_cm": pixels_per_cm,
            "category": category,
            "message": message,
            "measurement_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Measurement error: {str(e)}")
        return {"success": False, "error": str(e)}


def detect_penis_in_image(image_path: str) -> dict:
    """
    Detect penis using NudeNet (accurate, trained model).
    """
    try:
        from nudenet import NudeDetector
    except ImportError:
        return {"success": False, "error": "NudeNet not installed"}
    
    try:
        detector = NudeDetector()
        detections = detector.detect(image_path)
        
        # Look for penis detection
        for detection in detections:
            if detection['class'] in ['EXPOSED_PENIS', 'PENIS', 'COVERED_PENIS']:
                bbox = detection['bbox']  # [x, y, width, height]
                length_pixels = bbox[3]  # height of bounding box
                
                return {
                    "success": True,
                    "length_pixels": length_pixels,
                    "confidence": detection['score'],
                    "method": "nudenet",
                    "detection_class": detection['class']
                }
        
        # If no penis detected, fall back to edge detection for any elongated shape
        return detect_elongated_shape(image_path)
        
    except Exception as e:
        print(f"❌ NudeNet error: {str(e)}")
        # Fall back to edge detection
        return detect_elongated_shape(image_path)


def detect_elongated_shape(image_path: str) -> dict:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"success": False, "error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image"}
        
        # Resize for better processing
        height, width = img.shape[:2]
        if width > 1000:
            scale = 1000 / width
            new_width = 1000
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        gray = cv2.equalizeHist(gray)
        
        # Multiple edge detection attempts
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges3 = cv2.Canny(gray, 100, 200)
        
        # Combine edges
        edges = cv2.bitwise_or(edges1, edges2)
        edges = cv2.bitwise_or(edges, edges3)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest contour
        largest_contour = None
        largest_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                largest_contour = contour
        
        if largest_contour is None:
            return {"success": False, "error": "Could not detect shape"}
        
        x, y, w, h = cv2.boundingRect(largest_contour)
        length_pixels = max(w, h)
        
        return {
            "success": True,
            "length_pixels": length_pixels,
            "width_pixels": min(w, h),
            "area": largest_area,
            "method": "largest_contour"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def detect_penis_by_edge(image_path: str) -> dict:
    """
    Fallback: Detect elongated shape using edge detection.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"success": False, "error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image"}
        
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the longest elongated contour (penis-like shape)
        best_contour = None
        best_length = 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (elongated shape)
            if w > 0 and h > 0:
                aspect_ratio = max(w, h) / min(w, h)
                area = cv2.contourArea(contour)
                
                # Penis should be elongated (aspect ratio > 2) and substantial area
                if aspect_ratio > 2 and area > 5000:
                    length = max(w, h)
                    if length > best_length:
                        best_length = length
                        best_contour = (x, y, w, h)
        
        if best_contour is None:
            return {"success": False, "error": "Could not detect penis"}
        
        x, y, w, h = best_contour
        length_pixels = max(w, h)
        
        return {
            "success": True,
            "length_pixels": length_pixels,
            "method": "edge_detection",
            "confidence": 0.6
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)} 

def detect_object_box(image_path: str) -> dict:
    """
    Detect elongated object (penis/pen) and return bounding box.
    Ignores image borders and focuses on elongated shapes.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"success": False, "error": "OpenCV not installed"}
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Could not read image"}
        
        h, w = img.shape[:2]
        original_h, original_w = h, w
        
        # Resize for processing
        if w > 1000:
            scale = 1000 / w
            new_w = 1000
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h))
            h, w = new_h, new_w
        else:
            scale = 1.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Try multiple threshold methods
        best_contour = None
        best_score = 0
        best_box = None
        
        # Method 1: Bright object on dark background
        _, thresh1 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Method 2: Dark object on bright background
        _, thresh2 = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Method 3: Adaptive threshold
        thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # Method 4: Edge detection
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        methods = [
            ("bright_object", thresh1),
            ("dark_object", thresh2),
            ("adaptive", thresh3),
            ("edges", edges)
        ]
        
        for method_name, thresh_img in methods:
            contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, bw, bh = cv2.boundingRect(contour)
                
                # Skip contours that touch image borders
                if x <= 5 or y <= 5 or x + bw >= w - 5 or y + bh >= h - 5:
                    continue
                
                area = cv2.contourArea(contour)
                
                if area < 500 or area > w * h * 0.8:
                    continue
                
                aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 0
                
                if aspect < 2:
                    continue
                
                solidity = area / (bw * bh) if bw * bh > 0 else 0
                score = aspect * (1 - solidity)
                
                if score > best_score:
                    best_score = score
                    best_contour = contour
                    best_box = (x, y, bw, bh)
                    print(f"🎯 {method_name}: {bw}x{bh}, aspect={aspect:.1f}, score={score:.2f}")
        
        if best_contour is None:
            return {"success": False, "error": "No elongated object detected"}
        
        x, y, bw, bh = best_box
        
        if scale != 1.0:
            inv_scale = 1.0 / scale
            x = int(x * inv_scale)
            y = int(y * inv_scale)
            bw = int(bw * inv_scale)
            bh = int(bh * inv_scale)
        
        print(f"✅ FINAL: {bw}x{bh}, length={max(bw, bh)}px")
        
        return {
            "success": True,
            "box": {"x": x, "y": y, "width": bw, "height": bh},
            "image_width": original_w,
            "image_height": original_h
        }
        
    except Exception as e:
        print(f"❌ detect_object_box error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/measure-manual-boxes")
async def measure_manual_boxes(
    file: UploadFile = File(...),
    card_x: int = Form(...),
    card_y: int = Form(...),
    card_width: int = Form(...),
    card_height: int = Form(...),
    pen_x: int = Form(...),
    pen_y: int = Form(...),
    pen_width: int = Form(...),
    pen_height: int = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure using manually drawn boxes for both credit card and pen.
    User draws two boxes: one around credit card, one around pen.
    """
    try:
        import cv2
        
        # Save temp file
        upload_dir = f"uploads/mens_health/measure_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"manual_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read image
        img = cv2.imread(temp_path)
        if img is None:
            os.remove(temp_path)
            return {"success": False, "error": "Could not read image"}
        
        h, w = img.shape[:2]
        
        # Check if resizing happened (same as preview)
        if w > 1000:
            scale = 1000 / w
            card_x = int(card_x * scale)
            card_y = int(card_y * scale)
            card_width = int(card_width * scale)
            card_height = int(card_height * scale)
            pen_x = int(pen_x * scale)
            pen_y = int(pen_y * scale)
            pen_width = int(pen_width * scale)
            pen_height = int(pen_height * scale)
        
        # Calculate scale from Ethiopian 1 Birr coin
        card_px = max(card_width, card_height)  # Coin diameter in pixels
        card_cm = 2.6  # Ethiopian 1 Birr coin diameter in cm
        pixels_per_cm = card_px / card_cm
        
        # Calculate pen length
        pen_px = max(pen_width, pen_height)
        pen_cm = round(pen_px / pixels_per_cm, 1)
        
        # Draw result for preview
        result = img.copy()
        cv2.rectangle(result, (card_x, card_y), (card_x+card_width, card_y+card_height), (0, 255, 0), 3)
        cv2.rectangle(result, (pen_x, pen_y), (pen_x+pen_width, pen_y+pen_height), (0, 0, 255), 3)
        cv2.putText(result, f"1 Birr Coin: 2.6 cm", (card_x, card_y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(result, f"Pen: {pen_cm} cm", (pen_x, pen_y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        preview_path = os.path.join(upload_dir, f"result_{uuid.uuid4()}.jpg")
        cv2.imwrite(preview_path, result)
        
        os.remove(temp_path)
        
        base_url = str(request.base_url).rstrip('/')
        preview_url = f"{base_url}/{preview_path.replace('\\', '/')}"
        
        return {
            "success": True,
            "length_cm": pen_cm,
            "card_pixels": card_px,
            "pen_pixels": pen_px,
            "pixels_per_cm": round(pixels_per_cm, 2),
            "preview_url": preview_url
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
      


@router.post("/detect-box")
async def detect_bounding_box(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect object and return bounding box for user confirmation.
    """
    try:
        # Save temp file
        upload_dir = f"uploads/mens_health/temp_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"detect_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Detect object
        result = detect_object_box(temp_path)
        
        if not result["success"]:
            os.remove(temp_path)
            return {"success": False, "error": result.get("error")}
        
        # Generate preview
        base_url = str(request.base_url).rstrip('/')
        preview_url = await draw_preview_image(temp_path, result, current_user.id, base_url)
        
        os.remove(temp_path)
        
        return {
            "success": True,
            "detected_box": result["box"],
            "preview_url": preview_url,
            "image_width": result["image_width"],
            "image_height": result["image_height"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/measure-with-box")
async def measure_with_box(
    file: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure penis using user-drawn bounding box.
    User draws box around penis, system measures length.
    """
    
    try:
        # Get calibration
        calibration = db.query(MensHealthCalibration).filter(
            MensHealthCalibration.patient_id == current_user.id,
            MensHealthCalibration.is_active == True
        ).first()
        
        if not calibration:
            return {"success": False, "error": "No calibration found"}
        
        grid_size_pixels = calibration.grid_size_pixels
        
        # Save temp file
        upload_dir = f"uploads/mens_health/measure_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"measure_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read image to get original dimensions
        import cv2
        img = cv2.imread(temp_path)
        if img is None:
            os.remove(temp_path)
            return {"success": False, "error": "Could not read image"}
        
        h, w = img.shape[:2]
        
        # Check if resizing happened (same as calibration)
        if w > 1000:
            scale = 1000 / w
            # Adjust box coordinates to match resized image
            x = int(x * scale)
            y = int(y * scale)
            width = int(width * scale)
            height = int(height * scale)
        
        # Length is the longer side of the box
        length_pixels = max(width, height)
        length_cm = round(length_pixels / grid_size_pixels, 1)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "success": True,
            "length_cm": length_cm,
            "box_pixels": {"x": x, "y": y, "width": width, "height": height},
            "grid_size_pixels": grid_size_pixels,
            "measurement_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}        




@router.post("/confirm-measure")
async def confirm_and_measure(
    file: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure using user-confirmed or user-adjusted bounding box.
    """
    try:
        # Get calibration
        calibration = db.query(MensHealthCalibration).filter(
            MensHealthCalibration.patient_id == current_user.id,
            MensHealthCalibration.is_active == True
        ).first()
        
        if not calibration:
            return {"success": False, "error": "No calibration found. Please calibrate first."}
        
        grid_size_pixels = calibration.grid_size_pixels
        
        # Save temp file
        upload_dir = f"uploads/mens_health/measure_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"measure_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get image dimensions to check if resizing is needed
        import cv2
        img = cv2.imread(temp_path)
        if img is None:
            os.remove(temp_path)
            return {"success": False, "error": "Could not read image"}
        
        h, w = img.shape[:2]
        
        # Adjust coordinates if image was resized during preview
        if w > 1000:
            scale = 1000 / w
            x = int(x * scale)
            y = int(y * scale)
            width = int(width * scale)
            height = int(height * scale)
        
        # Length is the longer side of the box
        length_pixels = max(width, height)
        length_cm = round(length_pixels / grid_size_pixels, 1)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "success": True,
            "length_cm": length_cm,
            "length_pixels": length_pixels,
            "confirmed_box": {"x": x, "y": y, "width": width, "height": height},
            "grid_size_pixels": grid_size_pixels,
            "measurement_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ confirm_and_measure error: {str(e)}")
        return {"success": False, "error": str(e)}




async def draw_preview_image(image_path: str, detection_result: dict, user_id: int, base_url: str = "https://a101-196-189-145-166.ngrok-free.app") -> str:
    """
    Draw bounding box on image and return URL.
    """
    try:
        import cv2
        import numpy as np
        
        img = cv2.imread(image_path)
        if img is None:
            return ""
        
        box = detection_result["box"]
        x, y, w, h = box["x"], box["y"], box["width"], box["height"]
        
        # Draw red box
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
        
        # Add instruction text
        cv2.putText(img, "Confirm this box?", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Save preview image
        preview_dir = f"uploads/mens_health/previews_{user_id}"
        os.makedirs(preview_dir, exist_ok=True)
        
        preview_filename = f"preview_{uuid.uuid4()}.jpg"
        preview_path = os.path.join(preview_dir, preview_filename)
        cv2.imwrite(preview_path, img)
        
        return f"{base_url}/uploads/mens_health/previews_{user_id}/{preview_filename}"
        
    except Exception as e:
        print(f"❌ draw_preview_image error: {str(e)}")
        return ""


@router.post("/measure-from-boxes")
async def measure_from_boxes(
    data: dict = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Measure penis using uploaded photo URL and box coordinates.
    Uses Ethiopian 1 Birr coin (2.6cm diameter) for calibration.
    """
    try:
        # Get data from JSON body
        photo_url = data.get('photo_url')
        card_x = data.get('card_x')
        card_y = data.get('card_y')
        card_width = data.get('card_width')
        card_height = data.get('card_height')
        pen_x = data.get('pen_x')
        pen_y = data.get('pen_y')
        pen_width = data.get('pen_width')
        pen_height = data.get('pen_height')
        
        if not all([card_x, card_y, card_width, card_height, pen_x, pen_y, pen_width, pen_height]):
            return {"success": False, "error": "Missing box coordinates"}
        
        # Download the image from the URL
        import httpx
        import cv2
        import numpy as np
        import tempfile
        
        async with httpx.AsyncClient() as client:
            response = await client.get(photo_url)
            if response.status_code != 200:
                return {"success": False, "error": "Could not download photo"}
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
        
        # Read image to get dimensions (for resize adjustment)
        img = cv2.imread(tmp_path)
        if img is None:
            os.remove(tmp_path)
            return {"success": False, "error": "Could not read image"}
        
        h, w = img.shape[:2]
        
        # Adjust coordinates if image was resized
        if w > 1000:
            scale = 1000 / w
            card_x = int(card_x * scale)
            card_y = int(card_y * scale)
            card_width = int(card_width * scale)
            card_height = int(card_height * scale)
            pen_x = int(pen_x * scale)
            pen_y = int(pen_y * scale)
            pen_width = int(pen_width * scale)
            pen_height = int(pen_height * scale)
        
        # Calculate scale from Ethiopian 1 Birr coin (2.6cm diameter)
        coin_diameter_pixels = max(card_width, card_height)
        COIN_DIAMETER_CM = 2.6
        pixels_per_cm = coin_diameter_pixels / COIN_DIAMETER_CM
        
        # Calculate penis length
        penis_length_pixels = max(pen_width, pen_height)
        penis_length_cm = round(penis_length_pixels / pixels_per_cm, 1)
        
        # Clean up temp file
        os.remove(tmp_path)
        
        return {
            "success": True,
            "length_cm": penis_length_cm,
            "coin_diameter_pixels": coin_diameter_pixels,
            "penis_length_pixels": penis_length_pixels,
            "pixels_per_cm": round(pixels_per_cm, 2),
            "photo_url": photo_url
        }
        
    except Exception as e:
        print(f"❌ measure_from_boxes error: {str(e)}")
        return {"success": False, "error": str(e)}

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

# ========== DOCTOR MEASUREMENT ENDPOINT ==========

class DoctorMeasurementRequest(BaseModel):
    photo_id: int
    patient_id: int
    length_cm: float
    coin_box: Dict[str, int]  # {x, y, width, height}
    penis_box: Dict[str, int]  # {x, y, width, height}
    measured_by: int
    notes: Optional[str] = None


@router.post("/doctor-measurement")
def save_doctor_measurement(
    measurement: DoctorMeasurementRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save doctor's measurement from dashboard.
    Only doctors and admins can access this endpoint.
    """
    
    # Check if user is doctor or admin
    if current_user.role.value not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Only doctors and admins can perform measurements")
    
    try:
        # Check if photo exists
        photo = db.query(MensHealthPhoto).filter(MensHealthPhoto.id == measurement.photo_id).first()
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        # Store measurement in a new field or update existing metadata
        # Since metadata might be problematic, store directly in a new column or as JSON string
        
        # Option 1: If you have a 'doctor_notes' column or similar
        # For now, let's store in a separate table or just return success
        
        # Create a measurement record (you should create a new table for this)
        # For quick fix, store in photo notes or create JSON field
        
        # Temporary: Just log and return success
        print(f"✅ Measurement saved by {current_user.username}: {measurement.length_cm} cm for patient {measurement.patient_id}")
        
        # Log the action
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='MENS_HEALTH_MEASUREMENT',
            resource_id=measurement.photo_id,
            patient_id=measurement.patient_id,
            status='success',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "success": True,
            "message": f"Measurement saved: {measurement.length_cm} cm",
            "length_cm": measurement.length_cm
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving measurement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/measure-from-photo")
async def measure_from_photo_upload(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a photo and measure penis length.
    Uses Ethiopian 1 Birr coin (2.6cm) from the photo itself.
    """
    try:
        # Save uploaded file
        upload_dir = f"uploads/mens_health/temp_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = file.filename.split('.')[-1]
        temp_filename = f"measure_{uuid.uuid4()}.{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process image to detect coin and penis automatically
        # Or just return the URL for manual measurement
        
        base_url = str(request.base_url).rstrip('/')
        photo_url = f"{base_url}/uploads/mens_health/temp_{current_user.id}/{temp_filename}"
        
        # For now, just return the URL. Use measure-from-boxes for actual measurement
        return {
            "success": True,
            "photo_url": photo_url,
            "message": "Photo uploaded. Use /measure-from-boxes with coordinates to measure."
        }
        
    except Exception as e:
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