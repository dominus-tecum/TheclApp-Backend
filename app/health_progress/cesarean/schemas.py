# app/health_progress/cesarean/schemas.py
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date  # ✅ ADD date import

class CesareanCommonData(BaseModel):
    temperature: Optional[str] = ""
    blood_pressure_systolic: Optional[str] = ""
    blood_pressure_diastolic: Optional[str] = ""
    heart_rate: Optional[str] = ""
    respiratory_rate: Optional[str] = ""
    pain_level: int
    # Note: fluid_intake and urine_output are in condition_data for cesarean

class CesareanConditionData(BaseModel):
    # Postpartum recovery metrics
    fundal_height: Optional[str] = ""
    uterine_firmness: str
    lochia_color: str
    lochia_amount: str
    lochia_odor: str
    
    # Surgical site metrics
    wound_condition: str
    wound_discharge_type: Optional[str] = ""
    wound_tenderness: str
    
    # Urinary/Bowel function
    urine_output: Optional[str] = ""
    urinary_retention: bool
    bowel_sounds: str
    flatus_passed: bool
    bowel_movement: bool
    
    # Mobility
    mobility_level: str
    ambulation_distance: str
    
    # Breastfeeding
    breastfeeding: bool
    breast_engorgement: str
    breast_tenderness: str
    nipple_condition: str
    feeding_frequency: str
    
    # General
    additional_notes: Optional[str] = ""
    status: str

class CesareanEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: CesareanCommonData
    condition_data: CesareanConditionData

    @validator('submission_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class CesareanEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    created_at: str

    # ✅ FIXED: Convert date to string for response
    @validator('submission_date', pre=True)
    def convert_date_to_string(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v