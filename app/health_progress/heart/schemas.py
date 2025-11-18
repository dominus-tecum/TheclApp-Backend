# app/health_progress/heart/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class HeartEntryCreate(BaseModel):
    # ✅ PERFECTLY MATCHES FRONTEND - ALL SNAKE_CASE
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    submission_date: Optional[str] = None
    
    # Common data - SNAKE_CASE
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    
    # Heart Disease-specific fields - SNAKE_CASE
    chest_pain_level: Optional[int] = None
    pain_location: Optional[str] = None
    weight: Optional[str] = None
    swelling_level: Optional[int] = None
    breathing_difficulty: Optional[int] = None
    condition_type: Optional[str] = "heart"

    class Config:
        extra = "allow"  # ✅ ACCEPT ANY EXTRA FIELDS
        from_attributes = True

class HeartEntryResponse(BaseModel):
    # ✅ FLAT FIELDS FOR RESPONSE TOO
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    
    # Common flat fields
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    
    # Heart-specific flat fields
    chest_pain_level: Optional[int] = None
    pain_location: Optional[str] = None
    weight: Optional[str] = None
    swelling_level: Optional[int] = None
    breathing_difficulty: Optional[int] = None
    condition_type: Optional[str] = "heart"
    created_at: Optional[str] = None

    class Config:
        from_attributes = True