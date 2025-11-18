from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

# Base Schemas
class MedicalRecordBase(BaseModel):
    patient_id: str
    patient_name: str
    type: str
    category: str  # "Lab Results", "Prescriptions", "Medical History"
    doctor: str
    date: str
    status: str
    details: Dict[str, Any]
    lab_order_id: Optional[str] = None
    prescription_id: Optional[str] = None
    appointment_id: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class MedicalRecord(MedicalRecordBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Specialized schemas for different categories
class LabResultCreate(BaseModel):
    patient_id: str
    patient_name: str
    test_type: str
    doctor: str
    results: Dict[str, Any]  # e.g., {"glucose": "95 mg/dL", "cholesterol": "180 mg/dL"}
    interpretation: Optional[str] = None
    lab_order_id: Optional[str] = None

class PrescriptionCreate(BaseModel):
    patient_id: str
    patient_name: str
    medication: str
    dosage: str
    frequency: str
    duration: str
    doctor: str
    instructions: Optional[str] = None