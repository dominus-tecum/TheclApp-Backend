import requests
import json
from datetime import datetime

# Your backend URL - UPDATE THIS
BASE_URL = "http://localhost:8000"  # Change to your actual URL

def test_health_progress_endpoints():
    """Test health progress endpoints to understand data structure"""
    print("🔍 Testing Health Progress Endpoints...")
    
    endpoints = [
        "/api/progress/entries",
        "/api/progress/dashboard-stats", 
        "/api/progress/entries?patient_id=1",
        "/api/progress/entries?surgery_type=abdominal"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📍 Testing: {endpoint}")
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"   Array with {len(data)} entries")
                    if len(data) > 0:
                        analyze_entry_structure(data[0], "First Entry")
                elif isinstance(data, dict):
                    print(f"   Object with keys: {list(data.keys())}")
                    if 'entries' in data:
                        print(f"   Has 'entries' array with {len(data['entries'])} items")
                        if len(data['entries']) > 0:
                            analyze_entry_structure(data['entries'][0], "First Entry")
                else:
                    print(f"   Raw response: {str(data)[:200]}...")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def analyze_entry_structure(entry, title="Entry"):
    """Analyze the structure of a single health progress entry"""
    print(f"\n📊 {title} Structure Analysis:")
    print(f"   Type: {type(entry)}")
    print(f"   Keys: {list(entry.keys())}")
    
    # Check for nested structures
    if 'common_data' in entry:
        print("   📦 common_data found:")
        if entry['common_data']:
            print(f"     Keys: {list(entry['common_data'].keys())}")
            for key, value in list(entry['common_data'].items())[:3]:  # Show first 3
                print(f"     {key}: {value} ({type(value)})")
        else:
            print("     (empty)")
    
    if 'condition_data' in entry:
        print("   📦 condition_data found:")
        if entry['condition_data']:
            print(f"     Keys: {list(entry['condition_data'].keys())}")
            for key, value in list(entry['condition_data'].items())[:3]:
                print(f"     {key}: {value} ({type(value)})")
        else:
            print("     (empty)")
    
    # Check for root-level metrics
    root_metrics = ['painLevel', 'temperature', 'dayPostOp', 'fluidIntake', 'urineOutput']
    found_root = []
    for metric in root_metrics:
        if metric in entry and entry[metric] not in [None, '']:
            found_root.append(f"{metric}: {entry[metric]}")
    
    if found_root:
        print("   📍 Root-level metrics found:")
        for metric in found_root:
            print(f"     {metric}")
    else:
        print("   📍 No root-level metrics found")
    
    # Show sample data values
    print(f"\n   📋 Sample Data:")
    for key in ['patient_id', 'patient_name', 'surgery_type', 'status', 'dayPostOp']:
        if key in entry:
            print(f"     {key}: {entry[key]}")
    
    return entry

def create_test_entries():
    """Create test entries with different data structures"""
    print("\n🧪 Creating Test Entries...")
    
    # Test 1: Root-level data structure
    payload1 = {
        "patient_id": 999,
        "patient_name": "Test Patient Root",
        "surgery_type": "abdominal",
        "dayPostOp": 1,
        "painLevel": 4,
        "temperature": 37.2,
        "fluidIntake": 1200,
        "urineOutput": 800,
        "status": "good",
        "additional_notes": "Test entry with root-level data"
    }
    
    # Test 2: Nested data structure
    payload2 = {
        "patient_id": 998,
        "patient_name": "Test Patient Nested", 
        "surgery_type": "cesarean",
        "dayPostOp": 2,
        "common_data": {
            "pain_level": 3,
            "temperature": 36.8,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80
        },
        "condition_data": {
            "lochia_amount": "moderate",
            "uterine_firmness": "firm", 
            "breastfeeding": True,
            "mobility": "with_assistance"
        },
        "status": "monitor",
        "additional_notes": "Test entry with nested data"
    }
    
    # Test 3: Mixed structure
    payload3 = {
        "patient_id": 997,
        "patient_name": "Test Patient Mixed",
        "surgery_type": "orthopedic", 
        "dayPostOp": 3,
        "painLevel": 5,  # Root level
        "common_data": {
            "temperature": 37.1,
            "heart_rate": 85
        },
        "limbColor": "normal",  # Root level surgery-specific
        "distalPulse": "present",  # Root level surgery-specific  
        "status": "good",
        "additional_notes": "Test entry with mixed data"
    }
    
    test_payloads = [
        ("Root-level structure", payload1),
        ("Nested structure", payload2), 
        ("Mixed structure", payload3)
    ]
    
    for test_name, payload in test_payloads:
        print(f"\n📤 Testing: {test_name}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/progress/entries",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Successfully created test entry")
                result = response.json()
                print(f"   Response: {result}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_dashboard_stats():
    """Test the dashboard stats endpoint"""
    print("\n📊 Testing Dashboard Stats...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/progress/dashboard-stats")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   Stats keys: {list(stats.keys())}")
            
            if 'surgery_type_stats' in stats:
                print(f"   Surgery types: {stats['surgery_type_stats']}")
            if 'total_entries' in stats:
                print(f"   Total entries: {stats['total_entries']}")
            if 'urgent_cases' in stats:
                print(f"   Urgent cases: {stats['urgent_cases']}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

def comprehensive_data_analysis():
    """Do a comprehensive analysis of all health progress data"""
    print("\n🔬 Comprehensive Data Analysis...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/progress/entries")
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict) and 'entries' in data:
                entries = data['entries']
            else:
                print("   ❓ Unknown response format")
                return
            
            print(f"   Found {len(entries)} total entries")
            
            # Analyze first 3 entries in detail
            for i, entry in enumerate(entries[:3]):
                analyze_entry_structure(entry, f"Entry {i+1}")
                
            # Count data structures
            root_count = 0
            nested_count = 0 
            mixed_count = 0
            
            for entry in entries:
                has_root = any(key in entry for key in ['painLevel', 'temperature', 'fluidIntake'])
                has_nested = 'common_data' in entry or 'condition_data' in entry
                
                if has_root and has_nested:
                    mixed_count += 1
                elif has_root:
                    root_count += 1
                elif has_nested:
                    nested_count += 1
            
            print(f"\n📈 Data Structure Distribution:")
            print(f"   Root-level only: {root_count}")
            print(f"   Nested only: {nested_count}") 
            print(f"   Mixed: {mixed_count}")
            
        else:
            print(f"   ❌ Failed to fetch entries: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Health Progress Data Structure Investigation")
    print(f"📡 Target: {BASE_URL}")
    print("=" * 60)
    
    # 1. Test all endpoints
    test_health_progress_endpoints()
    
    # 2. Comprehensive analysis of existing data
    comprehensive_data_analysis()
    
    # 3. Test dashboard stats
    test_dashboard_stats()
    
    # 4. Create test entries (optional - comment out if you don't want to create test data)
    # create_test_entries()
    
    print("\n" + "=" * 60)
    print("🎉 Investigation Complete!")
    print("💡 Use the results to fix the getDetailedMetrics function")