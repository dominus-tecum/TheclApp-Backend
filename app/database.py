from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the SINGLE, SHARED Base that ALL models use
from app.database_base import Base  # <-- CHANGE: Use database_base.Base

DATABASE_URL = "sqlite:///./hospiapp.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ========== IMPORT ALL MODELS THAT USE THIS BASE ==========
# 1. Core models (User, Prescription, Appointment)
from app.models import User, Prescription, Appointment

# 2. Fertility models - MUST FIRST fix app/fertility/models.py:
#    Change line 8 from "Base = declarative_base()" to "from app.database_base import Base"
from app.fertility.models import Patient, FertilityEntry, FertilityProfile, CycleAnalysis, FertilityInsight

# 3. Add other models as needed:
# from app.medical_record.models import MedicalRecord
# from app.other_module.models import OtherModel
# ===========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables for ALL imported models
Base.metadata.create_all(bind=engine)
print(f"✅ Creating tables: {list(Base.metadata.tables.keys())}")