from sqlalchemy.orm import relationship
from app.database_base import Base
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, JSON, Text


# Define allowed roles
class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"      
    STAFF = "staff"      
    ADMIN = "admin"
    PHARMACY = "pharmacy"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.PATIENT, nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), nullable=True)
    organization = relationship("Organization", backref="users")
    
    # COMMON FIELDS FOR ALL USERS
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    emirates_id = Column(String, nullable=True)
    passport_number = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    education = Column(String, nullable=True)
    experience_years = Column(Integer, default=0)
    
    # STAFF-SPECIFIC FIELDS
    specialization = Column(String, nullable=True)
    department = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", backref="users")

        
    # ✅ ADD THIS LINE - Status for approval workflow
    status = Column(String, default='pending')  # 'pending' or 'approved'
    profile_image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


        # ========== ENCRYPTED FIELDS FOR COMPLIANCE ==========
    # These will store encrypted versions of PII
    name_encrypted = Column(Text, nullable=True)
    email_encrypted = Column(Text, nullable=True)
    phone_encrypted = Column(Text, nullable=True)
    passport_encrypted = Column(Text, nullable=True)
    emirates_id_encrypted = Column(Text, nullable=True)
    
    # Hashed fields for duplicate checking (one-way, cannot be reversed)
    email_hash = Column(String, unique=True, index=True, nullable=True)
    phone_hash = Column(String, unique=True, index=True, nullable=True)
    passport_hash = Column(String, unique=True, index=True, nullable=True)
    emirates_id_hash = Column(String, unique=True, index=True, nullable=True)
    # ===================================================
       
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

    pharmacy = relationship("Pharmacy", back_populates="users")    

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    medication = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    issued_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="prescriptions"
    )

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
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

# In app/models.py, add this:

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    
    # Pregnancy-related (for prenatal)
    lmp = Column(String, nullable=True)  # Last Menstrual Period
    edd = Column(String, nullable=True)  # Expected Due Date
    
    # Postnatal-related
    delivery_date = Column(String, nullable=True)
    delivery_type = Column(String, nullable=True)
    baby_name = Column(String, nullable=True)
    baby_birth_weight = Column(String, nullable=True)
    
    # General
    high_risk = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Add this after your existing classes (after PatientProfile)

class PatientConsent(Base):
    __tablename__ = "patient_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    consent_type = Column(String, nullable=False)  # 'data_collection', 'data_sharing', 'research'
    consent_version = Column(String, nullable=False)  # 'v1.0'
    accepted = Column(Boolean, default=True)
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", backref="consents")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # 'view', 'edit', 'export', 'consent_given', 'login'
    resource_type = Column(String, nullable=True)  # 'patient_profile', 'medical_record', 'consent'
    resource_id = Column(Integer, nullable=True)
    staff_id = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
        # ✅ ADD THESE NEW COLUMNS (keep existing ones above)
    username = Column(String, nullable=True)  # Cache username for quick lookup
    user_role = Column(String, nullable=True)  # Cache role for filtering
    patient_id = Column(Integer, nullable=True, index=True)  # Which patient was accessed
    old_value = Column(String, nullable=True)  # For UPDATE actions (store JSON)
    new_value = Column(String, nullable=True)  # For CREATE/UPDATE actions (store JSON)
    status = Column(String, default='success')  # success, failed, denied
    purpose = Column(String, nullable=True)  # TREATMENT, PAYMENT, OPERATIONS, EMERGENCY
    
    # Relationship
    user = relationship("User", backref="audit_logs")

    # Add this AFTER the AuditLog class (after its closing brace)


class PatientDoctorAssignment(Base):
    __tablename__ = "patient_doctor_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])

class OneTimeToken(Base):
    __tablename__ = "one_time_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    purpose = Column(String, nullable=False)  # 'admin_creation', 'password_reset'
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    license_number = Column(String(100), unique=True, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    subscription_plan = Column(String(50), default='basic')
    subscription_status = Column(String(50), default='trial')
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    max_staff = Column(Integer, default=10)
    max_patients = Column(Integer, default=500)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    allowed_modules = Column(JSON, default=list)  # ← ADD THIS
    type = Column(String, default="hospital")

# ========== PRESCRIPTION VOUCHER SYSTEM ==========
# Add this AFTER your existing Organization class

class PrescriptionVoucher(Base):
    __tablename__ = "prescriptions_voucher"
    
    id = Column(Integer, primary_key=True, index=True)
    prescription_code = Column(String, unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    medication_name = Column(String, nullable=False)
    strength = Column(String, nullable=True)
    dosage = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    status = Column(String, default="active")  # active, shared, sold, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    medical_record_id = Column(String, nullable=True)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])


class PrescriptionShare(Base):
    __tablename__ = "prescription_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions_voucher.id"), nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    share_token = Column(String, unique=True, nullable=False, index=True)
    shared_at = Column(DateTime, default=datetime.utcnow)
    viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)
    sold = Column(Boolean, default=False)
    sold_at = Column(DateTime, nullable=True)
    
    # Relationships
    prescription = relationship("PrescriptionVoucher")
    pharmacy = relationship("Organization")    