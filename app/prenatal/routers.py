from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.prenatal.models import PrenatalEntry
from app.prenatal.schemas import PrenatalCreate, PrenatalResponse, PrenatalCheckResponse
from app.prenatal.services import PrenatalService

router = APIRouter()

@router.post("/entries", response_model=PrenatalResponse)
async def create_prenatal_entry(
    entry: PrenatalCreate,
    db: Session = Depends(get_db)
):
    """
    Create prenatal entry - accept frontend data as-is
    """
    print("🚨 Received prenatal entry:", entry.dict())
    result = PrenatalService.create_prenatal_entry(db=db, entry=entry)
    print("🚨 Entry saved with ID:", result.id)
    return result

@router.get("/entries/{patient_id}/{date}", response_model=PrenatalCheckResponse)
async def check_existing_entry(
    patient_id: str,
    date: date,
    db: Session = Depends(get_db)
):
    """
    Check if prenatal entry exists for specific patient and date
    """
    existing_entry = PrenatalService.check_existing_entry(db, patient_id, date)
    return PrenatalCheckResponse(
        exists=existing_entry is not None,
        entry_id=existing_entry.id if existing_entry else None
    )

@router.get("/entries")
async def get_all_prenatal_entries(db: Session = Depends(get_db)):
    """
    Get ALL prenatal entries for dashboard
    """
    try:
        entries = PrenatalService.get_all_prenatal_entries(db)
        
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
                
                # ALL PRENATAL DATA FIELDS:
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
    db: Session = Depends(get_db)
):
    """
    Get all prenatal entries for a specific patient
    """
    try:
        entries = db.query(PrenatalEntry).filter(
            PrenatalEntry.patient_id == patient_id
        ).all()
        
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
                
                # ALL PRENATAL DATA FIELDS:
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
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient entries: {str(e)}")