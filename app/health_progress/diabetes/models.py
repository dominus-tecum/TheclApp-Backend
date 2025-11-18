# app/health_progress/diabetes/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DiabetesEntry(Base):
    __tablename__ = "diabetes_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String, nullable=False)
    submission_date = Column(String, nullable=False)
    
    # Flat fields that match frontend
    blood_glucose = Column(String, nullable=True)
    blood_pressure_systolic = Column(String, nullable=True)
    blood_pressure_diastolic = Column(String, nullable=True)
    energy_level = Column(Integer, nullable=True)
    sleep_hours = Column(Integer, nullable=True)
    sleep_quality = Column(Integer, nullable=True)
    medications = Column(JSON, nullable=True)
    symptoms = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=True)
    condition_type = Column(String, default="diabetes")
    
    created_at = Column(DateTime, default=datetime.utcnow)