# debug_database.py
import sys
import os

# Add your app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def safe_dict_row(row):
    """Safely convert SQLAlchemy row to dictionary"""
    try:
        if hasattr(row, '_asdict'):
            return row._asdict()
        elif hasattr(row, '_mapping'):
            return dict(row._mapping)
        else:
            return dict(row)
    except:
        # Fallback: create dict from row items
        return {key: getattr(row, key) for key in row.keys()}

def check_table_structure(table_name):
    """Check the structure of a table"""
    db = SessionLocal()
    try:
        print(f"\n📋 CHECKING STRUCTURE OF {table_name.upper()}...")
        print("=" * 60)
        
        # Get table structure
        result = db.execute(text(f"PRAGMA table_info({table_name})"))
        columns = []
        for row in result:
            row_dict = safe_dict_row(row)
            columns.append(row_dict)
            print(f"  Column: {row_dict['name']:20} Type: {row_dict.get('type', 'N/A')}")
        
        return columns
        
    except Exception as e:
        print(f"❌ Error checking structure of {table_name}: {str(e)}")
        return []
    finally:
        db.close()

def check_hypertension_data():
    """Check hypertension table"""
    db = SessionLocal()
    try:
        print("\n🫀 CHECKING HYPERTENSION TABLE DATA...")
        print("=" * 60)
        
        # First check structure
        columns = check_table_structure('hypertension_entries')
        
        # Get all hypertension entries
        result = db.execute(text("""
            SELECT * FROM hypertension_entries 
            WHERE patient_id = 5 
            ORDER BY submission_date DESC
        """))
        
        hypertension_entries = []
        for row in result:
            entry = safe_dict_row(row)
            hypertension_entries.append(entry)
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"  Patient: {entry.get('patient_name', 'N/A')}")
            print(f"  Date: {entry.get('submission_date', 'N/A')}")
            print(f"  Common Data: {entry.get('common_data', 'N/A')}")
            print(f"  Condition Data: {entry.get('condition_data', 'N/A')}")
            print()
        
        print(f"📊 Total hypertension entries for patient 5: {len(hypertension_entries)}")
        return hypertension_entries
        
    except Exception as e:
        print(f"❌ Hypertension table error: {str(e)}")
        return []
    finally:
        db.close()

def check_urological_data():
    """Check urological table"""
    db = SessionLocal()
    try:
        print("\n💧 CHECKING UROLOGICAL TABLE DATA...")
        print("=" * 60)
        
        # First check structure
        columns = check_table_structure('urological_surgery_entries')
        
        # Get all urological entries
        result = db.execute(text("""
            SELECT * FROM urological_surgery_entries 
            WHERE patient_id = 5 
            ORDER BY submission_date DESC
        """))
        
        urological_entries = []
        for row in result:
            entry = safe_dict_row(row)
            urological_entries.append(entry)
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"  Patient: {entry.get('patient_name', 'N/A')}")
            print(f"  Date: {entry.get('submission_date', 'N/A')}")
            print(f"  Common Data: {entry.get('common_data', 'N/A')}")
            print(f"  Condition Data: {entry.get('condition_data', 'N/A')}")
            if 'condition_type' in entry:
                print(f"  Condition Type: {entry['condition_type']}")
            if 'surgery_type' in entry:
                print(f"  Surgery Type: {entry['surgery_type']}")
            print()
        
        print(f"📊 Total urological entries for patient 5: {len(urological_entries)}")
        return urological_entries
        
    except Exception as e:
        print(f"❌ Urological table error: {str(e)}")
        return []
    finally:
        db.close()

def check_gynecologic_data():
    """Check gynecologic table"""
    db = SessionLocal()
    try:
        print("\n🌸 CHECKING GYNECOLOGIC TABLE DATA...")
        print("=" * 60)
        
        # First check structure
        columns = check_table_structure('gynecologic_surgery_entries')
        
        # Get all gynecologic entries
        result = db.execute(text("""
            SELECT * FROM gynecologic_surgery_entries 
            WHERE patient_id = 5 
            ORDER BY submission_date DESC
        """))
        
        gynecologic_entries = []
        for row in result:
            entry = safe_dict_row(row)
            gynecologic_entries.append(entry)
            print(f"ID: {entry.get('id', 'N/A')}")
            print(f"  Patient: {entry.get('patient_name', 'N/A')}")
            print(f"  Date: {entry.get('submission_date', 'N/A')}")
            print(f"  Common Data: {entry.get('common_data', 'N/A')}")
            print(f"  Condition Data: {entry.get('condition_data', 'N/A')}")
            if 'condition_type' in entry:
                print(f"  Condition Type: {entry['condition_type']}")
            if 'surgery_type' in entry:
                print(f"  Surgery Type: {entry['surgery_type']}")
            print()
        
        print(f"📊 Total gynecologic entries for patient 5: {len(gynecologic_entries)}")
        return gynecologic_entries
        
    except Exception as e:
        print(f"❌ Gynecologic table error: {str(e)}")
        return []
    finally:
        db.close()

def check_all_tables_simple():
    """Simple check of all tables without complex processing"""
    db = SessionLocal()
    try:
        print("\n🔍 SIMPLE CHECK OF ALL TABLES FOR PATIENT 5...")
        print("=" * 60)
        
        condition_tables = [
            'hypertension_entries',
            'urological_surgery_entries', 
            'gynecologic_surgery_entries',
            'cesarean_section_entries',
            'diabetes_entries',
            'cardiac_surgery_entries',
            'bariatric_entries',
            'burn_care_entries',
            'orthopedic_surgery_entries'
        ]
        
        for table in condition_tables:
            try:
                # Simple count query
                count_result = db.execute(text(f"""
                    SELECT COUNT(*) as count FROM {table} WHERE patient_id = 5
                """))
                count_row = count_result.fetchone()
                count = count_row[0] if count_row else 0
                
                print(f"📋 {table}: {count} entries")
                
                # If entries exist, show basic info
                if count > 0:
                    entries_result = db.execute(text(f"""
                        SELECT id, patient_name, submission_date FROM {table} 
                        WHERE patient_id = 5 
                        ORDER BY submission_date DESC 
                        LIMIT 3
                    """))
                    
                    for row in entries_result:
                        entry = safe_dict_row(row)
                        print(f"  • ID: {entry.get('id', 'N/A')}, Date: {entry.get('submission_date', 'N/A')}")
                
            except Exception as e:
                print(f"  ❌ Error reading {table}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error in simple check: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 STARTING DATABASE DEBUG SCRIPT...")
    
    # First do a simple check of all tables
    check_all_tables_simple()
    
    # Then check specific tables in detail
    print("\n" + "="*80)
    hypertension_data = check_hypertension_data()
    print("\n" + "="*80)
    urological_data = check_urological_data() 
    print("\n" + "="*80)
    gynecologic_data = check_gynecologic_data()
    
    print("\n🎯 SUMMARY:")
    print("=" * 60)
    print(f"Hypertension entries: {len(hypertension_data)}")
    print(f"Urological entries: {len(urological_data)}")
    print(f"Gynecologic entries: {len(gynecologic_data)}")