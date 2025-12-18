from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, ForeignKey, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from app.database_base import Base

# Enums for Fertility Tracking
class CervicalFluidType(str, enum.Enum):
    DRY = "dry"
    STICKY = "sticky"
    CREAMY = "creamy"
    WATERY = "watery"
    EGG_WHITE = "egg_white"
    BLOODY = "bloody"

class CervicalFluidAmount(str, enum.Enum):
    NONE = "none"
    SCANT = "scant"
    MODERATE = "moderate"
    ABUNDANT = "abundant"

class CervicalPosition(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CervicalFirmness(str, enum.Enum):
    FIRM = "firm"
    MEDIUM = "medium"
    SOFT = "soft"

class CervicalOpening(str, enum.Enum):
    CLOSED = "closed"
    PARTIALLY_OPEN = "partially_open"
    OPEN = "open"

class LHTestResult(str, enum.Enum):
    NEGATIVE = "negative"
    LOW = "low"
    HIGH = "high"
    PEAK = "peak"

class MenstrualFlow(str, enum.Enum):
    SPOTTING = "spotting"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    VERY_HEAVY = "very_heavy"

class MoodLevel(str, enum.Enum):
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "very_sad"
    ANXIOUS = "anxious"

class EnergyLevel(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"

class StressLevel(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class LibidoLevel(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"

class SymptomSeverity(str, enum.Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class FertilityStatus(str, enum.Enum):
    FERTILE = "fertile"
    POSSIBLY_FERTILE = "possibly_fertile"
    INFERTILE = "infertile"
    POST_OVULATION = "post_ovulation"

class IntercoursePosition(str, enum.Enum):
    MISSIONARY = "missionary"
    DOGGY = "doggy"
    COWGIRL = "cowgirl"
    SPOONING = "spooning"
    OTHER = "other"

class ContraceptionType(str, enum.Enum):
    NONE = "none"
    CONDOM = "condom"
    PULL_OUT = "pull_out"
    OTHER = "other"

class CyclePhase(str, enum.Enum):
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATION = "ovulation"
    LUTEAL = "luteal"


class FertilityEntry(Base):
    __tablename__ = "fertility_entries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Patient Information
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    patient_name = Column(String(255), nullable=False)
    
    # Cycle Information
    cycle_day = Column(Integer, nullable=False)
    predicted_ovulation_day = Column(Integer, nullable=False)
    fertility_window_start = Column(Integer, nullable=False)
    fertility_window_end = Column(Integer, nullable=False)
    fertility_status = Column(Enum(FertilityStatus), nullable=False)
    cycle_phase = Column(Enum(CyclePhase), nullable=True)
    
    # Basal Body Temperature (BBT)
    bbt_temperature = Column(Float, nullable=True)
    bbt_time = Column(String(50), nullable=True)
    bbt_notes = Column(Text, nullable=True)
    
    # Cervical Fluid
    cervical_fluid_type = Column(Enum(CervicalFluidType), nullable=True)
    cervical_fluid_amount = Column(Enum(CervicalFluidAmount), nullable=True)
    cervical_fluid_color = Column(String(50), nullable=True)
    
    # Cervical Position
    cervical_position = Column(Enum(CervicalPosition), nullable=True)
    cervical_firmness = Column(Enum(CervicalFirmness), nullable=True)
    cervical_opening = Column(Enum(CervicalOpening), nullable=True)
    
    # LH Testing
    lh_test_result = Column(Enum(LHTestResult), nullable=True)
    lh_test_time = Column(String(50), nullable=True)
    lh_test_brand = Column(String(100), nullable=True)
    
    # Menstrual Tracking
    menstrual_flow = Column(Enum(MenstrualFlow), nullable=True)
    menstrual_color = Column(String(50), nullable=True)
    menstrual_cramps = Column(Enum(SymptomSeverity), nullable=True)
    
    # Symptoms
    libido_level = Column(Enum(LibidoLevel), nullable=True)
    breast_tenderness = Column(Enum(SymptomSeverity), nullable=True)
    ovulation_pain = Column(Boolean, default=False)
    ovulation_pain_side = Column(String(50), nullable=True)
    bloating = Column(Enum(SymptomSeverity), nullable=True)
    mood = Column(Enum(MoodLevel), nullable=True)
    energy_level = Column(Enum(EnergyLevel), nullable=True)
    
    # Intercourse Tracking
    intercourse_today = Column(Boolean, default=False)
    intercourse_time = Column(String(50), nullable=True)
    intercourse_position = Column(Enum(IntercoursePosition), nullable=True)
    contraception_used = Column(Enum(ContraceptionType), nullable=True)
    
    # Health Metrics
    weight = Column(Float, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    stress_level = Column(Enum(StressLevel), nullable=True)
    
    # Medications and Supplements (stored as JSON)
    medications = Column(JSON, default=dict)
    
    # Additional Notes
    additional_notes = Column(Text, nullable=True)
    
    # Metadata
    submission_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD format
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="fertility_entries")
    
    class Config:
        orm_mode = True


class FertilityProfile(Base):
    __tablename__ = "fertility_profiles"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    
    # Cycle Information
    cycle_length = Column(Integer, default=28)
    period_length = Column(Integer, default=5)
    last_period_date = Column(String(10), nullable=True)  # YYYY-MM-DD format
    typical_cycle_pattern = Column(String(50), default="regular")
    
    # Fertility Goals
    trying_to_conceive = Column(Boolean, default=False)
    fertility_issues = Column(JSON, default=list)  # List of strings
    
    # Medical History
    known_conditions = Column(JSON, default=list)
    medications_history = Column(JSON, default=list)

    # ============ ADD THIS LINE ============
    period_dates = Column(JSON, nullable=True)  # or Text if you prefer
    # =======================================
    
    # Pregnancy History
    previous_pregnancies = Column(Integer, default=0)
    previous_births = Column(Integer, default=0)
    previous_miscarriages = Column(Integer, default=0)
    
    # Partner Information
    partner_age = Column(Integer, nullable=True)
    partner_fertility_issues = Column(JSON, default=list)
    
    # Risk Factors
    high_risk = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="fertility_profile", uselist=False)
    
    class Config:
        orm_mode = True


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    birth_date = Column(String(10), nullable=True)  # YYYY-MM-DD format
    phone_number = Column(String(50), nullable=True)
    # ADD THESE FIELDS:
    #last_period_date = Column(Date, nullable=True)  # ← ADD THIS
    #cycle_length = Column(Integer, default=28)       # ← Already have? Make sure
    #period_length = Column(Integer, default=5)       # ← Already have
    #trying_to_conceive = Column(Boolean, default=True)
    #fertility_issues = Column(JSON, default=[])      # Or use Array if PostgreSQL
    #high_risk = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fertility_entries = relationship("FertilityEntry", back_populates="patient", cascade="all, delete-orphan")
    fertility_profile = relationship("FertilityProfile", back_populates="patient", cascade="all, delete-orphan")
    
    class Config:
        orm_mode = True


class CycleAnalysis(Base):
    __tablename__ = "cycle_analyses"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=True)
    
    # Analysis Results
    cycle_length = Column(Integer, nullable=True)
    ovulation_day = Column(Integer, nullable=True)
    luteal_phase_length = Column(Integer, nullable=True)
    bbt_shift_detected = Column(Boolean, default=False)
    ovulation_confirmed = Column(Boolean, default=False)
    
    # Statistics
    average_bbt_pre_ovulation = Column(Float, nullable=True)
    average_bbt_post_ovulation = Column(Float, nullable=True)
    bbt_shift_amount = Column(Float, nullable=True)
    
    # Symptoms Analysis
    symptoms_summary = Column(JSON, default=dict)
    
    # Fertility Insights
    fertile_window = Column(JSON, default=dict)  # {"start_day": X, "end_day": Y}
    peak_fertility_day = Column(Integer, nullable=True)
    
    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient")
    
    class Config:
        orm_mode = True


class FertilityInsight(Base):
    __tablename__ = "fertility_insights"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    
    # Insight Data
    insight_type = Column(String(100), nullable=False)  # pattern, prediction, recommendation
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    confidence_score = Column(Float, nullable=True)
    
    # Status
    is_actionable = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    patient = relationship("Patient")
    
    class Config:
        orm_mode = True