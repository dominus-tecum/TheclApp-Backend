from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Enum as SQLEnum, Date, Text
from sqlalchemy.sql import func
from datetime import date, datetime
import enum
from app.database import Base


class WomensHealthStatus(str, enum.Enum):
    URGENT = "urgent"
    MONITOR = "monitor"
    GOOD = "good"


class WomensHealthIntake(Base):
    """Questionnaire intake answers - saved once per patient"""
    __tablename__ = "womens_health_intake"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    completed_at = Column(DateTime, server_default=func.now())
    answers = Column(JSON, nullable=False)  # Full questionnaire answers
    recommendations = Column(JSON, nullable=True)  # Generated recommendations
    confirmed_conditions = Column(JSON, nullable=True)  # User confirmed conditions
    is_active = Column(Boolean, default=True)


class WomensHealthEntry(Base):
    """Daily entries for women's reproductive health"""
    __tablename__ = "womens_health_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    patient_name = Column(String, nullable=False)
    submission_date = Column(Date, nullable=False, index=True)
    submitted_at = Column(DateTime, server_default=func.now())
    
    # Which conditions were tracked this day
    conditions_selected = Column(JSON, nullable=False)  # ['vaginismus', 'menopause']
    
    # Shared data across all conditions
    common_data = Column(JSON, nullable=True)  # energy, sleep, medications, symptoms, notes
    
    # Condition-specific data
    condition_data = Column(JSON, nullable=True)  # vaginismus, endometriosis, sti, menopause, pcos
    
    # Status flags
    status = Column(SQLEnum(WomensHealthStatus), default=WomensHealthStatus.GOOD)
    
    # Optional photo references
    photo_ids = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class WomensHealthPhoto(Base):
    """Photos for STI and skin condition tracking"""
    __tablename__ = "womens_health_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    entry_id = Column(Integer, nullable=True, index=True)  # Optional: link to entry
    condition = Column(String, nullable=False)  # 'sti', 'vaginismus', etc.
    photo_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    taken_at = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)  # For timeline ordering