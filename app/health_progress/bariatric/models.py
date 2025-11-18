# app/health_progress/bariatric/models.py - TEMPORARY FIX
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BariatricEntry(Base):
    __tablename__ = "bariatric_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    submission_date = Column(String(50), nullable=False)
    submitted_at = Column(DateTime)
    urgency_status = Column(String(50))
    common_data = Column(JSON)
    condition_data = Column(JSON)
    
    # REMOVE the new columns temporarily until migration is done
    # temperature = Column(String(10))
    # blood_pressure_systolic = Column(String(10))
    # ... etc