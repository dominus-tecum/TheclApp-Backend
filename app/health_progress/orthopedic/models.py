from sqlalchemy import Column, Integer, String, DateTime, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class OrthopedicSurgeryEntry(Base):
    __tablename__ = "orthopedic_surgery_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    surgery_type = Column(String)
    submission_date = Column(Date)  # ✅ Changed to Date like cesarean
    
    # ✅ EXACT same structure as cesarean
    common_data = Column(JSON, nullable=False)     # Store common fields as JSON
    condition_data = Column(JSON, nullable=False)  # Store orthopedic fields as JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)