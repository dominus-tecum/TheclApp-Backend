# clear_database.py
from app.database import engine, Base
from sqlalchemy import inspect

def clear_and_recreate_tables():
    """Clear all tables and recreate them fresh"""
    print("🗑️  CLEARING DATABASE AND RECREATING TABLES")
    print("=" * 50)
    
    # Import ALL models to ensure they're registered
    print("📦 Importing all models...")
    try:
        from app.health_progress.general.models import GeneralHealthEntry
        from app.health_progress.diabetes.models import DiabetesEntry
        from app.health_progress.hypertension.models import HypertensionEntry
        from app.health_progress.heart.models import HeartEntry
        from app.health_progress.cancer.models import CancerEntry
        from app.health_progress.kidney.models import KidneyEntry
        from app.health_progress.abdominal.models import AbdominalEntry
        
        print("✅ All models imported successfully")
    except Exception as e:
        print(f"❌ Error importing models: {e}")
        return
    
    # Drop ALL tables
    print("\n🗑️  Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return
    
    # Create ALL tables fresh
    print("\n🏗️  Creating all tables fresh...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return
    
    # Verify
    print("\n🔍 Verifying new tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        'general_health_entries',
        'diabetes_entries',
        'hypertension_entries',
        'heart_entries', 
        'cancer_entries',
        'kidney_entries',
        'abdominal_entries'
    ]
    
    print("📊 Created tables:")
    for table in sorted(tables):
        status = "✅" if table in expected_tables else "📝"
        print(f"   {status} {table}")
    
    print(f"\n🎉 DATABASE RESET COMPLETE!")
    print("🚀 Your FastAPI server should now work with all new tables!")

if __name__ == "__main__":
    clear_and_recreate_tables()