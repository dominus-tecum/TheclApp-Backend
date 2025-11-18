#!/usr/bin/env python3
"""
FIND THE ACTUAL DATA MIX-UP: Urological data stored in Gynecologic table
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def safe_json_parse(data):
    if data is None: return {}
    if isinstance(data, dict): return data
    if isinstance(data, str):
        try: return json.loads(data)
        except: return {}
    return {}

def find_misclassified_entries():
    """Find entries that are clearly in the WRONG table"""
    db = SessionLocal()
    try:
        print("🔍 FINDING MISCLASSIFIED ENTRIES (THE ACTUAL MIX-UP)")
        print("=" * 80)
        
        print("1. CHECKING GYNECOLOGIC TABLE FOR UROLOGICAL ENTRIES...")
        gyn_result = db.execute(text("SELECT * FROM gynecologic_surgery_entries"))
        gyn_entries = gyn_result.fetchall()
        
        misclassified = []
        for entry in gyn_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            # Check if this is actually urological data
            has_urologic_data = any(field in condition_data for field in [
                'urine_output', 'urine_color', 'urine_clarity', 'urine_odor', 
                'selected_condition', 'has_catheter', 'catheter_patency'
            ])
            
            has_gynecologic_data = any(field in condition_data for field in [
                'bleedingAmount', 'dischargeColor', 'dischargeOdor', 'dischargeConsistency'
            ])
            
            # If it has urologic data but NO gynecologic data, it's MISCLASSIFIED
            if has_urologic_data and not has_gynecologic_data:
                misclassified.append({
                    'id': entry_dict['id'],
                    'patient_name': entry_dict['patient_name'],
                    'surgery_type': entry_dict.get('surgery_type'),
                    'submission_date': entry_dict.get('submission_date'),
                    'has_urologic_data': has_urologic_data,
                    'has_gynecologic_data': has_gynecologic_data,
                    'urologic_fields': [k for k in condition_data.keys() if any(word in k.lower() for word in ['urine', 'urinary', 'catheter'])],
                    'selected_condition': condition_data.get('selected_condition'),
                    'full_condition_data': condition_data
                })
        
        if misclassified:
            print("🚨 MISCLASSIFIED ENTRIES FOUND IN GYNECOLOGIC TABLE:")
            print("   UROLOGICAL DATA STORED AS GYNECOLOGIC ENTRIES!")
            print()
            
            for wrong in misclassified:
                print(f"📋 Entry ID: {wrong['id']}")
                print(f"   👤 Patient: {wrong['patient_name']}")
                print(f"   📅 Date: {wrong['submission_date']}")
                print(f"   🏷️  Surgery Type: {wrong['surgery_type']}")
                print(f"   ❌ Urologic Fields: {wrong['urologic_fields']}")
                print(f"   🔧 selected_condition: {wrong['selected_condition']}")
                print(f"   📊 Urologic Data Sample:")
                for key in list(wrong['full_condition_data'].keys())[:5]:
                    print(f"      {key}: {wrong['full_condition_data'][key]}")
                print("-" * 60)
        else:
            print("✅ No misclassified entries found")
        
        print("\n2. CHECKING IF THESE SHOULD BE IN UROLOGIC TABLE...")
        # Check if these entries exist in urologic table (they shouldn't)
        for wrong in misclassified:
            uro_check = db.execute(text(f"""
                SELECT id, surgery_type, condition_data 
                FROM urological_surgery_entries 
                WHERE patient_id = 5 AND submission_date = '{wrong['submission_date']}'
            """)).fetchall()
            
            if uro_check:
                print(f"   📅 Date {wrong['submission_date']}: Also exists in urologic table")
                for uro_entry in uro_check:
                    print(f"      Urologic Entry ID: {uro_entry.id}, Type: {uro_entry.surgery_type}")
            else:
                print(f"   📅 Date {wrong['submission_date']}: NOT in urologic table")
                
    except Exception as e:
        print(f"❌ Error finding misclassified entries: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def analyze_mixup_pattern():
    """Analyze the pattern of how the mix-up happens"""
    db = SessionLocal()
    try:
        print("\n🔍 ANALYZING MIX-UP PATTERN")
        print("=" * 80)
        
        print("🎯 THE MIX-UP PATTERN:")
        print("   1. Frontend submits urological data")
        print("   2. Backend stores it in GYNECOLOGIC table") 
        print("   3. But marks it with urological metadata")
        print("   4. Result: Urological data in wrong table")
        print()
        
        # Check the specific entries from your console log
        print("3. VERIFYING CONSOLE LOG ENTRIES...")
        entries_to_check = [1, 2, 3]  # From your console log
        
        for entry_id in entries_to_check:
            result = db.execute(text(f"""
                SELECT id, patient_name, surgery_type, submission_date, condition_data
                FROM gynecologic_surgery_entries 
                WHERE id = {entry_id}
            """)).fetchone()
            
            if result:
                print(f"   📋 Entry ID {entry_id}:")
                print(f"      Patient: {result.patient_name}")
                print(f"      Surgery Type: {result.surgery_type}")
                print(f"      Date: {result.submission_date}")
                
                condition_data = safe_json_parse(result.condition_data)
                if 'selected_condition' in condition_data:
                    print(f"      selected_condition: {condition_data['selected_condition']}")
                print(f"      Is Urological Data: {'urine_output' in condition_data}")
                print(f"      Is Gynecologic Data: {'bleedingAmount' in condition_data}")
                
    except Exception as e:
        print(f"❌ Error analyzing pattern: {e}")
    finally:
        db.close()

def check_burn_care_mixup():
    """Check if burn care is also involved in the mix-up"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING BURN CARE INVOLVEMENT")
        print("=" * 80)
        
        # Check burn care table for misclassified entries
        burn_result = db.execute(text("SELECT * FROM burn_care_entries"))
        burn_entries = burn_result.fetchall()
        
        burn_misclassified = []
        for entry in burn_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            # Check for urological or gynecologic data in burn care
            has_urologic = any(field in condition_data for field in ['urine_output', 'urine_color', 'selected_condition'])
            has_gynecologic = any(field in condition_data for field in ['bleedingAmount', 'dischargeColor'])
            has_burn_care = any(field in condition_data for field in ['burnLocation', 'burnDegree', 'tbsa'])
            
            if (has_urologic or has_gynecologic) and not has_burn_care:
                burn_misclassified.append({
                    'id': entry_dict['id'],
                    'patient_name': entry_dict['patient_name'],
                    'surgery_type': entry_dict.get('surgery_type'),
                    'condition_type': entry_dict.get('condition_type'),
                    'has_urologic': has_urologic,
                    'has_gynecologic': has_gynecologic,
                    'has_burn_care': has_burn_care
                })
        
        if burn_misclassified:
            print("🚨 BURN CARE TABLE ALSO HAS MIX-UP:")
            for wrong in burn_misclassified:
                print(f"   Entry ID: {wrong['id']} - {wrong['patient_name']}")
                print(f"   Surgery: {wrong['surgery_type']}, Condition: {wrong['condition_type']}")
                print(f"   Has Urologic: {wrong['has_urologic']}, Has Gynecologic: {wrong['has_gynecologic']}")
        else:
            print("✅ No mix-up found in burn care table")
            
    except Exception as e:
        print(f"❌ Error checking burn care: {e}")
    finally:
        db.close()

def generate_fix_recommendation():
    """Generate specific fix recommendations"""
    print("\n🎯 FIX RECOMMENDATIONS")
    print("=" * 80)
    
    print("🚨 ROOT CAUSE:")
    print("   API endpoint routing error")
    print("   Urological data being sent to /api/health-progress/gynecologic/entries")
    print()
    
    print("🔧 IMMEDIATE FIXES:")
    print("   1. Check frontend form submission endpoints")
    print("   2. Verify backend route handlers")
    print("   3. Add data validation before saving")
    print("   4. Move misclassified entries to correct tables")
    print()
    
    print("📋 SQL TO MOVE MISCLASSIFIED ENTRIES:")
    print("""
-- Move urological data from gynecologic to urologic table
INSERT INTO urological_surgery_entries (
    patient_id, patient_name, surgery_type, submission_date,
    common_data, condition_data, created_at
)
SELECT 
    patient_id, patient_name, surgery_type, submission_date,
    common_data, condition_data, created_at
FROM gynecologic_surgery_entries 
WHERE condition_data LIKE '%urine_output%' 
   AND condition_data LIKE '%selected_condition%'
   AND condition_data NOT LIKE '%bleedingAmount%';

-- Then delete from gynecologic table
DELETE FROM gynecologic_surgery_entries 
WHERE condition_data LIKE '%urine_output%' 
   AND condition_data LIKE '%selected_condition%'
   AND condition_data NOT LIKE '%bleedingAmount%';
""")

if __name__ == "__main__":
    print("🚀 IDENTIFYING THE ACTUAL DATA MIX-UP")
    print("=" * 80)
    print("Target: Urological data stored in Gynecologic table")
    print("=" * 80)
    
    find_misclassified_entries()
    analyze_mixup_pattern()
    check_burn_care_mixup()
    generate_fix_recommendation()