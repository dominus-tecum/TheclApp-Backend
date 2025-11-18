import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./hospiapp.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def analyze_orthopedic_data():
    print("🔍 ANALYZING CURRENT ORTHOPEDIC DATA...")
    
    db = SessionLocal()
    try:
        # Get all orthopedic entries with full details
        result = db.execute(text("""
            SELECT id, patient_id, patient_name, surgery_type, submission_date, 
                   common_data, condition_data, created_at
            FROM orthopedic_surgery_entries 
            ORDER BY created_at DESC
        """))
        entries = result.fetchall()
        
        print(f"📊 TOTAL ORTHOPEDIC ENTRIES: {len(entries)}")
        
        # Show all entries in detail
        print("\n📋 ALL ORTHOPEDIC ENTRIES:")
        print("=" * 80)
        for entry in entries:
            print(f"ID: {entry[0]}")
            print(f"Patient: {entry[2]} (ID: {entry[1]})")
            print(f"Surgery Type: {entry[3]}")
            print(f"Submission Date: {entry[4]}")
            print(f"Created: {entry[7]}")
            
            # Parse JSON data
            try:
                common_data = json.loads(entry[5]) if entry[5] else {}
                print(f"Common Data:")
                for key, value in common_data.items():
                    print(f"  - {key}: {value}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Common Data: ERROR parsing - {e}")
                print(f"  Raw data: {entry[5]}")
            
            try:
                condition_data = json.loads(entry[6]) if entry[6] else {}
                print(f"Condition Data:")
                for key, value in condition_data.items():
                    print(f"  - {key}: {value}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Condition Data: ERROR parsing - {e}")
                print(f"  Raw data: {entry[6]}")
            
            print("-" * 80)
        
        # Check for patterns
        print("\n📈 DATA PATTERNS:")
        
        # Patient distribution
        result = db.execute(text("""
            SELECT patient_id, patient_name, COUNT(*) as entry_count
            FROM orthopedic_surgery_entries 
            GROUP BY patient_id, patient_name
            ORDER BY entry_count DESC
        """))
        patient_dist = result.fetchall()
        
        print("👥 PATIENT DISTRIBUTION:")
        for patient_id, patient_name, count in patient_dist:
            print(f"  - {patient_name} (ID: {patient_id}): {count} entries")
        
        # Date distribution
        result = db.execute(text("""
            SELECT submission_date, COUNT(*) as entry_count
            FROM orthopedic_surgery_entries 
            GROUP BY submission_date
            ORDER BY submission_date DESC
        """))
        date_dist = result.fetchall()
        
        print("\n📅 DATE DISTRIBUTION:")
        for date, count in date_dist:
            print(f"  - {date}: {count} entries")
        
        # Surgery type distribution
        result = db.execute(text("""
            SELECT surgery_type, COUNT(*) as type_count
            FROM orthopedic_surgery_entries 
            GROUP BY surgery_type
            ORDER BY type_count DESC
        """))
        surgery_dist = result.fetchall()
        
        print("\n🦴 SURGERY TYPE DISTRIBUTION:")
        for surgery_type, count in surgery_dist:
            print(f"  - {surgery_type}: {count} entries")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_orthopedic_data()