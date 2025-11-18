from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database_base import Base  # <-- Import Base directly from database_base!
from app.users.users import User

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)     # Patient
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)   # Doctor
    medication = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    issued_date = Column(DateTime, nullable=False)

    patient = relationship("User", foreign_keys=[user_id], back_populates="patient_prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_prescriptions")