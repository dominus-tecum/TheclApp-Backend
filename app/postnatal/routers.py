from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.postnatal.models import PostnatalEntry, PostnatalProfile
from app.postnatal.schemas import PostnatalCreate, PostnatalResponse, PostnatalCheckResponse, PostnatalProfileCreate, PostnatalProfileResponse
from app.postnatal.services import PostnatalService

router = APIRouter()

@router.post("/profile", response_model=PostnatalProfileResponse)
async def create_postnatal_profile(
    profile: PostnatalProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create postnatal profile - accept frontend data as-is
    """
    print("🚨 Received postnatal profile:", profile.dict())
    result = PostnatalService.create_or_update_profile(db=db, patient_id=profile.patient_id, profile_data=profile)
    print("🚨 Profile saved with ID:", result.id)
    return result

@router.get("/profile", response_model=PostnatalProfileResponse)
async def get_postnatal_profile(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get postnatal profile for current user
    """
    profile = PostnatalService.get_profile(db, patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/entries", response_model=PostnatalResponse)
async def create_postnatal_entry(
    entry: PostnatalCreate,
    db: Session = Depends(get_db)
):
    """
    Create postnatal entry - accept frontend data as-is
    """
    print("🚨 Received postnatal entry:", entry.dict())
    result = PostnatalService.create_postnatal_entry(db=db, entry=entry)
    print("🚨 Entry saved with ID:", result.id)
    return result

@router.get("/entries/{patient_id}/{date}", response_model=PostnatalCheckResponse)
async def check_existing_entry(
    patient_id: str,
    date: date,
    db: Session = Depends(get_db)
):
    """
    Check if postnatal entry exists for specific patient and date
    """
    existing_entry = PostnatalService.check_existing_entry(db, patient_id, date)
    return PostnatalCheckResponse(
        exists=existing_entry is not None,
        entry_id=existing_entry.id if existing_entry else None
    )

@router.get("/entries")
async def get_all_postnatal_entries(db: Session = Depends(get_db)):
    """
    Get ALL postnatal entries for dashboard
    """
    try:
        entries = PostnatalService.get_all_postnatal_entries(db)
        
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
                
                # ALL POSTNATAL DATA FIELDS:
                "lochia_flow": entry.lochia_flow,
                "lochia_color": entry.lochia_color,
                "perineal_pain": entry.perineal_pain,
                "uterine_pain": entry.uterine_pain,
                "breast_engorgement": entry.breast_engorgement,
                "nipple_pain": entry.nipple_pain,
                "c_section_pain": entry.c_section_pain,
                "incision_redness": entry.incision_redness,
                "incision_discharge": entry.incision_discharge,
                "maternal_temperature": entry.maternal_temperature,
                "blood_pressure_systolic": entry.blood_pressure_systolic,
                "blood_pressure_diastolic": entry.blood_pressure_diastolic,
                "maternal_heart_rate": entry.maternal_heart_rate,
                "mood_laugh": entry.mood_laugh,
                "mood_anxious": entry.mood_anxious,
                "mood_blame": entry.mood_blame,
                "mood_panic": entry.mood_panic,
                "mood_sleep": entry.mood_sleep,
                "mood_sad": entry.mood_sad,
                "mood_crying": entry.mood_crying,
                "mood_harm": entry.mood_harm,
                "feeding_method": entry.feeding_method,
                "feeding_frequency": entry.feeding_frequency,
                "feeding_duration": entry.feeding_duration,
                "latching_quality": entry.latching_quality,
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
                "maternal_energy": entry.maternal_energy,
                "support_system": entry.support_system,
                "additional_notes": entry.additional_notes
            })
        
        return {
            "entries": formatted_entries,
            "total": len(entries),
            "condition_type": "postnatal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving postnatal entries: {str(e)}")