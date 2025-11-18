# diagnose_tables.py
from sqlalchemy import create_engine, inspect

engine = create_engine("sqlite:///./hospiapp.db")
inspector = inspect(engine)

print("🔍 CURRENT TABLES IN DATABASE:")
tables = inspector.get_table_names()
for table in tables:
    print(f"  - {table}")

print(f"\n📊 Total tables: {len(tables)}")

if 'cesarean_section_entries' in tables:
    print("✅ cesarean_section_entries table EXISTS")
    columns = inspector.get_columns('cesarean_section_entries')
    print("📋 Columns:")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
else:
    print("❌ cesarean_section_entries table NOT FOUND")