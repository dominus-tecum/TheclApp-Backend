from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Enum as SQLEnum, Date, Text
from sqlalchemy.sql import func
from datetime import date, datetime
import enum
from app.database import Base


class MensHealthStatus(str, enum.Enum):
    URGENT = "urgent"
    MONITOR = "monitor"
    GOOD = "good"


class MensHealthIntake(Base):
    """Questionnaire intake answers - saved once per patient"""
    __tablename__ = "mens_health_intake"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    completed_at = Column(DateTime, server_default=func.now())
    answers = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=True)
    confirmed_conditions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)


class MensHealthEntry(Base):
    """Daily entries for men's sexual health"""
    __tablename__ = "mens_health_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    patient_name = Column(String, nullable=False)
    submission_date = Column(Date, nullable=False, index=True)
    submitted_at = Column(DateTime, server_default=func.now())
    
    # Which conditions were tracked this day
    conditions_selected = Column(JSON, nullable=False)
    
    # Condition-specific data
    condition_data = Column(JSON, nullable=True)
    
    # Status flags
    status = Column(SQLEnum(MensHealthStatus), default=MensHealthStatus.GOOD)
    
    # Optional photo references
    photo_ids = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class MensHealthPhoto(Base):
    """Photos for size measurement and Peyronie's curvature tracking"""
    __tablename__ = "mens_health_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    entry_id = Column(Integer, nullable=True, index=True)
    condition = Column(String, nullable=False)  # 'size', 'peyronies'
    photo_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    taken_at = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)
    photo_metadata = Column(JSON, nullable=True)  # Stores length, girth, curvature angle
    consent_shared = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)



class MensHealthCalibration(Base):
    __tablename__ = "mens_health_calibration"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    grid_size_pixels = Column(Float, nullable=False)  # pixels per grid square (1 cm)
    card_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    calibrated_at = Column(DateTime, server_default=func.now())