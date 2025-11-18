from pydantic import BaseModel, validator
from typing import Optional, List, Literal
from datetime import datetime

class GynecologicEntryCreate(BaseModel):
    # Patient Info
    patientId: int
    patientName: str
    submissionDate: str
    surgeryType: str = "gynecologic"
    submittedAt: str
    dayPostOp: int
    status: Literal['urgent', 'monitor', 'good']
    
    # Vital Signs and Pain Level
    temperature: Optional[str] = ""
    bloodPressureSystolic: Optional[str] = ""
    bloodPressureDiastolic: Optional[str] = ""
    heartRate: Optional[str] = ""
    respiratoryRate: Optional[str] = ""
    oxygenSaturation: Optional[str] = ""
    painLevel: int
    painLocation: List[Literal['abdominal', 'pelvic', 'shoulder', 'back', 'incisional', 'other']] = []
    
    # Vaginal Bleeding or Discharge
    bleedingAmount: Literal['none', 'spotting', 'light', 'moderate', 'heavy'] = 'none'
    dischargeColor: Literal['clear', 'pink', 'red', 'brown', 'yellow', 'green', 'other'] = 'clear'
    dischargeOdor: Literal['none', 'mild', 'strong', 'foul'] = 'none'
    dischargeConsistency: Literal['thin', 'thick', 'mucous', 'watery', 'clotted'] = 'thin'
    clotsPresent: bool = False
    clotSize: Literal['none', 'small', 'medium', 'large'] = 'none'
    
    # Urinary Function
    urinaryFrequency: Literal['normal', 'increased', 'decreased', 'painful'] = 'normal'
    urinaryRetention: bool = False
    hasCatheter: bool = False
    catheterOutput: Optional[str] = ""
    catheterPatency: Literal['patent', 'slow', 'obstructed', 'leaking'] = 'patent'
    dysuria: Literal['none', 'mild', 'moderate', 'severe'] = 'none'
    
    # Gastrointestinal Function
    nauseaLevel: Literal['none', 'mild', 'moderate', 'severe'] = 'none'
    vomitingEpisodes: int = 0
    abdominalDistension: Literal['none', 'mild', 'moderate', 'severe'] = 'none'
    bowelSounds: Literal['present_normal', 'present_hyperactive', 'present_hypoactive', 'absent'] = 'present_normal'
    flatusPassed: bool = False
    bowelMovement: bool = False
    bowelMovementType: Literal['normal', 'constipated', 'diarrhea', 'other'] = 'normal'
    
    # Wound and Drain Site
    woundCondition: Literal['clean_dry', 'redness', 'swelling', 'discharge', 'dehiscence'] = 'clean_dry'
    woundDischargeType: Optional[Literal['serous', 'sanguinous', 'purulent', 'other']] = None
    woundTenderness: Literal['none', 'mild', 'moderate', 'severe'] = 'mild'
    hasDrain: bool = False
    drainOutput: Optional[str] = ""
    drainColor: Literal['serous', 'sanguinous', 'serosanguinous', 'purulent'] = 'serosanguinous'
    drainConsistency: Literal['thin', 'thick', 'clotted'] = 'thin'
    
    # Mobility and Emotional Status
    mobilityLevel: Literal['bed_bound', 'chair', 'assisted_walking', 'independent'] = 'bed_bound'
    ambulationFrequency: Literal['none', 'rare', 'regular', 'frequent'] = 'none'
    ambulationDistance: Literal['none', 'room', 'hallway', 'unlimited'] = 'none'
    moodState: Literal['excellent', 'good', 'fair', 'poor', 'depressed'] = 'good'
    anxietyLevel: Literal['none', 'mild', 'moderate', 'severe'] = 'none'
    sleepQuality: Literal['poor', 'fair', 'good', 'excellent'] = 'fair'
    emotionalSupport: Literal['adequate', 'some', 'minimal', 'none'] = 'adequate'
    
    additionalNotes: Optional[str] = ""

    @validator('submissionDate')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class GynecologicEntryResponse(BaseModel):
    id: int
    patientId: int
    patientName: str
    submissionDate: str
    surgeryType: str
    submittedAt: str
    dayPostOp: int
    status: Literal['urgent', 'monitor', 'good']
    
    # All the same fields as create
    temperature: Optional[str] = ""
    bloodPressureSystolic: Optional[str] = ""
    bloodPressureDiastolic: Optional[str] = ""
    heartRate: Optional[str] = ""
    respiratoryRate: Optional[str] = ""
    oxygenSaturation: Optional[str] = ""
    painLevel: int
    painLocation: List[str] = []
    
    bleedingAmount: str = 'none'
    dischargeColor: str = 'clear'
    dischargeOdor: str = 'none'
    dischargeConsistency: str = 'thin'
    clotsPresent: bool = False
    clotSize: str = 'none'
    
    urinaryFrequency: str = 'normal'
    urinaryRetention: bool = False
    hasCatheter: bool = False
    catheterOutput: Optional[str] = ""
    catheterPatency: str = 'patent'
    dysuria: str = 'none'
    
    nauseaLevel: str = 'none'
    vomitingEpisodes: int = 0
    abdominalDistension: str = 'none'
    bowelSounds: str = 'present_normal'
    flatusPassed: bool = False
    bowelMovement: bool = False
    bowelMovementType: str = 'normal'
    
    woundCondition: str = 'clean_dry'
    woundDischargeType: Optional[str] = None
    woundTenderness: str = 'mild'
    hasDrain: bool = False
    drainOutput: Optional[str] = ""
    drainColor: str = 'serosanguinous'
    drainConsistency: str = 'thin'
    
    mobilityLevel: str = 'bed_bound'
    ambulationFrequency: str = 'none'
    ambulationDistance: str = 'none'
    moodState: str = 'good'
    anxietyLevel: str = 'none'
    sleepQuality: str = 'fair'
    emotionalSupport: str = 'adequate'
    
    additionalNotes: Optional[str] = ""
    createdAt: str