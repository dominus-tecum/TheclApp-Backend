# app/health_progress/heart/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class HeartEntry(Base):
    __tablename__ = "heart_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String, nullable=False)
    submission_date = Column(String, nullable=False)
    
    # ✅ FLAT FIELDS INSTEAD OF NESTED JSON
    blood_pressure_systolic = Column(String, nullable=True)
    blood_pressure_diastolic = Column(String, nullable=True)
    energy_level = Column(Integer, nullable=True)
    sleep_hours = Column(Integer, nullable=True)
    sleep_quality = Column(Integer, nullable=True)
    medications = Column(JSON, nullable=True)
    symptoms = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=True)
    
    # Heart-specific flat fields
    chest_pain_level = Column(Integer, nullable=True)
    pain_location = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    swelling_level = Column(Integer, nullable=True)
    breathing_difficulty = Column(Integer, nullable=True)
    condition_type = Column(String, default="heart")
    
    created_at = Column(DateTime, default=datetime.utcnow)