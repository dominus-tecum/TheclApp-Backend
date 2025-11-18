from sqlalchemy import Column, Integer, String, DateTime, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CesareanSectionEntry(Base):
    __tablename__ = "cesarean_section_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    surgery_type = Column(String)
    submission_date = Column(Date)
    
    # ✅ CHANGE TO JSON COLUMNS like abdominal
    common_data = Column(JSON, nullable=False)     # Store common fields as JSON
    condition_data = Column(JSON, nullable=False)  # Store cesarean fields as JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)