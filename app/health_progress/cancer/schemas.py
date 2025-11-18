from pydantic import BaseModel
from typing import Optional, Dict, Any

class CancerEntryCreate(BaseModel):
    # ✅ Basic info - MATCH frontend exactly
    patient_id: int
    patient_name: str
    submission_date: str
    status: Optional[str] = None
    
    # ✅ Common data - MATCH frontend types
    blood_pressure_systolic: Optional[str] = None  # Frontend sends string
    blood_pressure_diastolic: Optional[str] = None # Frontend sends string
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None              # Frontend sends float
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None   # Frontend sends object
    symptoms: Optional[Dict[str, Any]] = None      # Frontend sends object
    notes: Optional[str] = None
    
    # ✅ Cancer-specific fields
    pain_level: Optional[int] = None
    pain_location: Optional[str] = None
    side_effects: Optional[int] = None
    
    # ✅ Condition type
    condition_type: Optional[str] = "cancer"
    
    # Optional fields
    urgency_status: Optional[str] = None

    class Config:
        from_attributes = True
        extra = "allow"

class CancerEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    status: Optional[str] = None
    
    # ✅ Common data
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = None
    symptoms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    # ✅ Cancer-specific fields
    pain_level: Optional[int] = None
    pain_location: Optional[str] = None
    side_effects: Optional[int] = None
    
    # ✅ Condition type
    condition_type: Optional[str] = "cancer"
    
    # Timestamps
    submitted_at: Optional[str] = None
    urgency_status: Optional[str] = None

    class Config:
        from_attributes = True