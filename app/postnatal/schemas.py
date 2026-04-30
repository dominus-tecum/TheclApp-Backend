from pydantic import BaseModel
from typing import Optional, Literal, List, Union  # ← ADD Union here
from datetime import date, datetime

class PostnatalProfileCreate(BaseModel):
    patient_id: str
    patient_name: str
    delivery_date: str
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
    # Basic Info
    patient_id: str
    patient_name: str
    infant_name: str
    submission_date: str
    condition_type: str
    status: Literal['urgent', 'monitor', 'good']
    days_postpartum: int
    submitted_at: Optional[str] = None
    
    # Vital Signs
    maternal_temperature: str
    blood_pressure_systolic: str
    blood_pressure_diastolic: str
    maternal_heart_rate: str
    sleep_hours: Optional[int] = 0
    
    # Pain Assessment
    pain_level: Optional[str] = None
    pain_location: Optional[Union[str, List[str]]] = None
    perineal_pain: Optional[str] = None
    uterine_pain: Optional[str] = None
    nipple_pain: Optional[str] = None
    c_section_pain: Optional[str] = None
    
    # Uterine Recovery & Lochia
    lochia_flow: Literal['none', 'light', 'moderate', 'heavy']
    lochia_color: Literal['red', 'pink', 'brown', 'yellow']
    lochia_odor: Optional[str] = None
    healing_progress: Optional[str] = None
    perineal_tear: Optional[str] = None
    
    # Incision
    incision_redness: Optional[bool] = False
    incision_discharge: Optional[bool] = False
    
    # Breastfeeding
    breastfeeding_status: Optional[str] = None
    breast_engorgement: Optional[str] = None
    nipple_condition: Optional[str] = None
    milk_supply: Optional[str] = None
    feeding_method: Optional[str] = None
    feeding_frequency: Optional[int] = 0
    feeding_duration: Optional[str] = None
    latching_quality: Optional[str] = None
    
    # Emotional Wellbeing
    baby_blues_symptoms: Optional[bool] = False
    maternal_energy: Optional[str] = None
    
    # Gastrointestinal & Urinary
    appetite: Optional[str] = None
    bowel_movement: Optional[str] = None
    urinary_frequency: Optional[str] = None
    incontinence: Optional[bool] = False
    
    # Baby Information
    baby_feeding_frequency: Optional[int] = 0
    baby_urination_frequency: Optional[int] = 0
    baby_bowel_movement_frequency: Optional[int] = 0
    baby_weight_gain: Optional[str] = None
    wet_diapers: Optional[int] = 0
    soiled_diapers: Optional[int] = 0
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
    
    # Medications
    medication_adherence: Optional[bool] = True
    missed_medications: Optional[str] = None
    
    # Notes
    additional_notes: Optional[str] = None
    additional_concerns: Optional[str] = None

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
    
    # Vital Signs
    maternal_temperature: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    maternal_heart_rate: Optional[str] = None
    sleep_hours: Optional[int] = None
    
    # Pain Assessment
    pain_level: Optional[str] = None
    pain_location: Optional[str] = None
    perineal_pain: Optional[str] = None
    uterine_pain: Optional[str] = None
    nipple_pain: Optional[str] = None
    c_section_pain: Optional[str] = None
    
    # Uterine Recovery & Lochia
    lochia_flow: Optional[str] = None
    lochia_color: Optional[str] = None
    lochia_odor: Optional[str] = None
    healing_progress: Optional[str] = None
    perineal_tear: Optional[str] = None
    
    # Incision
    incision_redness: Optional[bool] = None
    incision_discharge: Optional[bool] = None
    
    # Breastfeeding
    breastfeeding_status: Optional[str] = None
    breast_engorgement: Optional[str] = None
    nipple_condition: Optional[str] = None
    milk_supply: Optional[str] = None
    feeding_method: Optional[str] = None
    feeding_frequency: Optional[int] = None
    feeding_duration: Optional[str] = None
    latching_quality: Optional[str] = None
    
    # Emotional Wellbeing
    baby_blues_symptoms: Optional[bool] = None
    maternal_energy: Optional[str] = None
    
    # Gastrointestinal & Urinary
    appetite: Optional[str] = None
    bowel_movement: Optional[str] = None
    urinary_frequency: Optional[str] = None
    incontinence: Optional[bool] = None
    
    # Baby Information
    baby_feeding_frequency: Optional[int] = None
    baby_urination_frequency: Optional[int] = None
    baby_bowel_movement_frequency: Optional[int] = None
    baby_weight_gain: Optional[str] = None
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
    
    # Medications
    medication_adherence: Optional[bool] = None
    missed_medications: Optional[str] = None
    
    # Notes
    additional_notes: Optional[str] = None
    additional_concerns: Optional[str] = None
    
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostnatalCheckResponse(BaseModel):
    exists: bool
    entry_id: Optional[int] = None