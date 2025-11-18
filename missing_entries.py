import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
import requests

DATABASE_URL = "sqlite:///./hospiapp.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def find_missing_entries():
    print("🔍 FINDING MISSING ORTHOPEDIC ENTRIES...")
    
    db = SessionLocal()
    try:
        # 1. Get ALL orthopedic entries from database
        result = db.execute(text("""
            SELECT id, patient_id, patient_name, submission_date, created_at 
            FROM orthopedic_surgery_entries 
            ORDER BY created_at DESC
        """))
        db_entries = result.fetchall()
        
        print(f"📊 DATABASE HAS {len(db_entries)} ORTHOPEDIC ENTRIES")
        
        # 2. Get what the API endpoint returns
        print("\n🌐 CHECKING API ENDPOINT RESPONSE...")
        try:
            response = requests.get('http://localhost:8000/api/health-entries', timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                api_entries = api_data.get('entries', [])
                
                # Filter only orthopedic entries from API
                api_orthopedic = [e for e in api_entries if e.get('condition_type') == 'orthopedic']
                print(f"📡 API RETURNS {len(api_orthopedic)} ORTHOPEDIC ENTRIES")
                
                # 3. Find missing entries
                db_ids = set(entry[0] for entry in db_entries)  # Database IDs
                api_ids = set(entry.get('id') for entry in api_orthopedic)  # API IDs
                
                missing_ids = db_ids - api_ids
                print(f"\n❌ MISSING ENTRIES: {len(missing_ids)}")
                
                if missing_ids:
                    print("\n📋 DETAILS OF MISSING ENTRIES:")
                    result = db.execute(text(f"""
                        SELECT id, patient_id, patient_name, submission_date, created_at, 
                               common_data, condition_data
                        FROM orthopedic_surgery_entries 
                        WHERE id IN ({','.join(map(str, missing_ids))})
                        ORDER BY created_at DESC
                    """))
                    missing_entries = result.fetchall()
                    
                    for entry in missing_entries:
                        print(f"   --- Missing Entry ID: {entry[0]} ---")
                        print(f"   Patient: {entry[2]} (ID: {entry[1]})")
                        print(f"   Submission Date: {entry[3]}")
                        print(f"   Created: {entry[4]}")
                        
                        # Check data structure issues
                        common_data = entry[5]
                        condition_data = entry[6]
                        
                        print(f"   Common Data Type: {type(common_data)}")
                        print(f"   Condition Data Type: {type(condition_data)}")
                        
                        # Check for NULL or problematic data
                        if common_data is None:
                            print("   ⚠️ COMMON DATA IS NULL")
                        if condition_data is None:
                            print("   ⚠️ CONDITION DATA IS NULL")
                        
                        print()
                
                # 4. Show what API IS returning
                print("\n✅ ENTRIES RETURNED BY API:")
                for entry in api_orthopedic[:5]:  # Show first 5
                    print(f"   ID: {entry.get('id')}, Patient: {entry.get('patient_name')}, Date: {entry.get('created_at')}")
                
                if len(api_orthopedic) > 5:
                    print(f"   ... and {len(api_orthopedic) - 5} more")
                    
            else:
                print(f"❌ API returned status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error calling API: {e}")
        
        # 5. Check for data structure issues in ALL database entries
        print(f"\n🔧 CHECKING DATA STRUCTURE IN DATABASE:")
        result = db.execute(text("""
            SELECT id, patient_name, 
                   json_type(common_data) as common_type,
                   json_type(condition_data) as condition_type,
                   common_data IS NULL as common_null,
                   condition_data IS NULL as condition_null
            FROM orthopedic_surgery_entries 
            ORDER BY id
        """))
        structure_check = result.fetchall()
        
        problematic_entries = []
        for entry in structure_check:
            entry_id, patient, common_type, condition_type, common_null, condition_null = entry
            if common_null or condition_null or common_type != 'object' or condition_type != 'object':
                problematic_entries.append(entry)
                print(f"   ⚠️ Problematic Entry ID: {entry_id}")
                print(f"      Patient: {patient}")
                print(f"      Common Data: NULL={common_null}, Type={common_type}")
                print(f"      Condition Data: NULL={condition_null}, Type={condition_type}")
        
        if not problematic_entries:
            print("   ✅ All entries have proper JSON data structure")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_endpoint_logic():
    """Test the endpoint logic directly"""
    print("\n" + "="*50)
    print("🔍 TESTING ENDPOINT LOGIC DIRECTLY")
    print("="*50)
    
    db = SessionLocal()
    try:
        # Simulate exactly what your endpoint does
        all_entries = []
        
        # Get orthopedic entries using service (like your endpoint does)
        try:
            from app.health_progress.orthopedic.services import OrthopedicProgressService
            orthopedic_service = OrthopedicProgressService(db)
            orthopedic_db_entries = orthopedic_service.get_all_entries()
            
            print(f"🦴 ORTHOPEDIC SERVICE RETURNS: {len(orthopedic_db_entries)} entries")
            
            for i, entry in enumerate(orthopedic_db_entries):
                standardized_entry = {
                    "id": getattr(entry, 'id', 0),
                    "patient_name": getattr(entry, 'patient_name', 'Unknown'),
                    "condition_type": "orthopedic",
                    "created_at": getattr(entry, 'created_at', '2024-01-15T00:00:00'),
                    "common_data": getattr(entry, 'common_data', {}),
                    "condition_data": getattr(entry, 'condition_data', {})
                }
                
                if hasattr(standardized_entry['created_at'], 'isoformat'):
                    standardized_entry['created_at'] = standardized_entry['created_at'].isoformat()
                
                all_entries.append(standardized_entry)
            
            print(f"📨 AFTER PROCESSING: {len(all_entries)} entries")
            
            # Check for any processing errors
            entries_with_issues = []
            for entry in all_entries:
                if not entry.get('id') or not entry.get('patient_name'):
                    entries_with_issues.append(entry)
            
            if entries_with_issues:
                print(f"⚠️  ENTRIES WITH PROCESSING ISSUES: {len(entries_with_issues)}")
                for entry in entries_with_issues:
                    print(f"   Problematic: ID={entry.get('id')}, Name={entry.get('patient_name')}")
                    
        except Exception as e:
            print(f"❌ Service error: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Endpoint simulation error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    find_missing_entries()
    check_endpoint_logic()