from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base

class AbdominalEntry(Base):
    __tablename__ = "abdominal_entries"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True, nullable=False)
    patient_name = Column(String, nullable=False)
    submission_date = Column(String, nullable=False)
    common_data = Column(JSON, nullable=False)
    condition_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())