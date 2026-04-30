from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class CommonDataSchema(BaseModel):
    blood_pressure_systolic: Optional[str] = None
    blood_pressure_diastolic: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[int] = None
    sleep_quality: Optional[int] = None
    medications: Optional[Dict[str, Any]] = {}
    symptoms: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = ""

class ConditionsDataSchema(BaseModel):
    diabetes: Optional[Dict[str, Any]] = {}
    hypertension: Optional[Dict[str, Any]] = {}
    heart: Optional[Dict[str, Any]] = {}
    cancer: Optional[Dict[str, Any]] = {}
    kidney: Optional[Dict[str, Any]] = {}

class LifelongEntryCreate(BaseModel):
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: CommonDataSchema
    conditions_data: ConditionsDataSchema
    status: Optional[str] = "good"

class LifelongEntryResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    submission_date: str
    common_data: Dict[str, Any]
    conditions_data: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime