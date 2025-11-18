from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import date, datetime

class PostnatalProfileCreate(BaseModel):
    # ✅ ACCEPT DATA EXACTLY AS FRONTEND SENDS IT:
    patient_id: str
    patient_name: str
    delivery_date: str  # string from frontend
    delivery_type: str
    infant_name: str
    infant_birth_weight: Optional[str] = None
    infant_birth_date: Optional[str] = None

    class Config:
        extra = "ignore"

class PostnatalProfileResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    delivery_date: Optional[str] = None
    delivery_type: str
    infant_name: str
    infant_birth_weight: Optional[str] = None
    infant_birth_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PostnatalCreate(BaseModel):
    # ✅ ACCEPT DATA EXACTLY AS FRONTEND SENDS IT:
    patient_id: str
    patient_name: str
    infant_name: str
    submission_date: str
    condition_type: str
    status: Literal['urgent', 'monitor', 'good']
    days_postpartum: int
    
    # ✅ MATERNAL RECOVERY (flat fields):
    lochia_flow: Literal['none', 'light', 'moderate', 'heavy']
    lochia_color: Literal['red', 'pink', 'brown', 'yellow']
    perineal_pain: Literal['none', 'mild', 'moderate', 'severe']
    uterine_pain: Literal['none', 'mild', 'moderate', 'severe']
    breast_engorgement: Literal['none', 'mild', 'moderate', 'severe']
    nipple_pain: Literal['none', 'mild', 'moderate', 'severe']
    c_section_pain: Literal['none', 'mild', 'moderate', 'severe']
    incision_redness: bool
    incision_discharge: bool
    
    # ✅ VITAL SIGNS:
    maternal_temperature: str
    blood_pressure_systolic: str
    blood_pressure_diastolic: str
    maternal_heart_rate: str
    
    # ✅ MENTAL HEALTH:
    mood_laugh: Literal['yes', 'sometimes', 'no']
    mood_anxious: Literal['no', 'sometimes', 'yes_often']
    mood_blame: Literal['no', 'sometimes', 'yes_often']
    mood_panic: Literal['no', 'sometimes', 'yes_often']
    mood_sleep: Literal['no', 'sometimes', 'yes_often']
    mood_sad: Literal['no', 'sometimes', 'yes_often']
    mood_crying: Literal['no', 'sometimes', 'yes_often']
    mood_harm: Literal['no', 'sometimes', 'yes_often']
    
    # ✅ INFANT CARE:
    feeding_method: Literal['breast', 'formula', 'mixed']
    feeding_frequency: int
    feeding_duration: str
    latching_quality: Literal['good', 'fair', 'poor']
    wet_diapers: int
    soiled_diapers: int
    stool_color: Literal['yellow', 'green', 'brown', 'black']
    stool_consistency: Literal['seedy', 'pasty', 'watery']
    infant_temperature: str
    infant_heart_rate: str
    jaundice_level: Literal['none', 'mild', 'moderate', 'severe']
    umbilical_cord: Literal['dry', 'moist', 'red', 'discharge']
    skin_condition: Literal['normal', 'rash', 'dry', 'peeling']
    infant_alertness: Literal['very_alert', 'alert', 'sleepy', 'lethargic']
    sleep_pattern: Literal['good', 'fair', 'poor']
    crying_level: Literal['normal', 'increased', 'excessive']
    
    # ✅ GENERAL:
    maternal_energy: Literal['good', 'fair', 'poor']
    support_system: Literal['adequate', 'some', 'inadequate']
    additional_notes: str

    class Config:
        extra = "ignore"

class PostnatalResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    infant_name: str
    submission_date: str
    condition_type: str
    status: str
    days_postpartum: int
    
    # All the flat fields from your model
    lochia_flow: Optional[str] = None
    lochia_color: Optional[str] = None
    perineal_pain: Optional[str] = None
    uterine_pain: Optional[str] = None
    breast_engorgement: Optional[str] = None
    nipple_pain: Optional[str] = None
    c_section_pain: Optional[str] = None
    incision_redness: Optional[bool] = None
    incision_discharge: Optional[bool] = None
    maternal_temperature: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    maternal_heart_rate: Optional[str] = None
    mood_laugh: Optional[str] = None
    mood_anxious: Optional[str] = None
    mood_blame: Optional[str] = None
    mood_panic: Optional[str] = None
    mood_sleep: Optional[str] = None
    mood_sad: Optional[str] = None
    mood_crying: Optional[str] = None
    mood_harm: Optional[str] = None
    feeding_method: Optional[str] = None
    feeding_frequency: Optional[int] = None
    feeding_duration: Optional[str] = None
    latching_quality: Optional[str] = None
    wet_diapers: Optional[int] = None
    soiled_diapers: Optional[int] = None
    stool_color: Optional[str] = None
    stool_consistency: Optional[str] = None
    infant_temperature: Optional[str] = None
    infant_heart_rate: Optional[str] = None
    jaundice_level: Optional[str] = None
    umbilical_cord: Optional[str] = None
    skin_condition: Optional[str] = None
    infant_alertness: Optional[str] = None
    sleep_pattern: Optional[str] = None
    crying_level: Optional[str] = None
    maternal_energy: Optional[str] = None
    support_system: Optional[str] = None
    additional_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostnatalCheckResponse(BaseModel):
    exists: bool
    entry_id: Optional[int] = None