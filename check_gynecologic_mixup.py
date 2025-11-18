#!/usr/bin/env python3
"""
Data Testing Script - Analyze gynecologic/urologic data patterns for system testing
NO ASSUMPTIONS - Pure data analysis for testing purposes
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def safe_json_parse(data):
    """Safely parse JSON data that might be stored as string"""
    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    return {}

def analyze_test_data_patterns():
    """Analyze data patterns without making assumptions about correctness"""
    db = SessionLocal()
    try:
        print("🧪 DATA PATTERN ANALYSIS FOR SYSTEM TESTING")
        print("=" * 80)
        
        # Get all data for comprehensive analysis
        gyn_result = db.execute(text("SELECT * FROM gynecologic_surgery_entries"))
        gyn_entries = gyn_result.fetchall()
        
        uro_result = db.execute(text("SELECT * FROM urological_surgery_entries"))
        uro_entries = uro_result.fetchall()
        
        print(f"📊 TEST DATA OVERVIEW:")
        print(f"   Gynecologic entries: {len(gyn_entries)}")
        print(f"   Urologic entries: {len(uro_entries)}")
        print(f"   Total test entries: {len(gyn_entries) + len(uro_entries)}")
        print()
        
        # Analyze patient distribution
        print("👥 PATIENT DISTRIBUTION ANALYSIS:")
        gyn_patients = set(entry.patient_id for entry in gyn_entries)
        uro_patients = set(entry.patient_id for entry in uro_entries)
        common_patients = gyn_patients & uro_patients
        
        print(f"   Unique patients in gynecologic: {len(gyn_patients)}")
        print(f"   Unique patients in urologic: {len(uro_patients)}")
        print(f"   Patients in both tables: {len(common_patients)}")
        print()
        
        # Analyze date patterns
        print("📅 DATE DISTRIBUTION ANALYSIS:")
        gyn_dates = set(entry.submission_date for entry in gyn_entries)
        uro_dates = set(entry.submission_date for entry in uro_entries)
        common_dates = gyn_dates & uro_dates
        
        print(f"   Unique dates in gynecologic: {len(gyn_dates)}")
        print(f"   Unique dates in urologic: {len(uro_dates)}")
        print(f"   Dates with entries in both tables: {len(common_dates)}")
        print()
        
        # Analyze field naming patterns
        print("🔤 FIELD NAMING PATTERN ANALYSIS:")
        if gyn_entries:
            gyn_sample = safe_json_parse(gyn_entries[0].condition_data)
            gyn_camelcase = [f for f in gyn_sample.keys() if any(c.isupper() for c in f[1:]) and '_' not in f]
            gyn_snakecase = [f for f in gyn_sample.keys() if '_' in f]
            print(f"   Gynecologic - CamelCase: {len(gyn_camelcase)}, Snake_case: {len(gyn_snakecase)}")
        
        if uro_entries:
            uro_sample = safe_json_parse(uro_entries[0].condition_data)
            uro_camelcase = [f for f in uro_sample.keys() if any(c.isupper() for c in f[1:]) and '_' not in f]
            uro_snakecase = [f for f in uro_sample.keys() if '_' in f]
            print(f"   Urologic - CamelCase: {len(uro_camelcase)}, Snake_case: {len(uro_snakecase)}")
        print()
        
        # Analyze data completeness
        print("📋 DATA COMPLETENESS ANALYSIS:")
        if gyn_entries:
            gyn_with_data = sum(1 for entry in gyn_entries if entry.condition_data and entry.condition_data != '{}')
            print(f"   Gynecologic entries with condition_data: {gyn_with_data}/{len(gyn_entries)}")
        
        if uro_entries:
            uro_with_data = sum(1 for entry in uro_entries if entry.condition_data and entry.condition_data != '{}')
            print(f"   Urologic entries with condition_data: {uro_with_data}/{len(uro_entries)}")
        print()
            
    except Exception as e:
        print(f"❌ Error in pattern analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def analyze_cross_table_patterns():
    """Analyze patterns across both tables for testing scenarios"""
    db = SessionLocal()
    try:
        print("\n🔍 CROSS-TABLE PATTERN ANALYSIS:")
        print("=" * 80)
        
        # Find patients with entries in both tables (TEST SCENARIO)
        result = db.execute(text("""
            SELECT g.patient_id, g.patient_name, g.submission_date,
                   COUNT(DISTINCT g.id) as gyn_entries,
                   COUNT(DISTINCT u.id) as uro_entries
            FROM gynecologic_surgery_entries g
            JOIN urological_surgery_entries u ON g.patient_id = u.patient_id 
                AND g.submission_date = u.submission_date
            GROUP BY g.patient_id, g.patient_name, g.submission_date
        """))
        
        cross_table_patterns = result.fetchall()
        
        if cross_table_patterns:
            print("🔄 PATTERNS: Patients with entries in BOTH tables (same date):")
            for pattern in cross_table_patterns:
                print(f"   👤 {pattern.patient_name} (ID: {pattern.patient_id})")
                print(f"   📅 {pattern.submission_date}")
                print(f"   🏥 Gynecologic: {pattern.gyn_entries} entries")
                print(f"   💧 Urologic: {pattern.uro_entries} entries")
                print(f"   🧪 TEST SCENARIO: Cross-specialty data entry")
                print("-" * 50)
        else:
            print("✅ No cross-table patterns found")
            
    except Exception as e:
        print(f"❌ Error in cross-table analysis: {e}")
    finally:
        db.close()

def analyze_data_consistency():
    """Analyze data consistency for testing validation"""
    db = SessionLocal()
    try:
        print("\n🔍 DATA CONSISTENCY ANALYSIS:")
        print("=" * 80)
        
        # Check for consistent field usage within each table
        print("📋 GYNECOLOGIC FIELD CONSISTENCY:")
        gyn_result = db.execute(text("""
            SELECT 
                COUNT(*) as total_entries,
                SUM(CASE WHEN condition_data LIKE '%bleedingAmount%' THEN 1 ELSE 0 END) as has_bleeding,
                SUM(CASE WHEN condition_data LIKE '%dischargeColor%' THEN 1 ELSE 0 END) as has_discharge,
                SUM(CASE WHEN condition_data LIKE '%urinaryFrequency%' THEN 1 ELSE 0 END) as has_urinary
            FROM gynecologic_surgery_entries
        """))
        gyn_stats = gyn_result.fetchone()
        print(f"   Total entries: {gyn_stats.total_entries}")
        print(f"   With bleeding data: {gyn_stats.has_bleeding}")
        print(f"   With discharge data: {gyn_stats.has_discharge}") 
        print(f"   With urinary data: {gyn_stats.has_urinary}")
        
        print("\n📋 UROLOGIC FIELD CONSISTENCY:")
        uro_result = db.execute(text("""
            SELECT 
                COUNT(*) as total_entries,
                SUM(CASE WHEN condition_data LIKE '%urine_output%' THEN 1 ELSE 0 END) as has_urine_output,
                SUM(CASE WHEN condition_data LIKE '%urine_color%' THEN 1 ELSE 0 END) as has_urine_color,
                SUM(CASE WHEN condition_data LIKE '%selected_condition%' THEN 1 ELSE 0 END) as has_selected_condition
            FROM urological_surgery_entries
        """))
        uro_stats = uro_result.fetchone()
        print(f"   Total entries: {uro_stats.total_entries}")
        print(f"   With urine output: {uro_stats.has_urine_output}")
        print(f"   With urine color: {uro_stats.has_urine_color}")
        print(f"   With selected_condition: {uro_stats.has_selected_condition}")
        
    except Exception as e:
        print(f"❌ Error in consistency analysis: {e}")
    finally:
        db.close()

def generate_test_scenarios():
    """Generate test scenarios based on actual data patterns"""
    print("\n🧪 TEST SCENARIOS IDENTIFIED:")
    print("=" * 80)
    
    print("1. SINGLE SPECIALTY TESTING")
    print("   - Patient with only gynecologic entries")
    print("   - Patient with only urologic entries")
    print("   - Multiple entries for same patient over time")
    print()
    
    print("2. CROSS-SPECIALTY TESTING") 
    print("   - Patient with entries in both tables")
    print("   - Same-day entries in different specialties")
    print("   - Field naming convention handling")
    print()
    
    print("3. DATA CONSISTENCY TESTING")
    print("   - Mixed field naming (camelCase vs snake_case)")
    print("   - Missing condition_data fields")
    print("   - Data validation across different patterns")
    print()
    
    print("4. SYSTEM INTEGRATION TESTING")
    print("   - Frontend form submission patterns")
    print("   - API endpoint data handling")
    print("   - Database constraint testing")
    print()

def create_test_validation_script():
    """Create a script to validate test data patterns"""
    print("\n🔧 TEST VALIDATION SCRIPT:")
    print("=" * 80)
    
    validation_sql = """
-- TEST DATA VALIDATION QUERIES
-- Use these to validate your test scenarios

-- 1. Validate gynecologic data patterns
SELECT 
    patient_id,
    patient_name,
    COUNT(*) as entry_count,
    MIN(submission_date) as first_entry,
    MAX(submission_date) as last_entry
FROM gynecologic_surgery_entries 
GROUP BY patient_id, patient_name
ORDER BY entry_count DESC;

-- 2. Validate urologic data patterns  
SELECT 
    patient_id,
    patient_name, 
    COUNT(*) as entry_count,
    MIN(submission_date) as first_entry,
    MAX(submission_date) as last_entry
FROM urological_surgery_entries
GROUP BY patient_id, patient_name
ORDER BY entry_count DESC;

-- 3. Cross-specialty validation
SELECT 
    g.patient_id,
    g.patient_name,
    COUNT(DISTINCT g.submission_date) as gyn_dates,
    COUNT(DISTINCT u.submission_date) as uro_dates,
    COUNT(DISTINCT CASE WHEN g.submission_date = u.submission_date THEN g.submission_date END) as same_day_entries
FROM gynecologic_surgery_entries g
LEFT JOIN urological_surgery_entries u ON g.patient_id = u.patient_id
GROUP BY g.patient_id, g.patient_name
HAVING uro_dates > 0;

-- 4. Data completeness check
SELECT 
    'gynecologic' as table_name,
    COUNT(*) as total,
    SUM(CASE WHEN condition_data IS NULL OR condition_data = '{}' THEN 1 ELSE 0 END) as empty_data
FROM gynecologic_surgery_entries
UNION ALL
SELECT 
    'urological' as table_name, 
    COUNT(*) as total,
    SUM(CASE WHEN condition_data IS NULL OR condition_data = '{}' THEN 1 ELSE 0 END) as empty_data
FROM urological_surgery_entries;
"""
    
    print(validation_sql)
    
    # Save to file for later use
    with open('test_validation_queries.sql', 'w') as f:
        f.write(validation_sql)
    print(f"\n💾 Validation queries saved to: test_validation_queries.sql")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE DATA TESTING ANALYSIS")
    print("=" * 80)
    print("🧪 Testing data patterns without assumptions")
    print("📊 Pure analysis for system validation")
    print("=" * 80)
    
    analyze_test_data_patterns()
    analyze_cross_table_patterns() 
    analyze_data_consistency()
    generate_test_scenarios()
    create_test_validation_script()
    
    print("\n🎯 TESTING ANALYSIS COMPLETE!")
    print("=" * 80)
    print("📋 Use these patterns to design comprehensive test cases")
    print("🔧 Use the validation queries to verify test scenarios")
    print("🧪 Continue testing - this is exactly the right approach!")