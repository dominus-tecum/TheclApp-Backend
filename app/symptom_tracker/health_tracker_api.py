from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()

# --- Models ---
class GlucoseReading(BaseModel):
    id: str
    glucose: float
    date: str
    note: Optional[str] = ""

class BPReading(BaseModel):
    id: str
    systolic: int
    diastolic: int
    date: str
    note: Optional[str] = ""

# --- In-memory DB ---
glucose_readings = []
bp_readings = []

# --- Glucose Endpoints ---
class GlucoseIn(BaseModel):
    glucose: float
    date: str
    note: Optional[str] = ""

@router.post("/readings/glucose")
def save_glucose(reading: GlucoseIn):
    entry = GlucoseReading(
        id=str(uuid.uuid4()),
        glucose=reading.glucose,
        date=reading.date,
        note=reading.note
    )
    glucose_readings.append(entry)
    return {"msg": "Glucose reading saved", "id": entry.id}

@router.get("/readings/glucose", response_model=List[GlucoseReading])
def get_glucose():
    return glucose_readings

# --- BP Endpoints ---
class BPIn(BaseModel):
    systolic: int
    diastolic: int
    date: str
    note: Optional[str] = ""

@router.post("/readings/bp")
def save_bp(reading: BPIn):
    entry = BPReading(
        id=str(uuid.uuid4()),
        systolic=reading.systolic,
        diastolic=reading.diastolic,
        date=reading.date,
        note=reading.note
    )
    bp_readings.append(entry)
    return {"msg": "BP reading saved", "id": entry.id}

@router.get("/readings/bp", response_model=List[BPReading])
def get_bp():
    return bp_readings