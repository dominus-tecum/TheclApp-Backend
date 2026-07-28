from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums for consistent data
class ActivityLevel(str, Enum):
    BED_REST = "bed_rest"
    LIGHT = "light"
    NORMAL = "normal"
    ACTIVE = "active"

class UrineOutput(str, Enum):
    LESS = "less"
    NORMAL = "normal"
    MORE = "more"

class ConditionType(str, Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    HEART = "heart"
    CANCER = "cancer"
    KIDNEY = "kidney"

class EntryStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"

# Medication sub-schema
class MedicationData(BaseModel):
    morning: bool = False
    afternoon: bool = False
    evening: bool = False
    side_effects: str = ""

# Symptoms sub-schema
class SymptomData(BaseModel):
    fatigue: bool = False
    nausea: bool = False
    breathing_issues: bool = False
    pain: bool = False
    swelling: bool = False
    other: str = ""

# Common data schema (used by all conditions)
class CommonData(BaseModel):
    pain_level: int = Field(ge=0, le=10, default=5)
    energy_level: int = Field(ge=0, le=10, default=5)
    sleep_hours: int = Field(ge=0, le=24, default=7)
    sleep_quality: int = Field(ge=1, le=5, default=3)
    activity_level: ActivityLevel = ActivityLevel.NORMAL
    medications: MedicationData = MedicationData()
    symptoms: SymptomData = SymptomData()
    notes: str = ""

# Condition-specific data schema
class ConditionSpecificData(BaseModel):
    selected_condition: Optional[ConditionType] = None
    
    # Diabetes
    blood_glucose: Optional[str] = None
    
    # Hypertension
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    
    # Heart Disease
    heart_weight: Optional[str] = None
    heart_swelling: Optional[int] = Field(ge=0, le=3, default=None)
    heart_breathing: Optional[int] = Field(ge=0, le=10, default=None)
    
    # Cancer
    cancer_side_effects: Optional[int] = Field(ge=0, le=10, default=None)
    
    # Kidney Disease
    kidney_weight: Optional[str] = None
    kidney_swelling: Optional[int] = Field(ge=0, le=3, default=None)
    kidney_urine_output: Optional[UrineOutput] = None
    kidney_fluid_intake: Optional[str] = None

# Main progress entry schemas
class ProgressEntryBase(BaseModel):
    common_data: CommonData
    condition_data: ConditionSpecificData
    status: EntryStatus = EntryStatus.DRAFT

class ProgressEntryCreate(ProgressEntryBase):
    pass

class ProgressEntryUpdate(BaseModel):
    common_data: Optional[CommonData] = None
    condition_data: Optional[ConditionSpecificData] = None
    status: Optional[EntryStatus] = None

class ProgressEntryResponse(ProgressEntryBase):
    id: int
    patient_id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    compliance_rate: float
    streak_days: int
    last_submission: Optional[datetime] = None
    pending_reviews: int
    condition_summary: list[str]

class RecentEntry(BaseModel):
    id: int
    date: datetime
    status: EntryStatus
    reviewed: bool