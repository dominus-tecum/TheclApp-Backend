#!/usr/bin/env python3
"""
Script to verify gynecologic and urologic entries in the database
and identify data mix-up issues
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.health_entries import HealthEntry  # Adjust based on your model name

def check_gynecologic_urologic_mixup():
    """Check for data mix-up between gynecologic and urologic entries"""
    db = SessionLocal()
    try:
        print("🔍 CHECKING GYNECOLOGIC/UROLOGIC DATA MIX-UP...")
        print("=" * 80)
        
        # Get all health entries
        entries = db.query(HealthEntry).all()
        
        print(f"📊 Total health entries in database: {len(entries)}")
        print()
        
        mixed_entries = []
        gynecologic_entries = []
        urologic_entries = []
        other_entries = []
        
        if entries:
            for i, entry in enumerate(entries, 1):
                # Determine entry type
                condition_type = getattr(entry, 'condition_type', None) or getattr(entry, 'conditionType', None)
                surgery_type = getattr(entry, 'surgery_type', None) or getattr(entry, 'surgeryType', None)
                
                entry_info = {
                    'id': entry.id,
                    'patient_id': getattr(entry, 'patient_id', 'N/A'),
                    'patient_name': getattr(entry, 'patient_name', 'N/A'),
                    'condition_type': condition_type,
                    'surgery_type': surgery_type,
                    'submission_date': getattr(entry, 'submission_date', 'N/A'),
                    'has_gynecologic_data': False,
                    'has_urologic_data': False,
                    'data_mismatch': False,
                    'mismatch_reason': None
                }
                
                # Check condition_data structure
                condition_data = getattr(entry, 'condition_data', {})
                if isinstance(condition_data, dict):
                    # Check for gynecologic fields
                    gynecologic_fields = ['bleedingAmount', 'dischargeColor', 'dischargeOdor', 'dischargeConsistency', 'clotsPresent', 'clotSize']
                    entry_info['has_gynecologic_data'] = any(field in condition_data for field in gynecologic_fields)
                    
                    # Check for urologic fields  
                    urologic_fields = ['urineOutput', 'urineColor', 'urineClarity', 'urineOdor', 'urineDebris']
                    entry_info['has_urologic_data'] = any(field in condition_data for field in urologic_fields)
                
                # Check for data mismatch
                if condition_type == 'gynecologic' and entry_info['has_urologic_data']:
                    entry_info['data_mismatch'] = True
                    entry_info['mismatch_reason'] = 'Gynecologic entry contains urologic data'
                    mixed_entries.append(entry_info)
                elif condition_type == 'urological' and entry_info['has_gynecologic_data']:
                    entry_info['data_mismatch'] = True  
                    entry_info['mismatch_reason'] = 'Urologic entry contains gynecologic data'
                    mixed_entries.append(entry_info)
                elif condition_type == 'gynecologic':
                    gynecologic_entries.append(entry_info)
                elif condition_type == 'urological':
                    urologic_entries.append(entry_info)
                else:
                    other_entries.append(entry_info)
        
        # Print summary
        print("📈 ENTRY SUMMARY:")
        print(f"   Total Gynecologic Entries: {len(gynecologic_entries)}")
        print(f"   Total Urologic Entries: {len(urologic_entries)}")
        print(f"   Total Mixed/Problematic Entries: {len(mixed_entries)}")
        print(f"   Other Entries: {len(other_entries)}")
        print()
        
        # Show mixed entries in detail
        if mixed_entries:
            print("🚨 MIXED DATA ENTRIES FOUND:")
            print("=" * 80)
            for entry in mixed_entries:
                print(f"📋 Entry ID: {entry['id']}")
                print(f"   Patient: {entry['patient_name']} (ID: {entry['patient_id']})")
                print(f"   Condition Type: {entry['condition_type']}")
                print(f"   Surgery Type: {entry['surgery_type']}")
                print(f"   Submission Date: {entry['submission_date']}")
                print(f"   ❌ ISSUE: {entry['mismatch_reason']}")
                
                # Show condition data fields
                condition_data = getattr(db.query(HealthEntry).filter(HealthEntry.id == entry['id']).first(), 'condition_data', {})
                if condition_data:
                    print("   Condition Data Fields:")
                    for key, value in list(condition_data.items())[:8]:  # Show first 8 fields
                        print(f"     {key}: {value}")
                    if len(condition_data) > 8:
                        print(f"     ... and {len(condition_data) - 8} more fields")
                print("-" * 50)
                print()
        
        # Show gynecologic entries
        if gynecologic_entries:
            print("🔬 GYNECOLOGIC ENTRIES ANALYSIS:")
            print("=" * 80)
            for entry in gynecologic_entries[:5]:  # Show first 5
                print(f"🎯 Entry ID: {entry['id']} - {entry['patient_name']}")
                
                condition_data = getattr(db.query(HealthEntry).filter(HealthEntry.id == entry['id']).first(), 'condition_data', {})
                if condition_data:
                    gynecologic_fields_present = [k for k in condition_data.keys() if k in ['bleedingAmount', 'dischargeColor', 'dischargeOdor', 'dischargeConsistency', 'clotsPresent', 'clotSize']]
                    print(f"   Gynecologic Fields: {gynecologic_fields_present}")
                    
                    # Check for any urologic contamination
                    urologic_fields_present = [k for k in condition_data.keys() if k in ['urineOutput', 'urineColor', 'urineClarity', 'urineOdor', 'urineDebris']]
                    if urologic_fields_present:
                        print(f"   ⚠️  Urologic Contamination: {urologic_fields_present}")
                
                print("-" * 50)
            
            if len(gynecologic_entries) > 5:
                print(f"   ... and {len(gynecologic_entries) - 5} more gynecologic entries")
            print()
        
        # Show urologic entries  
        if urologic_entries:
            print("💧 UROLOGIC ENTRIES ANALYSIS:")
            print("=" * 80)
            for entry in urologic_entries[:5]:  # Show first 5
                print(f"🎯 Entry ID: {entry['id']} - {entry['patient_name']}")
                
                condition_data = getattr(db.query(HealthEntry).filter(HealthEntry.id == entry['id']).first(), 'condition_data', {})
                if condition_data:
                    urologic_fields_present = [k for k in condition_data.keys() if k in ['urineOutput', 'urineColor', 'urineClarity', 'urineOdor', 'urineDebris']]
                    print(f"   Urologic Fields: {urologic_fields_present}")
                    
                    # Check for any gynecologic contamination
                    gynecologic_fields_present = [k for k in condition_data.keys() if k in ['bleedingAmount', 'dischargeColor', 'dischargeOdor', 'dischargeConsistency', 'clotsPresent', 'clotSize']]
                    if gynecologic_fields_present:
                        print(f"   ⚠️  Gynecologic Contamination: {gynecologic_fields_present}")
                
                print("-" * 50)
            
            if len(urologic_entries) > 5:
                print(f"   ... and {len(urologic_entries) - 5} more urologic entries")
            print()
        
        # Database schema check
        print("🗄️  DATABASE SCHEMA CHECK:")
        print("=" * 80)
        if entries:
            sample_entry = entries[0]
            print("Available columns in health_entries table:")
            for column in sample_entry.__table__.columns:
                print(f"   {column.name} ({column.type})")
        
        # Field naming analysis
        print()
        print("🔤 FIELD NAMING ANALYSIS:")
        print("=" * 80)
        if entries and hasattr(entries[0], 'condition_data'):
            sample_data = entries[0].condition_data or {}
            camel_case_fields = [k for k in sample_data.keys() if any(c.isupper() for c in k[1:]) and '_' not in k]
            snake_case_fields = [k for k in sample_data.keys() if '_' in k]
            
            print(f"CamelCase fields: {camel_case_fields[:10]}")  # Show first 10
            print(f"Snake_case fields: {snake_case_fields[:10]}")  # Show first 10
            
            if camel_case_fields and snake_case_fields:
                print("❌ FIELD NAMING INCONSISTENCY: Mix of camelCase and snake_case detected!")
            else:
                print("✅ Field naming appears consistent")
        
        # Final summary
        print()
        print("🎯 FINAL DIAGNOSIS:")
        print("=" * 80)
        if mixed_entries:
            print(f"❌ DATA MIX-UP CONFIRMED: {len(mixed_entries)} entries have mixed data types")
            print("   Possible causes:")
            print("   1. Shared backend endpoint handling both condition types")
            print("   2. Incorrect field mapping in API")
            print("   3. Database schema allows mixed data types")
            print("   4. Frontend sending wrong condition_type")
        else:
            print("✅ No data mix-up detected in database entries")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_specific_patient(patient_id):
    """Check entries for a specific patient"""
    db = SessionLocal()
    try:
        print(f"🔍 CHECKING ENTRIES FOR PATIENT {patient_id}...")
        print("=" * 80)
        
        entries = db.query(HealthEntry).filter(HealthEntry.patient_id == patient_id).all()
        
        print(f"📊 Found {len(entries)} entries for patient {patient_id}")
        print()
        
        for entry in entries:
            condition_type = getattr(entry, 'condition_type', None) or getattr(entry, 'conditionType', None)
            surgery_type = getattr(entry, 'surgery_type', None) or getattr(entry, 'surgeryType', None)
            
            print(f"📋 Entry ID: {entry.id}")
            print(f"   Condition Type: {condition_type}")
            print(f"   Surgery Type: {surgery_type}") 
            print(f"   Submission Date: {getattr(entry, 'submission_date', 'N/A')}")
            
            # Show condition data structure
            condition_data = getattr(entry, 'condition_data', {})
            if condition_data:
                print("   Condition Data Fields:")
                for key, value in condition_data.items():
                    print(f"     {key}: {value}")
            else:
                print("   Condition Data: EMPTY")
            
            print("-" * 50)
            print()
            
    except Exception as e:
        print(f"❌ Error checking patient data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Check all entries for mix-up
    check_gynecologic_urologic_mixup()
    
    # Uncomment to check specific patient (replace with actual patient ID)
    # check_specific_patient("your-patient-id-here")