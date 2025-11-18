from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class ActivityLevel(enum.Enum):
    BED_REST = "bed_rest"
    LIGHT = "light"
    NORMAL = "normal"
    ACTIVE = "active"

class UrineOutput(enum.Enum):
    LESS = "less"
    NORMAL = "normal"
    MORE = "more"

class ConditionType(enum.Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    HEART = "heart"
    CANCER = "cancer"
    KIDNEY = "kidney"

class EntryStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"

class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True, nullable=False)
    
    # Common data (stored as JSON for flexibility)
    common_data = Column(JSON, nullable=False)
    
    # Condition-specific data (stored as JSON)
    condition_data = Column(JSON, nullable=False)
    
    status = Column(Enum(EntryStatus), default=EntryStatus.DRAFT)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())              

class PatientCondition(Base):
    __tablename__ = "patient_conditions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True, nullable=False)
    condition_name = Column(String(100), nullable=False)
    condition_type = Column(Enum(ConditionType), nullable=False)
    diagnosed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)