#!/usr/bin/env python3
"""
IDENTIFY THREE-WAY DATA MIX-UP: Gynecology, Urology, and Burn Care endpoint confusion
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

def identify_cross_contamination():
    """Identify data mix-up between all three specialty tables"""
    db = SessionLocal()
    try:
        print("🔍 IDENTIFYING THREE-WAY DATA MIX-UP")
        print("=" * 80)
        
        # Define field signatures for each specialty
        specialty_signatures = {
            'gynecologic': ['bleedingAmount', 'dischargeColor', 'dischargeOdor', 'dischargeConsistency', 'clotsPresent', 'clotSize'],
            'urologic': ['urineOutput', 'urineColor', 'urineClarity', 'urineOdor', 'urineDebris', 'selected_condition'],
            'burn_care': ['burnLocation', 'burnDegree', 'burnPercentage', 'tbsa', 'woundCare', 'dressingType', 'burnType']
        }
        
        print("1. CHECKING GYNECOLOGIC TABLE FOR OTHER SPECIALTY DATA...")
        gyn_result = db.execute(text("SELECT * FROM gynecologic_surgery_entries"))
        gyn_entries = gyn_result.fetchall()
        
        contaminated_gyn = []
        for entry in gyn_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            # Check for urologic contamination
            has_urologic = any(field in condition_data for field in specialty_signatures['urologic'])
            # Check for burn care contamination  
            has_burn_care = any(field in condition_data for field in specialty_signatures['burn_care'])
            
            if has_urologic or has_burn_care:
                contaminated_gyn.append({
                    'id': entry_dict['id'],
                    'patient_name': entry_dict['patient_name'],
                    'surgery_type': entry_dict.get('surgery_type'),
                    'has_urologic': has_urologic,
                    'has_burn_care': has_burn_care,
                    'urologic_fields': [f for f in specialty_signatures['urologic'] if f in condition_data],
                    'burn_care_fields': [f for f in specialty_signatures['burn_care'] if f in condition_data],
                    'sample_data': {k: v for k, v in list(condition_data.items())[:3]}
                })
        
        if contaminated_gyn:
            print("🚨 GYNECOLOGIC TABLE CONTAMINATION:")
            for contam in contaminated_gyn:
                print(f"   📋 Entry ID: {contam['id']}")
                print(f"   👤 Patient: {contam['patient_name']}")
                print(f"   🏷️  Surgery Type: {contam['surgery_type']}")
                if contam['has_urologic']:
                    print(f"   ❌ UROLOGIC FIELDS: {contam['urologic_fields']}")
                if contam['has_burn_care']:
                    print(f"   🔥 BURN CARE FIELDS: {contam['burn_care_fields']}")
                print(f"   📊 Sample: {contam['sample_data']}")
                print("-" * 50)
        else:
            print("✅ No contamination found in gynecologic table")
        
        print("\n2. CHECKING UROLOGIC TABLE FOR OTHER SPECIALTY DATA...")
        uro_result = db.execute(text("SELECT * FROM urological_surgery_entries"))
        uro_entries = uro_result.fetchall()
        
        contaminated_uro = []
        for entry in uro_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            # Check for gynecologic contamination
            has_gynecologic = any(field in condition_data for field in specialty_signatures['gynecologic'])
            # Check for burn care contamination
            has_burn_care = any(field in condition_data for field in specialty_signatures['burn_care'])
            
            if has_gynecologic or has_burn_care:
                contaminated_uro.append({
                    'id': entry_dict['id'],
                    'patient_name': entry_dict['patient_name'],
                    'surgery_type': entry_dict.get('surgery_type'),
                    'has_gynecologic': has_gynecologic,
                    'has_burn_care': has_burn_care,
                    'gynecologic_fields': [f for f in specialty_signatures['gynecologic'] if f in condition_data],
                    'burn_care_fields': [f for f in specialty_signatures['burn_care'] if f in condition_data],
                    'sample_data': {k: v for k, v in list(condition_data.items())[:3]}
                })
        
        if contaminated_uro:
            print("🚨 UROLOGIC TABLE CONTAMINATION:")
            for contam in contaminated_uro:
                print(f"   📋 Entry ID: {contam['id']}")
                print(f"   👤 Patient: {contam['patient_name']}")
                print(f"   🏷️  Surgery Type: {contam['surgery_type']}")
                if contam['has_gynecologic']:
                    print(f"   ❌ GYNECOLOGIC FIELDS: {contam['gynecologic_fields']}")
                if contam['has_burn_care']:
                    print(f"   🔥 BURN CARE FIELDS: {contam['burn_care_fields']}")
                print(f"   📊 Sample: {contam['sample_data']}")
                print("-" * 50)
        else:
            print("✅ No contamination found in urologic table")
        
        print("\n3. CHECKING BURN CARE TABLE FOR OTHER SPECIALTY DATA...")
        burn_result = db.execute(text("SELECT * FROM burn_care_entries"))
        burn_entries = burn_result.fetchall()
        
        contaminated_burn = []
        for entry in burn_entries:
            entry_dict = dict(entry._mapping)
            condition_data = safe_json_parse(entry_dict.get('condition_data', '{}'))
            
            # Check for gynecologic contamination
            has_gynecologic = any(field in condition_data for field in specialty_signatures['gynecologic'])
            # Check for urologic contamination
            has_urologic = any(field in condition_data for field in specialty_signatures['urologic'])
            
            if has_gynecologic or has_urologic:
                contaminated_burn.append({
                    'id': entry_dict['id'],
                    'patient_name': entry_dict['patient_name'],
                    'surgery_type': entry_dict.get('surgery_type'),
                    'condition_type': entry_dict.get('condition_type'),
                    'has_gynecologic': has_gynecologic,
                    'has_urologic': has_urologic,
                    'gynecologic_fields': [f for f in specialty_signatures['gynecologic'] if f in condition_data],
                    'urologic_fields': [f for f in specialty_signatures['urologic'] if f in condition_data],
                    'sample_data': {k: v for k, v in list(condition_data.items())[:3]}
                })
        
        if contaminated_burn:
            print("🚨 BURN CARE TABLE CONTAMINATION:")
            for contam in contaminated_burn:
                print(f"   📋 Entry ID: {contam['id']}")
                print(f"   👤 Patient: {contam['patient_name']}")
                print(f"   🏷️  Surgery Type: {contam['surgery_type']}")
                print(f"   🏥 Condition Type: {contam['condition_type']}")
                if contam['has_gynecologic']:
                    print(f"   ❌ GYNECOLOGIC FIELDS: {contam['gynecologic_fields']}")
                if contam['has_urologic']:
                    print(f"   💧 UROLOGIC FIELDS: {contam['urologic_fields']}")
                print(f"   📊 Sample: {contam['sample_data']}")
                print("-" * 50)
        else:
            print("✅ No contamination found in burn care table")
                
    except Exception as e:
        print(f"❌ Error identifying cross-contamination: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_common_data_structure_issues():
    """Check for common data structure problems across all tables"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING COMMON DATA STRUCTURE ISSUES")
        print("=" * 80)
        
        # Check for entries with wrong condition_type or surgery_type
        print("1. CHECKING FOR MISMATCHED CONDITION TYPES...")
        
        # In burn_care_entries, check condition_type vs surgery_type
        burn_mismatch = db.execute(text("""
            SELECT id, patient_name, surgery_type, condition_type
            FROM burn_care_entries 
            WHERE condition_type != 'burn_care' 
               OR surgery_type NOT LIKE '%burn%'
        """))
        
        burn_mismatches = burn_mismatch.fetchall()
        if burn_mismatches:
            print("🚨 BURN CARE ENTRIES WITH WRONG TYPES:")
            for mismatch in burn_mismatches:
                print(f"   ID: {mismatch.id} | Patient: {mismatch.patient_name}")
                print(f"   Surgery: {mismatch.surgery_type} | Condition: {mismatch.condition_type}")
                print("-" * 30)
        else:
            print("✅ No type mismatches in burn care entries")
        
        # Check for entries that might be in wrong table based on data content
        print("\n2. CHECKING FOR OBVIOUSLY MISPLACED ENTRIES...")
        
        # Look for burn care data in other tables
        burn_in_gyn = db.execute(text("""
            SELECT id, patient_name, surgery_type, condition_data
            FROM gynecologic_surgery_entries
            WHERE condition_data LIKE '%burn%' 
               OR condition_data LIKE '%tbsa%'
               OR condition_data LIKE '%dressingType%'
        """))
        
        burn_in_gyn_entries = burn_in_gyn.fetchall()
        if burn_in_gyn_entries:
            print("🚨 BURN CARE DATA IN GYNECOLOGIC TABLE:")
            for entry in burn_in_gyn_entries:
                print(f"   ID: {entry.id} | Patient: {entry.patient_name}")
                print(f"   Surgery: {entry.surgery_type}")
                data = safe_json_parse(entry.condition_data)
                burn_fields = [k for k in data.keys() if 'burn' in k.lower() or 'dressing' in k.lower() or 'tbsa' in k.lower()]
                print(f"   Burn-related fields: {burn_fields}")
                print("-" * 30)
        else:
            print("✅ No burn care data found in gynecologic table")
                
    except Exception as e:
        print(f"❌ Error checking data structure: {e}")
    finally:
        db.close()

def analyze_endpoint_confusion_patterns():
    """Analyze patterns that suggest endpoint confusion"""
    db = SessionLocal()
    try:
        print("\n🔍 ANALYZING ENDPOINT CONFUSION PATTERNS")
        print("=" * 80)
        
        print("1. CHECKING FOR 'selected_condition' FIELD PATTERNS...")
        
        # This field often indicates which frontend form was used
        selected_condition_analysis = db.execute(text("""
            SELECT 
                'gynecologic' as table_name,
                COUNT(*) as total_entries,
                SUM(CASE WHEN condition_data LIKE '%selected_condition%' THEN 1 ELSE 0 END) as has_selected_condition,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"urological"%' THEN 1 ELSE 0 END) as has_urological_value,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"burn_care"%' THEN 1 ELSE 0 END) as has_burn_care_value
            FROM gynecologic_surgery_entries
            UNION ALL
            SELECT 
                'urological' as table_name,
                COUNT(*) as total_entries,
                SUM(CASE WHEN condition_data LIKE '%selected_condition%' THEN 1 ELSE 0 END) as has_selected_condition,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"gynecologic"%' THEN 1 ELSE 0 END) as has_gynecologic_value,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"burn_care"%' THEN 1 ELSE 0 END) as has_burn_care_value
            FROM urological_surgery_entries
            UNION ALL
            SELECT 
                'burn_care' as table_name,
                COUNT(*) as total_entries,
                SUM(CASE WHEN condition_data LIKE '%selected_condition%' THEN 1 ELSE 0 END) as has_selected_condition,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"gynecologic"%' THEN 1 ELSE 0 END) as has_gynecologic_value,
                SUM(CASE WHEN condition_data LIKE '%"selected_condition":"urological"%' THEN 1 ELSE 0 END) as has_urological_value
            FROM burn_care_entries
        """))
        
        selected_results = selected_condition_analysis.fetchall()
        
        print("   SELECTED_CONDITION FIELD ANALYSIS:")
        for result in selected_results:
            print(f"   📋 {result.table_name.upper()} Table:")
            print(f"      Total entries: {result.total_entries}")
            print(f"      Has selected_condition: {result.has_selected_condition}")
            if result.table_name == 'gynecologic':
                print(f"      With 'urological' value: {result.has_urological_value}")
                print(f"      With 'burn_care' value: {result.has_burn_care_value}")
            elif result.table_name == 'urological':
                print(f"      With 'gynecologic' value: {result.has_gynecologic_value}")
                print(f"      With 'burn_care' value: {result.has_burn_care_value}")
            elif result.table_name == 'burn_care':
                print(f"      With 'gynecologic' value: {result.has_gynecologic_value}")
                print(f"      With 'urological' value: {result.has_urological_value}")
            print()
            
    except Exception as e:
        print(f"❌ Error analyzing endpoint patterns: {e}")
    finally:
        db.close()

def generate_mixup_report():
    """Generate final mix-up identification report"""
    print("\n🎯 THREE-WAY DATA MIX-UP REPORT")
    print("=" * 80)
    
    print("🔍 EXPECTED PATTERN:")
    print("   Gynecology → gynecologic_surgery_entries")
    print("   Urology → urological_surgery_entries") 
    print("   Burn Care → burn_care_entries")
    print()
    
    print("🚨 SUSPECTED MIX-UP PATTERN:")
    print("   Some burn care data is being identified as urology/gynecology")
    print("   OR some urology/gynecology data is being routed to burn care")
    print()
    
    print("💡 NEXT STEPS:")
    print("   1. Check frontend form submissions")
    print("   2. Verify API endpoint routing")
    print("   3. Check for shared backend logic between endpoints")
    print("   4. Look for condition_type/surgery_type mismatches")

if __name__ == "__main__":
    print("🚀 IDENTIFYING THREE-WAY ENDPOINT DATA MIX-UP")
    print("=" * 80)
    print("Target: Gynecology, Urology, Burn Care endpoint confusion")
    print("=" * 80)
    
    identify_cross_contamination()
    check_common_data_structure_issues()
    analyze_endpoint_confusion_patterns()
    generate_mixup_report()