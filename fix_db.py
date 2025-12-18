import sqlite3

DB_PATH = "hospiapp.db"  # Make sure this path is correct

def fix_fertility_profiles_table():
    """Adds period_dates column to fertility_profiles table if it doesn't exist."""
    
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Connected to database successfully.")
        
        # 1. Check current structure of fertility_profiles
        cursor.execute("PRAGMA table_info(fertility_profiles);")
        columns = cursor.fetchall()
        
        print("\nCurrent columns in 'fertility_profiles':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if period_dates already exists
        column_names = [col[1] for col in columns]
        if "period_dates" in column_names:
            print("\n✅ 'period_dates' column already exists. No changes needed.")
            return
        
        # 2. Add the missing column
        print("\nAdding 'period_dates' column...")
        
        # For SQLite, we'll store JSON as TEXT
        # You can also use: TEXT CHECK(json_valid(period_dates))
        cursor.execute("""
            ALTER TABLE fertility_profiles 
            ADD COLUMN period_dates TEXT DEFAULT NULL;
        """)
        
        # 3. Verify the column was added
        cursor.execute("PRAGMA table_info(fertility_profiles);")
        new_columns = cursor.fetchall()
        
        print("\n✅ Column added successfully!")
        print("\nUpdated columns in 'fertility_profiles':")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Commit the changes
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

def check_all_tables():
    """Lists all tables in the database."""
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nAll tables in the database:")
        for table in tables:
            print(f"  - {table[0]}")
            
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Database Fix Script for hospiapp.db")
    print("=" * 50)
    
    # First, show all tables
    check_all_tables()
    
    # Fix the fertility_profiles table
    fix_fertility_profiles_table()