from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database_base import Base
import enum

# Define allowed roles
class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    
    # COMMON FIELDS FOR ALL USERS
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    emirates_id = Column(String, nullable=True)
    passport_number = Column(String, nullable=True)
    
    # STAFF-SPECIFIC FIELDS
    specialization = Column(String, nullable=True)
    department = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # EXISTING relationships
    prescriptions = relationship(
        "Prescription", 
        back_populates="user",
        foreign_keys="[Prescription.user_id]"
    )

    appointments = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="[Appointment.user_id]",
        cascade="all, delete-orphan",
    )

    appointments_as_doctor = relationship(
        "Appointment",
        back_populates="doctor",
        foreign_keys="[Appointment.doctor_id]",
        cascade="all, delete-orphan",
    )

    # Helper methods
    def is_doctor(self):
        return self.role == UserRole.DOCTOR
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_patient(self):
        return self.role == UserRole.PATIENT

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    medication = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    issued_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="prescriptions"
    )

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)

    patient = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="appointments"
    )
    doctor = relationship(
        "User",
        foreign_keys=[doctor_id],
        back_populates="appointments_as_doctor"
    )