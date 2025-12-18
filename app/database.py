from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import Patient's Base
from app.fertility.models import Base

DATABASE_URL = "sqlite:///./hospiapp.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# IMPORT ALL MODELS that use this Base
from app.fertility.models import Patient, FertilityEntry, FertilityProfile, CycleAnalysis, FertilityInsight
# Add other model imports if they use the same Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables for ALL imported models
Base.metadata.create_all(bind=engine)