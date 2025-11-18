from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import date, datetime

class PrenatalCreate(BaseModel):
    # ✅ ACCEPT DATA EXACTLY AS FRONTEND SENDS IT:
    patient_id: str
    patient_name: str
    gestational_age: str
    condition_type: str 
    submission_date: date
    submitted_at: datetime
    status: Literal['urgent', 'monitor', 'good']
    high_risk: bool
    
    # ✅ MATERNAL VITAL SIGNS (flat fields):
    maternal_temperature: str
    blood_pressure_systolic: str
    blood_pressure_diastolic: str
    maternal_heart_rate: str
    respiratory_rate: str
    oxygen_saturation: str
    
    # ✅ MATERNAL SYMPTOMS:
    weight: str
    edema: Literal['none', 'mild', 'moderate', 'severe']
    edema_location: List[str]
    headache: Literal['none', 'mild', 'moderate', 'severe']
    visual_disturbances: bool
    epigastric_pain: bool
    nausea_level: Literal['none', 'mild', 'moderate', 'severe']
    vomiting_episodes: int
    
    # ✅ FETAL MOVEMENT AND ACTIVITY:
    fetal_movement: Literal['normal', 'decreased', 'increased', 'absent']
    movement_count: int
    movement_duration: str
    
    # ✅ CONTRACTIONS:
    contractions: bool
    contraction_frequency: str
    contraction_duration: str
    contraction_intensity: Literal['mild', 'moderate', 'strong']
    
    # ✅ VAGINAL SYMPTOMS:
    vaginal_bleeding: Literal['none', 'spotting', 'light', 'moderate', 'heavy']
    bleeding_color: Literal['pink', 'red', 'brown']
    fluid_leak: bool
    fluid_color: Literal['clear', 'yellow', 'green', 'blood_tinged']
    fluid_amount: Literal['small', 'moderate', 'large']
    
    # ✅ URINARY SYMPTOMS:
    urinary_frequency: Literal['normal', 'increased', 'decreased']
    dysuria: Literal['none', 'mild', 'moderate', 'severe']
    urinary_incontinence: bool
    
    # ✅ GASTROINTESTINAL:
    appetite: Literal['normal', 'decreased', 'increased']
    heartburn: Literal['none', 'mild', 'moderate', 'severe']
    constipation: Literal['none', 'mild', 'moderate', 'severe']
    
    # ✅ MEDICATION COMPLIANCE:
    medications_taken: bool
    missed_medications: str
    
    # ✅ ADDITIONAL NOTES:
    additional_notes: str

    class Config:
        # ✅ Allow extra fields in case frontend sends more data
        extra = "ignore"

class PrenatalResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    gestational_age: str
    submission_date: date
    condition_type: str
    status: str
    high_risk: bool
    
    # All the flat fields from your model
    maternal_temperature: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    maternal_heart_rate: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    weight: Optional[str] = None
    edema: Optional[str] = None
    edema_location: Optional[str] = None
    headache: Optional[str] = None
    visual_disturbances: Optional[bool] = None
    epigastric_pain: Optional[bool] = None
    nausea_level: Optional[str] = None
    vomiting_episodes: Optional[int] = None
    fetal_movement: Optional[str] = None
    movement_count: Optional[int] = None
    movement_duration: Optional[str] = None
    contractions: Optional[bool] = None
    contraction_frequency: Optional[str] = None
    contraction_duration: Optional[str] = None
    contraction_intensity: Optional[str] = None
    vaginal_bleeding: Optional[str] = None
    bleeding_color: Optional[str] = None
    fluid_leak: Optional[bool] = None
    fluid_color: Optional[str] = None
    fluid_amount: Optional[str] = None
    urinary_frequency: Optional[str] = None
    dysuria: Optional[str] = None
    urinary_incontinence: Optional[bool] = None
    appetite: Optional[str] = None
    heartburn: Optional[str] = None
    constipation: Optional[str] = None
    medications_taken: Optional[bool] = None
    missed_medications: Optional[str] = None
    additional_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    urgency_status: Optional[str] = None

    class Config:
        from_attributes = True

class PrenatalCheckResponse(BaseModel):
    exists: bool
    entry_id: Optional[int] = None

# ✅ ADD: For update operations if needed
class PrenatalUpdate(BaseModel):
    # Maternal Vital Signs
    maternal_temperature: Optional[str] = None
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    maternal_heart_rate: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    
    # Maternal Symptoms
    weight: Optional[str] = None
    edema: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    edema_location: Optional[List[str]] = None
    headache: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    visual_disturbances: Optional[bool] = None
    epigastric_pain: Optional[bool] = None
    nausea_level: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    vomiting_episodes: Optional[int] = None
    
    # Fetal Movement
    fetal_movement: Optional[Literal['normal', 'decreased', 'increased', 'absent']] = None
    movement_count: Optional[int] = None
    movement_duration: Optional[str] = None
    
    # Contractions
    contractions: Optional[bool] = None
    contraction_frequency: Optional[str] = None
    contraction_duration: Optional[str] = None
    contraction_intensity: Optional[Literal['mild', 'moderate', 'strong']] = None
    
    # Vaginal Symptoms
    vaginal_bleeding: Optional[Literal['none', 'spotting', 'light', 'moderate', 'heavy']] = None
    bleeding_color: Optional[Literal['pink', 'red', 'brown']] = None
    fluid_leak: Optional[bool] = None
    fluid_color: Optional[Literal['clear', 'yellow', 'green', 'blood_tinged']] = None
    fluid_amount: Optional[Literal['small', 'moderate', 'large']] = None
    
    # Urinary Symptoms
    urinary_frequency: Optional[Literal['normal', 'increased', 'decreased']] = None
    dysuria: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    urinary_incontinence: Optional[bool] = None
    
    # Gastrointestinal
    appetite: Optional[Literal['normal', 'decreased', 'increased']] = None
    heartburn: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    constipation: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    
    # Medication Compliance
    medications_taken: Optional[bool] = None
    missed_medications: Optional[str] = None
    
    # Additional Notes
    additional_notes: Optional[str] = None
    status: Optional[Literal['urgent', 'monitor', 'good']] = None

    class Config:
        extra = "ignore"