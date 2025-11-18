from pydantic import BaseModel
from typing import Optional, Dict, Any

class GeneralEntryCreate(BaseModel):
    # ✅ Basic info - MATCH frontend exactly
    patient_id: int
    patient_name: str
    submission_date: str
    status: Optional[str] = None
    
    # ✅ General health specific fields
    health_trend: Optional[str] = None
    overall_wellbeing: Optional[int] = None
    primary_symptom_severity: Optional[int] = None
    primary_symptom_description: Optional[str] = None
    notes: Optional[str] = None
    
    # ✅ Condition type
    condition_type: Optional[str] = "general_health"
    
    # Optional fields
    urgency_status: Optional[str] = None
    submitted_at: Optional[str] = None

    class Config:
        from_attributes = True
        extra = "allow"

class GeneralEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    status: Optional[str] = None
    
    # ✅ General health specific fields
    health_trend: Optional[str] = None
    overall_wellbeing: Optional[int] = None
    primary_symptom_severity: Optional[int] = None
    primary_symptom_description: Optional[str] = None
    notes: Optional[str] = None
    
    # ✅ Condition type
    condition_type: Optional[str] = "general_health"
    
    # Timestamps
    submitted_at: Optional[str] = None
    urgency_status: Optional[str] = None

    class Config:
        from_attributes = True