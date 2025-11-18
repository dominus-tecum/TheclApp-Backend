# check_cardiac_table.py
from sqlalchemy import create_engine, inspect
import sys
import os

sys.path.append(os.path.dirname(__file__))

# Use your actual database URL
DATABASE_URL = "sqlite:///./test.db"  # Change to your DB

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

tables = inspector.get_table_names()
print("📊 CURRENT TABLES:", tables)

if 'cardiac_surgery_entries' in tables:
    print("✅ CARDIAC TABLE EXISTS!")
    columns = inspector.get_columns('cardiac_surgery_entries')
    print("📋 COLUMNS:")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
else:
    print("❌ CARDIAC TABLE DOES NOT EXIST")