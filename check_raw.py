import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./hospiapp.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_orthopedic_data_in_db():
    print("🔍 CHECKING RAW ORTHOPEDIC DATA IN DATABASE...")
    
    db = SessionLocal()
    try:
        # Get ALL orthopedic entries with raw JSON data
        result = db.execute(text("""
            SELECT id, patient_id, patient_name, surgery_type, submission_date, 
                   common_data, condition_data, created_at
            FROM orthopedic_surgery_entries 
            ORDER BY id
        """))
        entries = result.fetchall()
        
        print(f"📊 FOUND {len(entries)} ORTHOPEDIC ENTRIES IN DATABASE")
        print("=" * 80)
        
        for entry in entries:
            entry_id, patient_id, patient_name, surgery_type, date, common_json, condition_json, created = entry
            
            print(f"🆔 ENTRY ID: {entry_id}")
            print(f"   Patient: {patient_name} (ID: {patient_id})")
            print(f"   Surgery Type: {surgery_type}")
            print(f"   Date: {date}")
            print(f"   Created: {created}")
            
            # Show RAW JSON data as stored in database
            print(f"   📋 RAW COMMON_DATA (first 200 chars):")
            print(f"      {common_json[:200]}...")
            
            print(f"   📋 RAW CONDITION_DATA (first 200 chars):")
            print(f"      {condition_json[:200]}...")
            
            # Parse and count fields
            try:
                common_data = json.loads(common_json) if common_json else {}
                condition_data = json.loads(condition_json) if condition_json else {}
                
                print(f"   📊 PARSED DATA FIELD COUNTS:")
                print(f"      Common Data: {len(common_data)} fields")
                print(f"      Condition Data: {len(condition_data)} fields")
                
                print(f"   🔍 COMMON DATA FIELDS:")
                for key, value in common_data.items():
                    print(f"      - {key}: {value}")
                
                print(f"   🔍 CONDITION DATA FIELDS:")
                for key, value in condition_data.items():
                    print(f"      - {key}: {value}")
                    
            except Exception as e:
                print(f"   ❌ ERROR PARSING JSON: {e}")
            
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_orthopedic_data_in_db()