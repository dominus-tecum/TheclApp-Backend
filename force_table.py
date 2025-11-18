# create_cesarean_only.py
from sqlalchemy import create_engine
from app.health_progress.cesarean.models import Base, CesareanSectionEntry

# Use the same database as your main app
engine = create_engine("sqlite:///./hospiapp.db")

print("🔄 Creating ONLY cesarean_section_entries table...")

# Create just this one table
CesareanSectionEntry.__table__.create(bind=engine, checkfirst=True)

# Verify
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'cesarean_section_entries' in tables:
    print("✅ cesarean_section_entries table created successfully!")
    columns = inspector.get_columns('cesarean_section_entries')
    print("📋 Columns created:")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
else:
    print("❌ Table creation failed!")