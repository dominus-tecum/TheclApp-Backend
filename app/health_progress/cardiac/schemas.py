# app/health_progress/cardiac/schemas.py
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date

class CardiacEntryCreate(BaseModel):
    # Accept the flat structure exactly as frontend sends it
    patientId: int
    patientName: str
    submissionDate: str
    surgeryType: str
    
    # Common data fields (camelCase)
    temperature: Optional[str] = ""
    bloodPressureSystolic: Optional[str] = ""
    bloodPressureDiastolic: Optional[str] = ""
    heartRate: Optional[str] = ""
    respiratoryRate: Optional[str] = ""
    oxygenSaturation: Optional[str] = ""
    painLevel: int
    
    # Condition data fields (camelCase)
    cardiacRhythm: str
    rhythmStable: bool
    breathingEffort: str
    oxygenTherapy: bool
    oxygenFlow: Optional[str] = ""
    incentiveSpirometer: str
    coughEffectiveness: str
    hasChestTube: bool
    chestTubeOutput: Optional[str] = ""
    chestDrainColor: str
    chestDrainConsistency: str
    urineOutput: Optional[str] = ""
    fluidBalance: Optional[str] = ""
    sternalWoundCondition: str
    graftWoundCondition: str
    woundDischargeType: Optional[str] = ""
    woundTenderness: str
    consciousnessLevel: str
    orientation: str
    limbMovement: str
    mobilityLevel: str
    ambulationDistance: str
    painLocation: str
    moodState: str
    sleepQuality: str
    additionalNotes: Optional[str] = ""
    status: Optional[str] = "stable"
    
    # Optional fields that might be sent
    submittedAt: Optional[str] = None
    dayPostOp: Optional[int] = None

    @validator('submissionDate')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class CardiacEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]
    created_at: str

    class Config:
        allow_population_by_field_name = True