print("=" * 100)
print("✅✅✅ ROUTERS.PY IS LOADED - THIS FILE IS ACTIVE ✅✅✅")
print("=" * 100)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas, database
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
from .authentication.auth import get_current_user
from app.models import User, UserRole
from app.models import PatientDoctorAssignment


# ========== MEDICAL RECORD SCHEMAS ==========

class MedicalRecordCreate(BaseModel):
    patient_id: int
    patient_name: str
    record_type: str
    title: str
    record_date: str
    status: str
    details: Dict[str, Any]
    doctor_name: Optional[str] = None

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    record_type: str
    title: str
    record_date: str
    status: str
    details: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True



router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users/", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
        username=user.username,
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


    # ========== MEDICAL RECORD ENDPOINTS ==========

@router.get("/patients/search")
def search_patients(
    q: str = "",
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(models.User).filter(models.User.role == models.UserRole.PATIENT)
    
    if q and len(q) >= 2:
        query = query.filter(
            (models.User.name.ilike(f"%{q}%")) | 
            (models.User.email.ilike(f"%{q}%"))
        )
    
    patients = query.limit(20).all()
    
    return {
        "patients": [
            {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "phone_number": p.phone_number
            }
            for p in patients
        ]
    }

@router.post("/medical-records", response_model=MedicalRecordResponse, status_code=201)
def create_medical_record(
    record: MedicalRecordCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    patient = db.query(models.User).filter(
        models.User.id == record.patient_id, 
        models.User.role == UserRole.PATIENT
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    doctor = db.query(models.User).filter(models.User.id == current_user.get('id')).first()
    
    db_record = models.MedicalRecord(
        patient_id=record.patient_id,
        patient_name=record.patient_name,
        doctor_id=doctor.id if doctor else None,
        doctor_name=record.doctor_name or (doctor.name if doctor else None),
        record_type=record.record_type,
        title=record.title,
        record_date=record.record_date,
        status=record.status,
        details=record.details
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record

@router.get("/medical-records/patient/{patient_id}")
def get_patient_medical_records(
    patient_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    patient = db.query(models.User).filter(models.User.id == patient_id, models.User.role == UserRole.PATIENT).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    records = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.patient_id == patient_id
    ).order_by(models.MedicalRecord.record_date.desc()).all()
    
    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email
        },
        "records": records,
        "total": len(records)
    }

@router.delete("/medical-records/{record_id}")
def delete_medical_record(
    record_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    
    return {"message": "Record deleted successfully"}

@router.get("/doctors/search")
def search_doctors(
    q: str = "",
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(models.User).filter(models.User.role == UserRole.DOCTOR)
    
    if q and len(q) >= 2:
        query = query.filter(
            (models.User.name.ilike(f"%{q}%")) | 
            (models.User.email.ilike(f"%{q}%"))
        )
    
    doctors = query.all()
    
    return {
        "doctors": [
            {
                "id": d.id,
                "name": d.name,
                "email": d.email,
                "specialization": d.specialization,
                "department": d.department,
                "phone_number": d.phone_number,
                "is_active": d.is_active,
                "description": d.description,
                "education": d.education,
                "experience_years": d.experience_years
            }
            for d in doctors
        ]
    }



@router.get("/patients/{patient_id}/current-doctor")
def get_patient_current_doctor(
    patient_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    assignment = db.query(PatientDoctorAssignment).filter(
        PatientDoctorAssignment.patient_id == patient_id,
        PatientDoctorAssignment.end_date == None
    ).first()
    
    if not assignment:
        return {"doctor": None}
    
    doctor = db.query(User).filter(User.id == assignment.doctor_id).first()
    
    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "specialization": doctor.specialization
        }
    }

@router.post("/patients/{patient_id}/assign-doctor")
def assign_doctor_to_patient(
    patient_id: int,
    doctor_id: int,
    reason: str = None,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    # End current assignment
    current = db.query(PatientDoctorAssignment).filter(
        PatientDoctorAssignment.patient_id == patient_id,
        PatientDoctorAssignment.end_date == None
    ).first()
    
    if current:
        current.end_date = datetime.now()
    
    # Create new assignment
    new_assignment = PatientDoctorAssignment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        assigned_date=datetime.now(),
        reason=reason
    )
    
    db.add(new_assignment)
    db.commit()
    
    return {"message": "Doctor assigned successfully"}


@router.get("/doctors/{doctor_id}")
def get_doctor_details(
    doctor_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == UserRole.DOCTOR
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "specialization": doctor.specialization,
            "department": doctor.department,
            "phone_number": doctor.phone_number,
            "is_active": doctor.is_active,
            "profile_image": doctor.profile_image,
            "description": doctor.description,
            "education": doctor.education,
            "experience_years": doctor.experience_years
        }
    }

@router.post("/doctors/profile")
def create_doctor_profile(
    doctor_data: dict,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    # Admin only
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == doctor_data.get('email')).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Auto-generate username and password
    email = doctor_data.get('email')
    username = email.split('@')[0]
    password = "Doctor@2024"
    hashed_password = pwd_context.hash(password)
    
    # Create user
    new_user = models.User(
        username=username,
        email=email,
        password_hash=hashed_password,
        name=doctor_data.get('name'),
        phone_number=doctor_data.get('phone_number'),
        role=UserRole.DOCTOR,
        specialization=doctor_data.get('specialization'),
        department=doctor_data.get('department'),
        is_active=True,
        status='approved'
    )
    
    # Add extra fields
    if doctor_data.get('experience_years'):
        new_user.experience_years = doctor_data.get('experience_years')
    if doctor_data.get('education'):
        new_user.education = doctor_data.get('education')
    if doctor_data.get('description'):
        new_user.description = doctor_data.get('description')
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Doctor created successfully", "id": new_user.id}

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    print("\n" + "!" * 50)
    print("UPDATE_USER IS BEING CALLED!")
    print(f"User ID: {user_id}")
    print(f"Data: {user_data}")
    print("!" * 50 + "\n")
    
    # Check if admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Get the user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the fields
    allowed_fields = ['name', 'email', 'phone_number', 'specialization', 'department', 
                      'description', 'education', 'experience_years', 'is_active']
    
    for field in allowed_fields:
        if field in user_data:
            print(f"Updating {field} to: {user_data[field]}")
            setattr(user, field, user_data[field])
    
    # Commit to database
    db.commit()
    db.refresh(user)
    
    print(f"After update - specialization: {user.specialization}, department: {user.department}")
    
    return user