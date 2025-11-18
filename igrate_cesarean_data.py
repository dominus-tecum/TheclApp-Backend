# migrate_cesarean_data.py
import sys
import os
import sqlalchemy as sa  # ✅ ADD THIS IMPORT

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.health_progress.cesarean.models import CesareanSectionEntry

def migrate_cesarean_data():
    print("🔄 Starting cesarean table migration...")
    
    # Step 1: Drop old table
    try:
        # Check if table exists before dropping
        inspector = sa.inspect(engine)
        if 'cesarean_section_entries' in inspector.get_table_names():
            CesareanSectionEntry.__table__.drop(engine)
            print("✅ Dropped old cesarean table")
        else:
            print("ℹ️  Cesarean table doesn't exist yet")
    except Exception as e:
        print(f"❌ Error dropping table: {e}")
        return
    
    # Step 2: Create new table with JSON columns
    try:
        Base.metadata.create_all(bind=engine, tables=[CesareanSectionEntry.__table__])
        print("✅ Created new cesarean table with JSON columns")
        print("📋 New columns: common_data (JSON), condition_data (JSON)")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return
    
    print("🎉 Migration completed successfully!")
    print("🚨 Note: All existing cesarean data was lost")
    print("💡 New entries will use the JSON column structure")

if __name__ == "__main__":
    migrate_cesarean_data()