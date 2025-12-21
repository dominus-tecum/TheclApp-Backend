# app/seed_staging.py
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Prescription, Appointment, UserRole
from app.fertility.models import Patient, FertilityEntry, FertilityProfile
from datetime import datetime, timedelta
import random
import hashlib

import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (matching backend)"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode('utf-8')

def seed_staging_data():
    """Populate staging database with safe, synthetic test data"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding staging database with test data...")
        
        # ========== CREATE TEST USERS ==========
        test_users = [
            {
                "email": "health_tester@test.com",
                "username": "health_tester",
                "password_hash": hash_password("Test123!"),
                "name": "Health Tester",
                "phone_number": "+1234567890",
                "emirates_id": "784-1990-1234567-1",
                "passport_number": "A12345678",
                "role": UserRole.PATIENT,
                "is_active": True
            },
            {
                "email": "doctor_test@test.com",
                "username": "doctor_test",
                "password_hash": hash_password("Doctor123!"),
                "name": "Dr. Test Smith",
                "phone_number": "+1987654321",
                "emirates_id": "784-1985-7654321-2",
                "passport_number": "B87654321",
                "role": UserRole.DOCTOR,
                "specialization": "General Medicine",
                "department": "Cardiology",
                "is_active": True
            },
            {
                "email": "admin_test@test.com", 
                "username": "admin_test",
                "password_hash": hash_password("Admin123!"),
                "name": "Admin Tester",
                "phone_number": "+1122334455",
                "emirates_id": "784-1975-1122334-3",
                "passport_number": "C11223344",
                "role": UserRole.ADMIN,
                "is_active": True
            }
        ]
        
        created_users = []
        for user_data in test_users:
            existing = db.query(User).filter_by(email=user_data["email"]).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
                created_users.append(user)
        
        db.commit()
        if created_users:
            print(f"   Created {len(created_users)} test users")
        
        # ========== CREATE TEST PATIENTS ==========
        health_user = db.query(User).filter_by(email="health_tester@test.com").first()
        doctor_user = db.query(User).filter_by(email="doctor_test@test.com").first()
        
        if health_user:
            # Create patient record - USING CORRECT FIELD NAMES FROM YOUR MODEL
            patient = Patient(
                user_id=str(health_user.id),  # String field in your model
                name="Health Tester",
                email="health_tester@test.com",
                birth_date="1990-05-15",  # String format YYYY-MM-DD
                phone_number="+1234567890",
            )
            db.add(patient)
            db.commit()
            
            print(f"   Created patient record for {health_user.email}")
            
            # Generate synthetic fertility data
            print("   Generating synthetic fertility data...")
            
            # Create fertility profile first
            profile = FertilityProfile(
                patient_id=patient.id,
                cycle_length=28,
                period_length=5,
                last_period_date=(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
                typical_cycle_pattern="regular",
                trying_to_conceive=True,
                fertility_issues=[],
                known_conditions=[],
                medications_history=[],
                previous_pregnancies=0,
                previous_births=0,
                previous_miscarriages=0,
                high_risk=False
            )
            db.add(profile)
            db.commit()
            print(f"   Created fertility profile")
            
            # Now create fertility entries
            for day in range(30):
                entry_date = datetime.now() - timedelta(days=30-day)
                
                fertility_entry = FertilityEntry(
                    patient_id=patient.id,
                    patient_name="Health Tester",
                    cycle_day=day + 1,
                    predicted_ovulation_day=14,
                    fertility_window_start=10,
                    fertility_window_end=17,
                    fertility_status="fertile" if 10 <= day <= 17 else "infertile",
                    cycle_phase="follicular" if day < 14 else "luteal",
                    bbt_temperature=round(36.5 + random.uniform(-0.2, 0.3), 1),
                    cervical_fluid_type="creamy",
                    cervical_fluid_amount="moderate",
                    menstrual_flow="light" if day < 5 else None,
                    libido_level="normal",
                    breast_tenderness="mild",
                    ovulation_pain=True if day == 14 else False,
                    mood="happy",
                    energy_level="normal",
                    stress_level="moderate",
                    intercourse_today=random.choice([True, False]),
                    submission_date=entry_date.strftime("%Y-%m-%d"),
                    additional_notes="SYNTHETIC TEST DATA - NOT REAL PATIENT INFORMATION"
                )
                db.add(fertility_entry)
            
            db.commit()
            print(f"   Created 30 synthetic fertility entries")
        
        # ========== CREATE TEST PRESCRIPTIONS ==========
        if health_user and doctor_user:
            prescriptions = [
                {
                    "user_id": health_user.id,
                    "doctor_id": doctor_user.id,
                    "medication": "Test Medication A",
                    "dosage": "10mg",
                    "issued_date": datetime.now(),
                },
                {
                    "user_id": health_user.id,
                    "doctor_id": doctor_user.id,
                    "medication": "Test Vitamin D",
                    "dosage": "1000IU",
                    "issued_date": datetime.now() - timedelta(days=15),
                }
            ]
            
            for rx_data in prescriptions:
                rx = Prescription(**rx_data)
                db.add(rx)
            
            db.commit()
            print(f"   Created 2 test prescriptions")
        
        # ========== CREATE TEST APPOINTMENTS ==========
        if health_user and doctor_user:
            appointments = [
                {
                    "user_id": health_user.id,
                    "doctor_id": doctor_user.id,
                    "appointment_date": datetime.now() + timedelta(days=7),
                    "reason": "Routine checkup (TEST)",
                },
                {
                    "user_id": health_user.id,
                    "doctor_id": doctor_user.id,
                    "appointment_date": datetime.now() + timedelta(days=14),
                    "reason": "Follow-up (TEST)",
                }
            ]
            
            for apt_data in appointments:
                apt = Appointment(**apt_data)
                db.add(apt)
            
            db.commit()
            print(f"   Created 2 test appointments")
        
        print("\n✅ Staging database seeded successfully!")
        print("\n🔐 TEST CREDENTIALS:")
        print("   Patient: health_tester@test.com / Test123!")
        print("   Doctor:  doctor_test@test.com / Doctor123!")
        print("   Admin:   admin_test@test.com / Admin123!")
        print("\n⚠️  REMINDER: All data is SYNTHETIC for testing only")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding staging data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_staging_data()