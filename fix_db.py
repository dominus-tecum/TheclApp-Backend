# Updated fix_db.py for Render
import sqlite3
import os

def get_db_path():
    """Find the correct database path on Render"""
    # Check Render's writable /tmp directory first
    render_paths = [
        "/tmp/render.db",
        "/tmp/hospiapp.db",
        "./hospiapp.db",
        "./instance/app.db"
    ]
    
    for path in render_paths:
        if os.path.exists(path):
            print(f"Found database at: {path}")
            return path
    
    # If no existing DB, create in /tmp (Render's writable space)
    print("No existing database found, creating at: /tmp/render.db")
    return "/tmp/render.db"

def create_all_tables():
    """Create ALL database tables from scratch"""
    
    DB_PATH = get_db_path()
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 50)
        print(f"Creating database tables at: {DB_PATH}")
        print("=" * 50)
        
        # 1. PATIENTS TABLE (the missing one!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                birth_date TEXT,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created 'patients' table")
        
        # 2. Fertility profiles (your existing fix)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fertility_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                cycle_length INTEGER DEFAULT 28,
                period_length INTEGER DEFAULT 5,
                last_period_date TEXT,
                period_dates TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        """)
        print("✅ Created 'fertility_profiles' table")
        
        # 3. Add a test patient (user_id = 1 for achu)
        cursor.execute("""
            INSERT OR IGNORE INTO patients (user_id, name, email, phone_number)
            VALUES (1, 'Achu', 'achu@gmail.com', '+251915652323');
        """)
        print("✅ Added test patient 'Achu'")
        
        # Commit changes
        conn.commit()
        
        # Show what was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n" + "=" * 50)
        print(f"Total tables created: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        print("=" * 50)
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_all_tables()