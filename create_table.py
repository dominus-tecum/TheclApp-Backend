# create_orthopedic_table.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Use your database URL
DATABASE_URL = "sqlite:///./hospiapp.db"

Base = declarative_base()

class OrthopedicSurgeryEntry(Base):
    __tablename__ = "orthopedic_surgery_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    surgery_type = Column(String)
    submission_date = Column(String)  # Store as string like "2024-01-15"
    
    common_data = Column(JSON, nullable=False)
    condition_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_orthopedic_table():
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        
        print("🛠️ Creating orthopedic_surgery_entries table...")
        Base.metadata.create_all(bind=engine)
        print("✅ orthopedic_surgery_entries table created successfully!")
        
        # Verify creation
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'orthopedic_surgery_entries' in tables:
            print("🎉 Verification: orthopedic_surgery_entries table exists!")
            print(f"📋 All tables: {tables}")
        else:
            print("❌ Table creation failed!")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_orthopedic_table()