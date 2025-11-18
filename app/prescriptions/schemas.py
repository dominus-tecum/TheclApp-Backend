from pydantic import BaseModel
from datetime import datetime

class PrescriptionCreate(BaseModel):
    user_id: int
    medication: str
    dosage: str
    issued_date: datetime
    doctor_id: int

class PrescriptionRead(BaseModel):
    id: int
    user_id: int
    medication: str
    dosage: str
    issued_date: datetime
    doctor_id: int

    model_config = {
        "from_attributes": True
    }