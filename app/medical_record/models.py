from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
import uuid

# FIX: Use the same Base as other models in your app
from app.database_base import Base  # This matches your other models

def generate_uuid():
    return str(uuid.uuid4())

class MedicalRecord(Base):
    __tablename__ = "medical_record"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "Blood Test", "X-Ray", "Consultation"
    category = Column(String, nullable=False)  # "Lab Results", "Prescriptions", "Medical History"
    doctor = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Store as string for flexibility
    status = Column(String, nullable=False)  # "Active", "Completed", "Pending", etc.
    details = Column(JSON, nullable=False)  # Store structured data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional fields for specific types
    lab_order_id = Column(String, nullable=True)  # For lab results
    prescription_id = Column(String, nullable=True)  # For prescriptions
    appointment_id = Column(String, nullable=True)  # Link to appointments