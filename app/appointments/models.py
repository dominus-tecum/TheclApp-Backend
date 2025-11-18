from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database_base import Base  # <-- shared Base, always import directly!
from app.models import User   # <-- import User separately

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {"extend_existing": True}  # prevents "table already defined" error

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)    # Patient
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)

    patient = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")