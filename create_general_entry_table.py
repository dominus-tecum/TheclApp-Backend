import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Use the same database URL as your main app
DATABASE_URL = "sqlite:///./test.db"  # Change this if your database is different

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define the GeneralHealthEntry model (same as in your models.py)
from sqlalchemy import Column, Integer, String, DateTime, Text

class GeneralHealthEntry(Base):
    __tablename__ = "general_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    submission_date = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    
    # General health specific fields
    health_trend = Column(String(50), nullable=True)
    overall_wellbeing = Column(Integer, nullable=True)
    primary_symptom_severity = Column(Integer, nullable=True)
    primary_symptom_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Condition type and timestamps
    condition_type = Column(String(50), default="general_health")
    submitted_at = Column(DateTime, nullable=True)
    urgency_status = Column(String(50), default="low")

def create_table():
    try:
        # Drop table if exists and create new one
        GeneralHealthEntry.__table__.drop(engine, checkfirst=True)
        GeneralHealthEntry.__table__.create(engine)
        print("✅ general_entries table created successfully!")
        
        # Verify it exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 All tables in database: {tables}")
        
        if 'general_entries' in tables:
            print("🎉 general_entries table verified!")
        else:
            print("❌ general_entries table not found!")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_table()