from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from typing import Optional, List, Dict, Any  # Make sure List is included

class AbdominalCommonData(BaseModel):
    temperature: Optional[str] = ""
    blood_pressure_systolic: Optional[str] = ""
    blood_pressure_diastolic: Optional[str] = ""
    heart_rate: Optional[str] = ""
    respiratory_rate: Optional[str] = ""
    pain_level: int
    fluid_intake: Optional[str] = ""
    urine_output: Optional[str] = ""

class AbdominalConditionData(BaseModel):
    gi_function: str
    nausea_vomiting: str
    appetite: str
    wound_condition: str
    mobility: str
    additional_notes: Optional[str] = ""

class AbdominalEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: AbdominalCommonData
    condition_data: AbdominalConditionData
    photo_urls: Optional[List[str]] = []

    @validator('submission_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class AbdominalEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    photo_urls: Optional[List[str]] = []
    created_at: str