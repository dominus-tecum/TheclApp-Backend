from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class GeneralHealthEntry(Base):  # ✅ Changed from GeneralEntry to GeneralHealthEntry
    __tablename__ = "general_entries"
    
    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    submission_date = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    
    # General health specific fields
    health_trend = Column(String(50), nullable=True)
    overall_wellbeing = Column(Integer, nullable=True)
    primary_symptom_severity = Column(Integer, nullable=True)
    primary_symptom_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Condition type and timestamps
    condition_type = Column(String(50), default="general_health")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    urgency_status = Column(String(50), default="low")  # Will be calculated by service