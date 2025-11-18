from sqlalchemy import Column, Integer, String, DateTime, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BurnCareEntry(Base):
    __tablename__ = "burn_care_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    patient_name = Column(String)
    surgery_type = Column(String)
    submission_date = Column(Date)
    condition_type = Column(String, default="burn_care")  # ✅ ADDED
    common_data = Column(JSON, nullable=False)
    condition_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)