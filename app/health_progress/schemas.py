from pydantic import BaseModel, field_validator, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class EntryStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"

class SurgeryType(str, Enum):
    ORTHOPEDIC = "orthopedic"
    CARDIAC = "cardiac"
    GYNECOLOGIC = "gynecologic"
    ABDOMINAL = "abdominal"
    BARIATRIC = "bariatric"
    CESAREAN = "cesarean"
    UROLOGICAL = "urological"
    BURN_CARE = "burn_care"
    CHRONIC = "chronic"
    GENERAL_HEALTH = "general_health"

class HealthTrend(str, Enum):
    SIGNIFICANTLY_WORSE = "significantly_worse"
    SLIGHTLY_WORSE = "slightly_worse"
    STABLE = "stable"
    SLIGHTLY_BETTER = "slightly_better"
    SIGNIFICANTLY_BETTER = "significantly_better"
    VARIES = "varies"

# For surgery-specific trackers
class ProgressEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    surgery_type: SurgeryType
    submission_date: str
    
    # Common data structure that matches your existing model
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    
    # Use the proper enum for status
    status: EntryStatus = EntryStatus.SUBMITTED
    notes: Optional[str] = None
    surgery_date: Optional[str] = None
    day_post_op: Optional[int] = None

# For general health tracker (matches your frontend structure)
class DailyHealthEntryCreate(BaseModel):
    patientId: str  # Note: string type from your frontend
    patientName: str
    conditionType: str = "general_health"
    submissionDate: str
    submittedAt: str
    status: str  # Keep as string for general health to match frontend
    
    # Health data from your frontend
    healthTrend: HealthTrend
    overallWellbeing: int
    primarySymptom: Dict[str, Any]
    notes: str

class ProgressEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    patient_id: int
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    status: str
    submitted_at: Optional[datetime] = None
    created_at: datetime  # CHANGED: Removed Optional - this should never be None
    updated_at: datetime  # CHANGED: Removed Optional - this should never be None
    
    # Additional fields for frontend compatibility
    patient_name: Optional[str] = None
    surgery_type: Optional[str] = None
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def validate_updated_at(cls, v):
        """Ensure updated_at is never None"""
        if v is None:
            raise ValueError("updated_at cannot be None. Check database defaults.")
        return v
    
    @field_validator('created_at', mode='before')
    @classmethod
    def validate_created_at(cls, v):
        """Ensure created_at is never None"""
        if v is None:
            raise ValueError("created_at cannot be None. Check database defaults.")
        return v

class DailyHealthEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    patient_id: int
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    status: str
    submitted_at: Optional[datetime] = None
    created_at: datetime  # CHANGED: Removed Optional
    
    @field_validator('created_at', mode='before')
    @classmethod
    def validate_created_at(cls, v):
        """Ensure created_at is never None"""
        if v is None:
            raise ValueError("created_at cannot be None. Check database defaults.")
        return v

class DashboardStats(BaseModel):
    total_entries: int
    urgent_entries: int
    surgery_type_stats: Dict[str, int]

class PatientConditionsResponse(BaseModel):
    patient_id: int
    patient_name: str
    conditions: List[str]
    recent_progress: List[ProgressEntryResponse]