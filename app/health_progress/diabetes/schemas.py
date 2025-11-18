# app/health_progress/diabetes/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class DiabetesEntryCreate(BaseModel):
    # ACCEPT EXACTLY what frontend sends - ALL FIELDS OPTIONAL
    patientId: Optional[int] = None
    patientName: Optional[str] = None
    submissionDate: Optional[str] = None
    
    # Common data
    bloodPressureSystolic: Optional[str] = None
    bloodPressureDiastolic: Optional[str] = None
    energyLevel: Optional[int] = None
    sleepHours: Optional[float] = None
    sleepQuality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    # Diabetes-specific
    bloodGlucose: Optional[str] = None
    carbsConsumed: Optional[str] = None
    insulinDose: Optional[str] = None
    activityLevel: Optional[str] = None
    status: Optional[str] = None
    
    # ANY other fields frontend might send
    weight: Optional[str] = None
    swellingLevel: Optional[int] = None
    painLevel: Optional[int] = None
    
    # ✅ ADD THIS LINE
    condition_type: Optional[str] = "diabetes"

    class Config:
        extra = "allow"  # ✅ ACCEPT ANY EXTRA FIELDS

class DiabetesEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    created_at: Optional[str] = None
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    # ✅ ADD THIS LINE
    condition_type: Optional[str] = "diabetes"

    class Config:
        allow_population_by_field_name = True