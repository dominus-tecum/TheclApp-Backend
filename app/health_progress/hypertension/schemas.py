# app/health_progress/hypertension/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class HypertensionEntryCreate(BaseModel):
    # ✅ PERFECTLY MATCHES FRONTEND - ALL SNAKE_CASE
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    submission_date: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    condition_type: Optional[str] = "hypertension"

    class Config:
        extra = "allow"  # Accept any extra fields
        from_attributes = True

class HypertensionEntryResponse(BaseModel):
    # ✅ FLAT FIELDS FOR RESPONSE TOO
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    condition_type: Optional[str] = "hypertension"
    created_at: Optional[str] = None

    class Config:
        from_attributes = True