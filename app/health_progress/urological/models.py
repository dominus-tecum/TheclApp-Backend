from app.database import Base
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime

class UrologicalSurgeryEntry(Base):
    __tablename__ = "urological_surgery_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    surgery_type = Column(String)
    submission_date = Column(String)
    common_data = Column(JSON)        # Store nested common_data as JSON
    condition_data = Column(JSON)     # Store nested condition_data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)