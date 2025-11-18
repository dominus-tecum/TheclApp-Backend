# app/health_progress/bariatric/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from datetime import datetime

class BariatricEntryCreate(BaseModel):
    # ✅ ACCEPT EXACTLY what frontend sends
    patientId: Optional[Union[int, str]] = None  # Accept both int and string
    patientName: Optional[str] = None
    submissionDate: Optional[str] = None
    
    # Vital signs - all strings from frontend
    temperature: Optional[str] = None
    bloodPressureSystolic: Optional[str] = None
    bloodPressureDiastolic: Optional[str] = None
    heartRate: Optional[str] = None
    respiratoryRate: Optional[str] = None
    oxygenSaturation: Optional[str] = None
    
    # Pain - frontend sends number for painLevel
    painLevel: Optional[Union[int, str]] = None  # Accept 0 (int) or "none" (string)
    painLocation: Optional[str] = None
    
    # Fluid intake
    fluidIntake: Optional[str] = None
    fluidTypes: Optional[list] = None
    urineOutput: Optional[str] = None
    urineColor: Optional[str] = None
    
    # GI symptoms
    nauseaLevel: Optional[str] = None           # Frontend sends "none" ✓
    vomitingEpisodes: Optional[int] = None      # Frontend sends 0 ✓
    abdominalPain: Optional[str] = None         # Frontend sends "none" ✓
    abdominalDistension: Optional[str] = None   # Frontend sends "none" ✓
    bloating: Optional[bool] = None             # Frontend sends false ✓
    
    # Wound assessment  
    woundCondition: Optional[str] = None        # Frontend sends "clean" ✓
    woundTenderness: Optional[str] = None       # Frontend sends "mild" ✓
    hasDrain: Optional[bool] = None             # Frontend sends false ✓
    
    # Respiratory & Mobility
    breathingEffort: Optional[str] = None       # Frontend sends "normal" ✓
    oxygenTherapy: Optional[bool] = None        # Frontend sends false ✓
    mobilityLevel: Optional[str] = None         # Frontend sends "bed_bound" ✓
    ambulationFrequency: Optional[str] = None   # Frontend sends "none" ✓
    physiotherapySessions: Optional[int] = None # Frontend sends 0 ✓
    
    # Nutrition & Mental
    dietStage: Optional[str] = None             # Frontend sends "clear_liquid" ✓
    proteinIntake: Optional[str] = None
    waterGoalMet: Optional[bool] = None         # Frontend sends false ✓
    moodState: Optional[str] = None             # Frontend sends "good" ✓
    motivationLevel: Optional[str] = None       # Frontend sends "moderate" ✓
    cravings: Optional[bool] = None             # Frontend sends false ✓
    
    # Additional fields
    additionalNotes: Optional[str] = None
    surgeryType: Optional[str] = None           # Frontend sends "bariatric" ✓
    submittedAt: Optional[str] = None           # Frontend sends ISO string ✓
    dayPostOp: Optional[int] = None             # Frontend sends 672 ✓
    status: Optional[str] = None                # Frontend sends "urgent" ✓
    
    urgencyStatus: Optional[str] = "low"

    class Config:
        extra = "allow"  # ✅ ACCEPT ANY EXTRA FIELDS

# ✅ ADD THE MISSING RESPONSE CLASS
class BariatricEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    submitted_at: Optional[str] = None
    urgency_status: Optional[str] = None
    common_data: Dict[str, Any]
    condition_data: Dict[str, Any]

    class Config:
        allow_population_by_field_name = True