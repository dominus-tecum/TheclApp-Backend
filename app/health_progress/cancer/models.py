from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CancerEntry(Base):
    __tablename__ = "cancer_entries"
    
    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    submission_date = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    
    # Common data fields (match frontend types)
    blood_pressure_systolic = Column(String(10), nullable=True)
    blood_pressure_diastolic = Column(String(10), nullable=True)
    energy_level = Column(Integer, nullable=True)
    sleep_hours = Column(String(10), nullable=True)
    sleep_quality = Column(Integer, nullable=True)
    medications = Column(JSON, nullable=True)
    symptoms = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Cancer-specific fields
    pain_level = Column(Integer, nullable=True)
    pain_location = Column(String(255), nullable=True)
    side_effects = Column(Integer, nullable=True)
    
    # Condition type and timestamps
    condition_type = Column(String(50), default="cancer")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    urgency_status = Column(String(50), default="low")  # Will be calculated by service