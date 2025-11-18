# app/postnatal/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class PostnatalEntry(Base):
    __tablename__ = "postnatal_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    infant_name = Column(String, nullable=False)
    submission_date = Column(String, nullable=False)
    condition_type = Column(String, default='postnatal')
    
    # MATERNAL RECOVERY
    lochia_flow = Column(String)
    lochia_color = Column(String)
    perineal_pain = Column(String)
    uterine_pain = Column(String)
    breast_engorgement = Column(String)
    nipple_pain = Column(String)
    c_section_pain = Column(String)
    incision_redness = Column(Boolean, default=False)
    incision_discharge = Column(Boolean, default=False)
    
    # Vital Signs
    maternal_temperature = Column(String)
    blood_pressure_systolic = Column(String)
    blood_pressure_diastolic = Column(String)
    maternal_heart_rate = Column(String)
    
    # Mental Health (EPDS)
    mood_laugh = Column(String)
    mood_anxious = Column(String)
    mood_blame = Column(String)
    mood_panic = Column(String)
    mood_sleep = Column(String)
    mood_sad = Column(String)
    mood_crying = Column(String)
    mood_harm = Column(String)
    
    # INFANT CARE
    feeding_method = Column(String)
    feeding_frequency = Column(Integer, default=0)
    feeding_duration = Column(String)
    latching_quality = Column(String)
    
    wet_diapers = Column(Integer, default=0)
    soiled_diapers = Column(Integer, default=0)
    stool_color = Column(String)
    stool_consistency = Column(String)
    
    infant_temperature = Column(String)
    infant_heart_rate = Column(String)
    jaundice_level = Column(String)
    umbilical_cord = Column(String)
    skin_condition = Column(String)
    
    infant_alertness = Column(String)
    sleep_pattern = Column(String)
    crying_level = Column(String)
    
    # GENERAL
    maternal_energy = Column(String)
    support_system = Column(String)
    additional_notes = Column(Text)
    status = Column(String)
    submitted_at = Column(DateTime)
    urgency_status = Column(String, default='low')
    days_postpartum = Column(Integer, default=0)


class PostnatalProfile(Base):
    __tablename__ = "postnatal_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    delivery_date = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False)
    infant_name = Column(String, nullable=False)
    infant_birth_weight = Column(String)
    infant_birth_date = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())