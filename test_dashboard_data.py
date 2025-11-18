import requests
import json

# Your domain
BASE_URL = "https://64b139983773.ngrok-free.app"

def test_endpoint(endpoint_name, url):
    """Test a single endpoint and analyze its data structure"""
    print(f"\n{'='*60}")
    print(f"TESTING: {endpoint_name}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if 'entries' in data:
            print(f"Number of entries: {len(data['entries'])}")
            
            if data['entries']:
                first_entry = data['entries'][0]
                print(f"\nFirst entry structure:")
                print(f"  - ID: {first_entry.get('id')}")
                print(f"  - Patient: {first_entry.get('patient_name')}")
                print(f"  - Condition Type: {first_entry.get('conditionType', 'NOT SET')}")
                
                # Check common_data
                common_data = first_entry.get('common_data', {})
                print(f"  - Has common_data: {'Yes' if common_data else 'No'}")
                if common_data:
                    print(f"    common_data keys: {list(common_data.keys())}")
                    print(f"    common_data content: {common_data}")
                else:
                    print(f"    common_data is: {common_data}")
                
                # Check condition_data
                condition_data = first_entry.get('condition_data', {})
                print(f"  - Has condition_data: {'Yes' if condition_data else 'No'}")
                if condition_data:
                    print(f"    condition_data keys: {list(condition_data.keys())}")
                    print(f"    condition_data content: {condition_data}")
                else:
                    print(f"    condition_data is: {condition_data}")
                
                # Check for direct fields that should be in common_data
                direct_fields = ['pain_level', 'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic']
                found_direct = []
                for field in direct_fields:
                    if field in first_entry:
                        found_direct.append(field)
                if found_direct:
                    print(f"  ⚠️  WARNING: Found direct fields (should be in common_data): {found_direct}")
                
                # Check for cesarean-specific fields that should be in condition_data
                cesarean_fields = ['uterine_firmness', 'lochia_amount', 'lochia_color', 'wound_condition', 'breastfeeding']
                found_cesarean = []
                for field in cesarean_fields:
                    if field in first_entry:
                        found_cesarean.append(field)
                if found_cesarean:
                    print(f"  ⚠️  WARNING: Found cesarean fields (should be in condition_data): {found_cesarean}")
                
            else:
                print("No entries found!")
        else:
            print("No 'entries' key in response!")
            print(f"Response keys: {list(data.keys())}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")

def compare_entries():
    """Compare data structures between different condition types"""
    print(f"\n{'='*60}")
    print("COMPARING DATA STRUCTURES")
    print('='*60)
    
    endpoints = {
        "Abdominal": f"{BASE_URL}/api/progress/abdominal-entries",
        "Diabetes": f"{BASE_URL}/api/health-progress/diabetes-entries", 
        "Cesarean": f"{BASE_URL}/api/health-progress/cesarean/entries"
    }
    
    structures = {}
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url)
            data = response.json()
            
            if data.get('entries'):
                first_entry = data['entries'][0]
                structures[name] = {
                    'common_data_keys': list(first_entry.get('common_data', {}).keys()),
                    'condition_data_keys': list(first_entry.get('condition_data', {}).keys()),
                    'direct_keys': [k for k in first_entry.keys() if k not in ['common_data', 'condition_data', 'id', 'patient_id', 'patient_name', 'created_at']]
                }
                
        except Exception as e:
            print(f"Error testing {name}: {e}")
    
    # Print comparison
    print("\nCOMPARISON RESULTS:")
    for name, structure in structures.items():
        print(f"\n{name}:")
        print(f"  common_data keys: {structure['common_data_keys']}")
        print(f"  condition_data keys: {structure['condition_data_keys']}")
        if structure['direct_keys']:
            print(f"  ⚠️  Direct keys (PROBLEM): {structure['direct_keys']}")

def test_specific_cesarean_fields():
    """Test if cesarean-specific fields exist in the data"""
    print(f"\n{'='*60}")
    print("TESTING CESAREAN-SPECIFIC FIELDS")
    print('='*60)
    
    url = f"{BASE_URL}/api/health-progress/cesarean/entries"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('entries'):
            first_entry = data['entries'][0]
            condition_data = first_entry.get('condition_data', {})
            
            cesarean_fields = {
                'uterine_firmness': 'Uterine Firmness',
                'lochia_amount': 'Lochia Amount', 
                'lochia_color': 'Lochia Color',
                'wound_condition': 'Wound Condition',
                'breastfeeding': 'Breastfeeding',
                'mobility_level': 'Mobility Level'
            }
            
            print("Cesarean-specific fields found in condition_data:")
            for field, description in cesarean_fields.items():
                exists = field in condition_data
                value = condition_data.get(field, 'NOT FOUND')
                status = "✅" if exists else "❌"
                print(f"  {status} {description}: {value}")
                
            if not any(field in condition_data for field in cesarean_fields.keys()):
                print("\n🚨 CRITICAL: No cesarean-specific fields found in condition_data!")
                print("This is why the dashboard shows abdominal metrics for cesarean entries.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("DASHBOARD DATA STRUCTURE TESTER")
    print("This will help identify why cesarean entries show abdominal metrics")
    
    # Test each endpoint
    test_endpoint("ABDOMINAL", f"{BASE_URL}/api/progress/abdominal-entries")
    test_endpoint("DIABETES", f"{BASE_URL}/api/health-progress/diabetes-entries")
    test_endpoint("CESAREAN", f"{BASE_URL}/api/health-progress/cesarean/entries")
    
    # Compare structures
    compare_entries()
    
    # Test cesarean-specific fields
    test_specific_cesarean_fields()
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print("If cesarean entries don't have proper condition_data with cesarean-specific")
    print("fields, the dashboard will fall back to showing abdominal metrics.")
    print("Check your cesarean router's get_all_cesarean_entries function.")
    print('='*60)