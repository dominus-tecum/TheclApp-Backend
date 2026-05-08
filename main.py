from app.database import engine, Base
from app import models
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
from app.database import engine, Base
from sqlalchemy import inspect
from app.health_progress.urological.models import UrologicalSurgeryEntry
from app.health_progress.gynecologic.models import GynecologicSurgeryEntry
from app.models import User
from app.medical_record.models import MedicalRecord
from app.health_progress.cesarean.models import CesareanSectionEntry
from app.health_progress.hypertension.models import HypertensionEntry
from app.health_progress.diabetes.models import DiabetesEntry
from app.health_progress.orthopedic.models import OrthopedicSurgeryEntry
from app.health_progress.bariatric.models import BariatricEntry
from app.health_progress.burn_care.models import BurnCareEntry
from app.health_progress.general.models import GeneralHealthEntry
from app.health_progress.heart.models import HeartEntry
from app.health_progress.cardiac.models import CardiacSurgeryEntry
from app.health_progress.abdominal.models import AbdominalEntry
from app.health_progress.diabetes.routers import router as diabetes_router
from app.health_progress.hypertension.routers import router as hypertension_router
from app.health_progress.heart.routers import router as heart_router
from app.health_progress.kidney.models import KidneyEntry
from app.health_progress.cancer.models import CancerEntry
from app.health_progress.kidney.routers import router as kidney_router
from app.health_progress.cancer.routers import router as cancer_router
#from app.skin_analysis.skin_prediction import router as skin_analysis_router
from app.prenatal.models import PrenatalEntry
from app.postnatal.models import PostnatalEntry, PostnatalProfile  # ✅ Only once
from app.postnatal.routers import router as postnatal_router  # ✅ Only once
from app.fertility.models import FertilityEntry, FertilityProfile
from app.fertility.routers import router as fertility_router
from fastapi import FastAPI, Request, Depends, HTTPException  # Add Depends, HTTPException
from app.dependencies import get_current_user
from sqlalchemy.orm import Session  # Add this if missing
from app.database import get_db
from app.fertility.services import PatientService, FertilityProfileService
from app.security.routers import router as security_router
from app.fertility.routers import router as fertility_router
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
from app.health_progress.lifelong.routers import router as lifelong_router
from starlette.middleware.sessions import SessionMiddleware
from app.utils.audit import log_audit
from app.routers import router as main_router
from app.health_progress.womens_reproductive.models import WomensHealthIntake, WomensHealthEntry, WomensHealthPhoto
from app.health_progress.womens_reproductive.routers import router as womens_health_router
from app.health_progress.mens_sexual_health.models import MensHealthIntake, MensHealthEntry, MensHealthPhoto
from app.health_progress.mens_sexual_health.routers import router as mens_health_router
from app.models import User
import shutil
import uuid



print("=" * 60)
print("🔍 DEBUG: Importing fertility router")
print(f"🔍 Imported from: app.fertility.routers")
print(f"🔍 Router object: {fertility_router}")
print(f"🔍 Router routes: {[route.path for route in fertility_router.routes]}")
print("=" * 60)



# Create tables
Base.metadata.create_all(bind=engine)

# Create postnatal tables
try:
    PostnatalEntry.__table__.create(engine, checkfirst=True)
    print("✅ postnatal_entries table created successfully")
except Exception as e:
    print(f"⚠️ Postnatal entries table creation note: {e}")

try:
    PostnatalProfile.__table__.create(engine, checkfirst=True)
    print("✅ postnatal_profiles table created successfully")
except Exception as e:
    print(f"⚠️ Postnatal profiles table creation note: {e}")


# ✅ ADD MISSING TABLE CREATIONS HERE:
try:
    OrthopedicSurgeryEntry.__table__.create(engine, checkfirst=True)
    print("✅ orthopedic_surgery_entries table created successfully")
except Exception as e:
    print(f"⚠️ Orthopedic entries table creation note: {e}")

try:
    UrologicalSurgeryEntry.__table__.create(engine, checkfirst=True)
    print("✅ urological_surgery_entries table created successfully")
except Exception as e:
    print(f"⚠️ Urological entries table creation note: {e}")

try:
    GynecologicSurgeryEntry.__table__.create(engine, checkfirst=True)
    print("✅ gynecologic_surgery_entries table created successfully")
except Exception as e:
    print(f"⚠️ Gynecologic entries table creation note: {e}")

try:
    CesareanSectionEntry.__table__.create(engine, checkfirst=True)
    print("✅ cesarean_section_entries table created successfully")
except Exception as e:
    print(f"⚠️ Cesarean entries table creation note: {e}")

try:
    HypertensionEntry.__table__.create(engine, checkfirst=True)
    print("✅ hypertension_entries table created successfully")
except Exception as e:
    print(f"⚠️ Hypertension entries table creation note: {e}")

try:
    DiabetesEntry.__table__.create(engine, checkfirst=True)
    print("✅ diabetes_entries table created successfully")
except Exception as e:
    print(f"⚠️ Diabetes entries table creation note: {e}")

try:
    BariatricEntry.__table__.create(engine, checkfirst=True)
    print("✅ bariatric_entries table created successfully")
except Exception as e:
    print(f"⚠️ Bariatric entries table creation note: {e}")

try:
    BurnCareEntry.__table__.create(engine, checkfirst=True)
    print("✅ burn_care_entries table created successfully")
except Exception as e:
    print(f"⚠️ Burn care entries table creation note: {e}")

try:
    GeneralHealthEntry.__table__.create(engine, checkfirst=True)
    print("✅ general_health_entries table created successfully")
except Exception as e:
    print(f"⚠️ General health entries table creation note: {e}")

try:
    HeartEntry.__table__.create(engine, checkfirst=True)
    print("✅ heart_entries table created successfully")
except Exception as e:
    print(f"⚠️ Heart entries table creation note: {e}")

try:
    KidneyEntry.__table__.create(engine, checkfirst=True)
    print("✅ kidney_entries table created successfully")
except Exception as e:
    print(f"⚠️ Kidney entries table creation note: {e}")

try:
    CancerEntry.__table__.create(engine, checkfirst=True)
    print("✅ cancer_entries table created successfully")
except Exception as e:
    print(f"⚠️ Cancer entries table creation note: {e}")

try:
    PrenatalEntry.__table__.create(engine, checkfirst=True)
    print("✅ prenatal_entries table created successfully")
except Exception as e:
    print(f"⚠️ Prenatal entries table creation note: {e}")


# Add this with your other table creations:
try:
    FertilityEntry.__table__.create(engine, checkfirst=True)
    print("✅ fertility_entries table created successfully")
except Exception as e:
    print(f"⚠️ Fertility entries table creation note: {e}")

try:
    FertilityProfile.__table__.create(engine, checkfirst=True)
    print("✅ fertility_profiles table created successfully")
except Exception as e:
    print(f"⚠️ Fertility profiles table creation note: {e}")

try:
    AbdominalEntry.__table__.create(engine, checkfirst=True)
    print("✅ abdominal_entries table created successfully")
except Exception as e:
    print(f"⚠️ Abdominal entries table creation note: {e}")

try:
    CardiacSurgeryEntry.__table__.create(engine, checkfirst=True)
    print("✅ cardiac_surgery_entries table created successfully")
except Exception as e:
    print(f"⚠️ Cardiac entries table creation note: {e}")

# Add with your other table creations

try:
    WomensHealthIntake.__table__.create(engine, checkfirst=True)
    print("✅ womens_health_intake table created successfully")
except Exception as e:
    print(f"⚠️ Womens health intake table creation note: {e}")

try:
    WomensHealthEntry.__table__.create(engine, checkfirst=True)
    print("✅ womens_health_entries table created successfully")
except Exception as e:
    print(f"⚠️ Womens health entries table creation note: {e}")

try:
    WomensHealthPhoto.__table__.create(engine, checkfirst=True)
    print("✅ womens_health_photos table created successfully")
except Exception as e:
    print(f"⚠️ Womens health photos table creation note: {e}")


try:
    MensHealthIntake.__table__.create(engine, checkfirst=True)
    print("✅ mens_health_intake table created successfully")
except Exception as e:
    print(f"⚠️ Mens health intake table creation note: {e}")

try:
    MensHealthEntry.__table__.create(engine, checkfirst=True)
    print("✅ mens_health_entries table created successfully")
except Exception as e:
    print(f"⚠️ Mens health entries table creation note: {e}")

try:
    MensHealthPhoto.__table__.create(engine, checkfirst=True)
    print("✅ mens_health_photos table created successfully")
except Exception as e:
    print(f"⚠️ Mens health photos table creation note: {e}")

try:
    MensHealthCalibration.__table__.create(engine, checkfirst=True)
    print("✅ mens_health_calibration table created successfully")
except Exception as e:
    print(f"⚠️ Mens health calibration table creation note: {e}")    





# Check users
from app.database import SessionLocal
db = SessionLocal()
users = db.query(User).all()
db.close()    


app = FastAPI(
    title="Healthcare Management API",
    description="A comprehensive healthcare management system with progress tracking, appointments, and medical records",
    version="1.0.0"
)

# Import all routers
from app.authentication.routers import router as auth_router
from app.users.routers import router as users_router
from app.appointments.routers import router as appointments_router
from app.health_progress.routers import router as progress_router
from app.chatbot.routers import router as chatbot_router
from app.telemedicine.transcription import router as transcription_router
from app.symptom_tracker.health_tracker_api import router as health_tracker_router
from app.staff.routers import router as staff_router
from app.prenatal.routers import router as prenatal_router
from app.medical_record.routers import router as medical_record_router
from app.health_progress.abdominal.routers import router as abdominal_router
from app.health_progress.general.routers import router as general_router
from app.health_progress.bariatric.routers import router as bariatric_router
from app.health_progress.burn_care.routers import router as burn_care_router
from app.health_progress.cardiac.routers import router as cardiac_router
from app.health_progress.lifelong.routers import router as lifelong_router
from app.health_progress.cesarean.routers import router as cesarean_router
from app.health_progress.gynecologic.routers import router as gynecologic_router
from app.health_progress.orthopedic.routers import router as orthopedic_router
from app.health_progress.urological.routers import router as urological_router
from app.health_progress.abdominal.models import AbdominalEntry

# CORS middleware for ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

# Create static directories
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js/handlers", exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Create uploads directory for photos
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...), request: Request = None):
    try:
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{unique_filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        base_url = str(request.base_url).rstrip('/')
        file_url = f"{base_url}/uploads/{unique_filename}"
        
        return {"success": True, "url": file_url}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Serve JavaScript handler files
@app.get("/static/js/handlers/{filename}")
async def serve_js_handler(filename: str):
    file_path = f"static/js/handlers/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    else:
        return {"error": f"Handler file {filename} not found"}, 404

# Health endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Healthcare Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "staff_login": "/staff"
    }

@app.get("/api/health-progress/general-entries/{patient_id}/{date}")
async def check_general_entry(
    patient_id: str,
    date: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
):
    try:
        # ← ADD THIS VERIFICATION
        if str(patient_id) != str(current_user.id):
            # ✅ LOG UNAUTHORIZED
            db = SessionLocal()
            log_audit(
                db=db,
                user_id=current_user.id,
                username=current_user.username,
                user_role=current_user.role.value,
                action='READ_DENIED',
                resource_type='HEALTH_PROGRESS',
                patient_id=int(patient_id),
                status='denied',
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent')
            )
            db.close()
            raise HTTPException(status_code=403, detail="Not authorized")
        
        from datetime import datetime
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        db = SessionLocal()
        try:
            existing_entry = db.query(GeneralHealthEntry).filter(
                GeneralHealthEntry.patient_id == patient_id,
                GeneralHealthEntry.submission_date == date
            ).first()
            
            # ✅ LOG SUCCESSFUL ACCESS
            log_audit(
                db=db,
                user_id=current_user.id,
                username=current_user.username,
                user_role=current_user.role.value,
                action='READ',
                resource_type='HEALTH_PROGRESS',
                patient_id=int(patient_id),
                status='success',
                purpose='TREATMENT',
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent')
            )
            
            return {
                "exists": existing_entry is not None,
                "data": {
                    "id": existing_entry.id if existing_entry else None,
                    "patient_id": existing_entry.patient_id if existing_entry else None,
                    "patient_name": existing_entry.patient_name if existing_entry else None,
                    "submission_date": existing_entry.submission_date if existing_entry else None,
                    "common_data": existing_entry.common_data if existing_entry else None,
                    "condition_data": existing_entry.condition_data if existing_entry else None,
                    "status": existing_entry.status if existing_entry else None,
                    "created_at": existing_entry.created_at if existing_entry else None
                } if existing_entry else None
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        return {"exists": False, "error": "Internal server error"}

#=======================================================
#     TEST ENDPOINT
#===========================================================

@app.post("/create-patients-table")
def create_patients_table():
    import sqlite3
    
    conn = sqlite3.connect("./hospiapp.db")
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute("""
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            birth_date TEXT,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add your user as patient
    cursor.execute("""
        INSERT INTO patients (user_id, name, email, phone_number)
        VALUES (1, 'Achu', 'achu@gmail.com', '+251915652323')
    """)
    
    conn.commit()
    conn.close()
    
    return {"status": "patients table created and user added"}

# ========== ADD GUARD ROUTE HERE ==========
@app.get("/api/patients/search")
def patient_search_guard(
    q: str = "",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle patient search - prevents 'search' from being treated as ID"""
    from app.routers import search_patients
    return search_patients(q, db, current_user)



@app.get("/api/patients/{patient_id}")
def get_patient_main(
    patient_id: str,
    request: Request,  # ← ADD THIS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient profile from unified PatientProfile table"""
    from app.models import PatientProfile
    
    # ← ADD THIS VERIFICATION
    if str(patient_id) != str(current_user.id):
        # ✅ LOG UNAUTHORIZED ACCESS ATTEMPT
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ_DENIED',
            resource_type='PATIENT',
            resource_id=int(patient_id),
            patient_id=int(patient_id),
            status='denied',
            purpose='UNAUTHORIZED',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print(f"🔍 [MAIN-PATIENT] Looking for user_id: {patient_id}")
    
    # Query the unified PatientProfile table by user_id
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == int(patient_id)).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # ✅ LOG SUCCESSFUL ACCESS
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ',
        resource_type='PATIENT',
        resource_id=int(patient_id),
        patient_id=int(patient_id),
        status='success',
        purpose='TREATMENT',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.name,
        "email": patient.email,
        "phone_number": patient.phone_number,
        "birth_date": patient.birth_date,
        "lmp": patient.lmp,
        "edd": patient.edd,
        "delivery_date": patient.delivery_date,
        "delivery_type": patient.delivery_type,
        "baby_name": patient.baby_name,
        "baby_birth_weight": patient.baby_birth_weight,
        "high_risk": patient.high_risk,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at
    }

     # Add this function BEFORE the patient endpoint


@app.get("/staff/health-progress", response_class=HTMLResponse, tags=["Staff Web"])
async def staff_health_progress(request: Request):
                     
    base_url = str(request.base_url).rstrip('/')
             

from fastapi.staticfiles import StaticFiles

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard")
async def serve_dashboard():
    with open("static/clinic-dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/admin")
async def serve_admin_dashboard():
    with open("static/admin-dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Include all your existing routers (no debug prints)

app.include_router(main_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(appointments_router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(progress_router)
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(transcription_router, prefix="/api/telemedicine", tags=["Telemedicine"])
app.include_router(health_tracker_router, prefix="/api/health-tracker", tags=["Health Tracker"])
app.include_router(staff_router, prefix="/staff", tags=["Staff Pages"])
app.include_router(medical_record_router, prefix="/api/medical-record", tags=["Medical Record"])
app.include_router(abdominal_router, prefix="/api/progress", tags=["Progress"])
app.include_router(general_router, prefix="/api/health-progress/general", tags=["general-health"])
app.include_router(bariatric_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(burn_care_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(cardiac_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(cesarean_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(gynecologic_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(orthopedic_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(urological_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(lifelong_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(diabetes_router, prefix="/api/health-progress/diabetes", tags=["diabetes"])
app.include_router(hypertension_router, prefix="/api/health-progress/hypertension", tags=["hypertension"])
#app.include_router(skin_analysis_router, prefix="/api/skin-analysis", tags=["Skin Analysis"]) 
app.include_router(heart_router, prefix="/api/health-progress/heart", tags=["Heart Disease"])
app.include_router(kidney_router, prefix="/api/health-progress/kidney", tags=["Kidney Disease"])
app.include_router(cancer_router, prefix="/api/health-progress/cancer", tags=["Cancer"])
app.include_router(prenatal_router, prefix="/api/prenatal", tags=["Prenatal"])
app.include_router(postnatal_router, prefix="/api/postnatal", tags=["Postnatal"])
app.include_router(fertility_router, prefix="/api/fertility", tags=["Fertility"])
app.include_router(security_router, tags=["Security"])
app.include_router(lifelong_router, prefix="/api")
app.include_router(womens_health_router, prefix="/api/womens-reproductive-health", tags=["Women's Reproductive Health"])
app.include_router(mens_health_router, prefix="/api/mens-sexual-health", tags=["Men's Sexual Health"])

# Add this RIGHT BEFORE the last line of main.py

@app.on_event("startup")
async def startup_event():
    print("Healthcare Management API starting up...")
    
    # Print all registered routes
    print("\n📋 REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"  {route.path}")
    print()



# Optional events (keep these)


@app.on_event("shutdown")
async def shutdown_event():
    print("Healthcare Management API shutting down...")


