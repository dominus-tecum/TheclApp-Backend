#!/usr/bin/env python3
"""
INVESTIGATE REAL-TIME DATA MIX-UP: Why console shows wrong data but database is correct
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

def investigate_real_time_mixup():
    """Investigate why console shows mix-up but database doesn't"""
    db = SessionLocal()
    try:
        print("🔍 INVESTIGATING REAL-TIME DATA MIX-UP")
        print("=" * 80)
        
        print("🎯 THE MYSTERY:")
        print("   Console shows: surgery_type: 'urological', conditionType: 'urological'")
        print("   Database shows: surgery_type: 'gynecologic'")
        print("   This suggests DATA TRANSFORMATION during API response")
        print()
        
        # Let's check ALL data to understand what's really happening
        print("1. COMPREHENSIVE DATA AUDIT...")
        
        # Check ALL gynecologic entries
        gyn_result = db.execute(text("SELECT * FROM gynecologic_surgery_entries"))
        gyn_entries = gyn_result.fetchall()
        
        print("📋 ALL GYNECOLOGIC ENTRIES:")
        for entry in gyn_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            print(f"   ID: {entry_dict['id']} | Patient: {entry_dict['patient_name']}")
            print(f"      Surgery Type: {entry_dict.get('surgery_type')}")
            print(f"      Date: {entry_dict.get('submission_date')}")
            print(f"      Has 'selected_condition': {'selected_condition' in condition_data}")
            if 'selected_condition' in condition_data:
                print(f"      selected_condition value: {condition_data['selected_condition']}")
            print(f"      Condition Data Keys: {list(condition_data.keys())[:8]}...")
            print()
        
        # Check ALL urologic entries
        uro_result = db.execute(text("SELECT * FROM urological_surgery_entries"))
        uro_entries = uro_result.fetchall()
        
        print("📋 ALL UROLOGIC ENTRIES:")
        for entry in uro_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            print(f"   ID: {entry_dict['id']} | Patient: {entry_dict['patient_name']}")
            print(f"      Surgery Type: {entry_dict.get('surgery_type')}")
            print(f"      Date: {entry_dict.get('submission_date')}")
            print(f"      Has 'selected_condition': {'selected_condition' in condition_data}")
            if 'selected_condition' in condition_data:
                print(f"      selected_condition value: {condition_data['selected_condition']}")
            print(f"      Condition Data Keys: {list(condition_data.keys())[:8]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error in investigation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_data_transformation():
    """Check if data is being transformed during API response"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING FOR DATA TRANSFORMATION PATTERNS")
        print("=" * 80)
        
        print("🎯 HYPOTHESIS: Backend is TRANSFORMING data before sending to frontend")
        print("   Database stores correctly, but API response is modified")
        print()
        
        # Look for entries that have both gynecologic and urologic characteristics
        print("1. LOOKING FOR HYBRID ENTRIES...")
        
        hybrid_entries = db.execute(text("""
            SELECT id, patient_name, surgery_type, submission_date, condition_data
            FROM gynecologic_surgery_entries 
            WHERE condition_data LIKE '%selected_condition%'
               OR condition_data LIKE '%urine_%'
        """)).fetchall()
        
        if hybrid_entries:
            print("🚨 HYBRID ENTRIES FOUND (might be transformed):")
            for entry in hybrid_entries:
                entry_dict = dict(entry._mapping)
                condition_data = safe_json_parse(entry_dict['condition_data'])
                
                print(f"   📋 Entry ID: {entry_dict['id']}")
                print(f"      Surgery Type: {entry_dict['surgery_type']}")
                print(f"      Has selected_condition: {'selected_condition' in condition_data}")
                print(f"      Has urine fields: {any('urine' in k for k in condition_data.keys())}")
                print(f"      Has bleeding fields: {any('bleeding' in k for k in condition_data.keys())}")
                
        else:
            print("✅ No hybrid entries found")
            
        print("\n2. CHECKING FIELD NAMING INCONSISTENCIES...")
        # Check if field names are being converted
        gyn_sample = db.execute(text("""
            SELECT condition_data FROM gynecologic_surgery_entries LIMIT 1
        """)).fetchone()
        
        if gyn_sample:
            gyn_data = safe_json_parse(gyn_sample[0])
            camel_case = [k for k in gyn_data.keys() if any(c.isupper() for c in k[1:])]
            snake_case = [k for k in gyn_data.keys() if '_' in k]
            
            print(f"   Gynecologic table field patterns:")
            print(f"      CamelCase: {len(camel_case)} fields")
            print(f"      Snake_case: {len(snake_case)} fields")
            if snake_case:
                print(f"      Snake_case examples: {snake_case[:3]}")
                
    except Exception as e:
        print(f"❌ Error checking transformation: {e}")
    finally:
        db.close()

def analyze_api_response_issue():
    """Analyze the API response issue from console logs"""
    print("\n🔍 ANALYZING API RESPONSE ISSUE")
    print("=" * 80)
    
    print("🎯 FROM YOUR CONSOLE LOGS:")
    print("   Entry shows: surgery_type: 'urological', conditionType: 'urological'")
    print("   But database has: surgery_type: 'gynecologic'")
    print()
    
    print("🚨 POSSIBLE CAUSES:")
    print("   1. BACKEND DATA TRANSFORMATION:")
    print("      - API modifies data before sending to frontend")
    print("      - Field name conversion (camelCase ↔ snake_case)")
    print("      - Condition type overriding")
    print()
    print("   2. FRONTEND DATA MAPPING:")
    print("      - Frontend is misinterpreting the API response")
    print("      - Wrong field mapping in frontend components")
    print("      - Cached data showing old values")
    print()
    print("   3. DATABASE VIEWS/TRIGGERS:")
    print("      - Database views that transform data")
    print("      - Triggers that modify data on read")
    print("      - ORM layer transformations")
    print()
    
    print("💡 INVESTIGATION STEPS:")
    print("   1. Check backend API response handlers")
    print("   2. Check frontend data mapping logic")
    print("   3. Check for database views or triggers")
    print("   4. Add debug logging to API endpoints")

def check_for_views_and_triggers():
    """Check if database views or triggers are causing the mix-up"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING FOR DATABASE VIEWS AND TRIGGERS")
        print("=" * 80)
        
        # Check for views (SQLite doesn't support information_schema.views easily)
        print("📋 Checking for potential data transformation layers...")
        
        # Check if there are any triggers
        trigger_check = db.execute(text("""
            SELECT name FROM sqlite_master WHERE type = 'trigger'
        """)).fetchall()
        
        if trigger_check:
            print("🚨 DATABASE TRIGGERS FOUND (might transform data):")
            for trigger in trigger_check:
                print(f"   Trigger: {trigger[0]}")
        else:
            print("✅ No database triggers found")
            
        # Check table structure for clues
        table_info = db.execute(text("""
            SELECT name FROM sqlite_master WHERE type = 'table'
        """)).fetchall()
        
        print(f"📋 All tables: {[t[0] for t in table_info if 'health' in t[0] or 'entry' in t[0]]}")
        
    except Exception as e:
        print(f"❌ Error checking views/triggers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 INVESTIGATING REAL-TIME DATA MIX-UP MYSTERY")
    print("=" * 80)
    print("Why console shows wrong data but database is correct?")
    print("=" * 80)
    
    investigate_real_time_mixup()
    check_data_transformation()
    analyze_api_response_issue()
    check_for_views_and_triggers()
    
    print("\n🎯 CONCLUSION:")
    print("=" * 80)
    print("The mix-up is happening during DATA RETRIEVAL/API RESPONSE, not data storage")
    print("Check: Backend API handlers, Frontend data mapping, Database views/triggers")