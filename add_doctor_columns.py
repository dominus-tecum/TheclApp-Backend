# add_doctor_columns.py
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Add description column
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN description TEXT"))
        print("✅ Added description column")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ description column already exists")
        else:
            print(f"❌ Error adding description: {e}")
    
    # Add education column
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN education TEXT"))
        print("✅ Added education column")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ education column already exists")
        else:
            print(f"❌ Error adding education: {e}")
    
    # Add experience_years column
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN experience_years INTEGER DEFAULT 0"))
        print("✅ Added experience_years column")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ experience_years column already exists")
        else:
            print(f"❌ Error adding experience_years: {e}")
    
    conn.commit()

print("\n✅ Column addition complete")