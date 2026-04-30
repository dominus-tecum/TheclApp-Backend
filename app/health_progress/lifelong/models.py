from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.database import Base

class LifelongEntry(Base):
    __tablename__ = "lifelong_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String, nullable=False)
    submission_date = Column(String, nullable=False)
    
    # Store all data in JSON
    common_data = Column(JSON, nullable=True)
    conditions_data = Column(JSON, nullable=True)
    
    status = Column(String, default="good")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)