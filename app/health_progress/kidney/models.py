# app/health_progress/kidney/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class KidneyEntry(Base):
    __tablename__ = "kidney_entries"
    
    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    submission_date = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    
    # Common data fields (match frontend types)
    blood_pressure_systolic = Column(String(10), nullable=True)  # Changed to String
    blood_pressure_diastolic = Column(String(10), nullable=True) # Changed to String
    energy_level = Column(Integer, nullable=True)
    sleep_hours = Column(String(10), nullable=True)              # Changed to String
    sleep_quality = Column(Integer, nullable=True)
    medications = Column(JSON, nullable=True)                    # Changed to JSON
    symptoms = Column(JSON, nullable=True)                       # Changed to JSON
    notes = Column(Text, nullable=True)
    
    # Kidney-specific fields
    weight = Column(String(50), nullable=True)
    swelling_level = Column(Integer, nullable=True)
    urine_output = Column(String(50), nullable=True)
    fluid_intake = Column(String(50), nullable=True)
    breathing_difficulty = Column(Integer, nullable=True)
    fatigue_level = Column(Integer, nullable=True)
    nausea_level = Column(Integer, nullable=True)
    itching_level = Column(Integer, nullable=True)
    
    # Condition type and timestamps
    condition_type = Column(String(50), default="kidney")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    urgency_status = Column(String(50), default="low")  # Will be calculated by service