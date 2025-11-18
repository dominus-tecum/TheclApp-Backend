from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, datetime

class BurnCareCreate(BaseModel):
    # ✅ ACCEPT DATA EXACTLY AS FRONTEND SENDS IT:
    patient_id: str
    patient_name: str
    surgery_type: str
    condition_type: str 
    submission_date: date
    submitted_at: datetime
    dayPost_op: int  # ← Match frontend's camelCase
    status: Literal['urgent', 'monitor', 'good']
    
    # ✅ ACCEPT ALL FLAT FIELDS (no nesting):
    pain_level: int
    itching: Literal['none', 'mild', 'moderate', 'severe']
    wound_appearance: Literal['pink', 'red', 'black', 'yellow', 'mixed']
    drainage: Literal['none', 'serous', 'serosanguinous', 'purulent']
    temperature: str
    rom_exercises: bool
    joint_tightness: Literal['none', 'mild', 'moderate', 'severe']
    mobility: Literal['bed_bound', 'chair', 'walking_indoor', 'walking_outdoor']
    compression_garment: bool
    scar_appearance: Literal['red_raised', 'pink_raised', 'flat_pink', 'flat_pale']
    protein_intake: str
    fluid_intake: str
    additional_notes: str

    class Config:
        # ✅ Allow extra fields in case frontend sends more data
        extra = "ignore"

class BurnCareResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    surgery_type: str
    condition_type: str
    submission_date: date
    submitted_at: datetime
    dayPost_op: int
    pain_level: int
    temperature: str
    status: str
    itching: str
    wound_appearance: str
    drainage: str
    rom_exercises: bool
    joint_tightness: str
    mobility: str
    compression_garment: bool
    scar_appearance: str
    protein_intake: str
    fluid_intake: str
    additional_notes: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ✅ ADD THE MISSING CLASS:
class BurnCareCheckResponse(BaseModel):
    exists: bool
    entry_id: Optional[int] = None

# ✅ ADD: For update operations if needed
class BurnCareUpdate(BaseModel):
    pain_level: Optional[int] = None
    itching: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    wound_appearance: Optional[Literal['pink', 'red', 'black', 'yellow', 'mixed']] = None
    drainage: Optional[Literal['none', 'serous', 'serosanguinous', 'purulent']] = None
    temperature: Optional[str] = None
    rom_exercises: Optional[bool] = None
    joint_tightness: Optional[Literal['none', 'mild', 'moderate', 'severe']] = None
    mobility: Optional[Literal['bed_bound', 'chair', 'walking_indoor', 'walking_outdoor']] = None
    compression_garment: Optional[bool] = None
    scar_appearance: Optional[Literal['red_raised', 'pink_raised', 'flat_pink', 'flat_pale']] = None
    protein_intake: Optional[str] = None
    fluid_intake: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[Literal['urgent', 'monitor', 'good']] = None

    class Config:
        extra = "ignore"