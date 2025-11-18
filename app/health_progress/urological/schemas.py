from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Common Data Model - snake_case
class CommonData(BaseModel):
    temperature: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    heart_rate: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    pain_level: int = 0

# Condition Data Model - snake_case  
class ConditionData(BaseModel):
    selected_condition: str
    urine_output: Optional[str] = None
    urine_color: str
    urine_clarity: str
    urine_odor: str
    urine_debris: str
    has_catheter: bool = False
    catheter_patency: Optional[str] = None
    catheter_drainage: Optional[str] = None
    has_drain: bool = False
    drain_output: Optional[str] = None
    drain_color: Optional[str] = None
    drain_consistency: Optional[str] = None
    insertion_site: Optional[str] = None
    wound_condition: Optional[str] = None
    wound_discharge_type: Optional[str] = None
    wound_tenderness: Optional[str] = None
    dressing_condition: Optional[str] = None
    nausea_level: str
    vomiting_episodes: int = 0
    abdominal_distension: str
    bowel_sounds: str
    flatus_passed: bool = False
    bowel_movement: bool = False
    oral_intake: Optional[str] = None
    iv_intake: Optional[str] = None
    total_intake: Optional[str] = None
    fluid_balance: Optional[str] = None
    creatinine_level: Optional[str] = None
    hydration_status: str
    additional_notes: Optional[str] = None
    status: str

# Create Request Model - snake_case with nested structure
class UrologicalEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    surgery_type: str
    submission_date: str
    common_data: CommonData
    condition_data: ConditionData

    class Config:
        from_attributes = True

# Response Model
class UrologicalEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    surgery_type: str
    submission_date: str
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True