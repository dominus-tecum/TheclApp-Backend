# app/health_progress/orthopedic/schemas.py
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime, date

class OrthopedicCommonData(BaseModel):
    temperature: Optional[str] = ""
    blood_pressure_systolic: Optional[str] = ""
    blood_pressure_diastolic: Optional[str] = ""
    heart_rate: Optional[str] = ""
    respiratory_rate: Optional[str] = ""
    pain_level: int

class OrthopedicConditionData(BaseModel):
    # Pain and neurovascular status
    selected_condition: str
    pain_location: str
    limb_color: Literal['normal', 'pale', 'blue', 'red']
    limb_temperature: Literal['normal', 'cool', 'warm', 'hot']
    capillary_refill: Literal['normal', 'delayed', 'absent']
    limb_movement: Literal['normal', 'reduced', 'absent']
    limb_sensation: Literal['normal', 'reduced', 'numbness', 'tingling']
    distal_pulse: Literal['present', 'reduced', 'absent']
    
    # Wound condition
    wound_condition: Literal['clean', 'redness', 'discharge', 'odor']
    wound_discharge_type: Optional[Literal['serous', 'bloody', 'purulent']] = None
    wound_swelling: Literal['none', 'mild', 'moderate', 'severe']
    
    # Mobility and weight-bearing
    mobility_level: Literal['independent', 'assisted', 'bed_bound']
    weight_bearing_status: Literal['non_weight', 'touch_down', 'partial', 'full']
    assistive_device: Optional[Literal['none', 'crutches', 'walker', 'cane']] = None
    
    # Drain management
    has_drain: bool
    drain_output: Optional[str] = None
    drain_color: Optional[Literal['serous', 'sanguinous', 'serosanguinous', 'purulent']] = None
    
    # General
    additional_notes: Optional[str] = ""
    status: Literal['urgent', 'monitor', 'good']

class OrthopedicEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: OrthopedicCommonData
    condition_data: OrthopedicConditionData

    @validator('submission_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class OrthopedicEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    created_at: str

    @validator('submission_date', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v