from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Define your database engine first
DATABASE_URL = "sqlite:///./hospiapp.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def diagnose_orthopedic_issue():
    with engine.connect() as conn:
        print("=== ORTHOPEDIC DATA DIAGNOSIS ===")
        
        # Basic counts
        result = conn.execute(text("SELECT COUNT(*) as total FROM orthopedic_surgery_entries"))
        total = result.fetchone()[0]
        print(f"Total orthopedic entries: {total}")
        
        result = conn.execute(text("SELECT COUNT(DISTINCT patient_id) as unique_patients FROM orthopedic_surgery_entries"))
        unique_patients = result.fetchone()[0]
        print(f"Unique patient IDs: {unique_patients}")
        
        # Check for NULL patient IDs
        result = conn.execute(text("SELECT COUNT(*) as null_patients FROM orthopedic_surgery_entries WHERE patient_id IS NULL"))
        null_patients = result.fetchone()[0]
        print(f"Entries with NULL patient_id: {null_patients}")
        
        # Check data recency
        result = conn.execute(text("SELECT MAX(created_at) as latest_entry FROM orthopedic_surgery_entries"))
        latest = result.fetchone()[0]
        print(f"Latest entry: {latest}")
        
        # Check sample data
        result = conn.execute(text("SELECT * FROM orthopedic_surgery_entries LIMIT 5"))
        sample_data = result.fetchall()
        print(f"\nSample orthopedic entries:")
        for row in sample_data:
            print(row)

def check_all_queries():
    """Test different counting methods"""
    print("\n=== TESTING DIFFERENT COUNTING METHODS ===")
    
    queries = [
        ("Simple count", "SELECT COUNT(*) FROM orthopedic_surgery_entries"),
        ("Non-null patient IDs", "SELECT COUNT(*) FROM orthopedic_surgery_entries WHERE patient_id IS NOT NULL"),
        ("Distinct patients", "SELECT COUNT(DISTINCT patient_id) FROM orthopedic_surgery_entries WHERE patient_id IS NOT NULL"),
        ("All distinct patients", "SELECT COUNT(DISTINCT patient_id) FROM orthopedic_surgery_entries"),
    ]
    
    with engine.connect() as conn:
        for description, query in queries:
            result = conn.execute(text(query))
            count = result.fetchone()[0]
            print(f"{description}: {count}")

def check_table_structure():
    """Verify the orthopedic table structure"""
    print("\n=== ORTHOPEDIC TABLE STRUCTURE ===")
    inspector = inspect(engine)
    columns = inspector.get_columns('orthopedic_surgery_entries')
    for col in columns:
        print(f"  {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(not null)'}")

if __name__ == "__main__":
    diagnose_orthopedic_issue()
    check_all_queries()
    check_table_structure()