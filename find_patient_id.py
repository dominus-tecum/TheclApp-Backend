# find_patient_id.py - Find your numeric patient ID using the auth token
import requests
import json

def find_patient_id(auth_token: str):
    base_url = "http://localhost:8000"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    # Try different endpoints that might return patient data
    endpoints_to_try = [
        '/api/auth/me',
        '/api/user/profile', 
        '/api/users/me',
        '/api/patients/me',
        '/api/patients/current',
        '/api/patient'
    ]
    
    print("🔍 Searching for your numeric patient ID...")
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(
                f"{base_url}{endpoint}", 
                headers=headers, 
                timeout=10
            )
            
            print(f"\n📡 GET {endpoint} -> Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Found data at {endpoint}")
                
                # Search for numeric IDs in the response
                numeric_ids = find_numeric_ids(data)
                
                if numeric_ids:
                    print("🎯 Found numeric IDs:")
                    for field_path, value in numeric_ids:
                        print(f"   {field_path}: {value}")
                    
                    # Save the results
                    with open('patient_data.json', 'w') as f:
                        json.dump({
                            'endpoint': endpoint,
                            'data': data,
                            'numeric_ids': numeric_ids
                        }, f, indent=2)
                    print("💾 Patient data saved to 'patient_data.json'")
                    return data
                else:
                    print("📊 Full response data:")
                    print(json.dumps(data, indent=2))
                    
        except Exception as e:
            print(f"❌ {endpoint} -> Error: {e}")
    
    print("\n❌ Could not find patient ID in any endpoint")
    return None

def find_numeric_ids(data, path=""):
    """Recursively find all numeric IDs in the response data"""
    numeric_ids = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            # Look for numeric values in ID fields
            if isinstance(value, int) and any(id_word in key.lower() for id_word in ['id', 'patient', 'user']):
                numeric_ids.append((current_path, value))
            # Recursively search nested objects
            elif isinstance(value, (dict, list)):
                numeric_ids.extend(find_numeric_ids(value, current_path))
    elif isinstance(data, list) and data:
        # Check first item in array
        numeric_ids.extend(find_numeric_ids(data[0], f"{path}[0]"))
    
    return numeric_ids

if __name__ == "__main__":
    # Read the token from the saved file
    try:
        with open('your_token.json', 'r') as f:
            token_data = json.load(f)
        auth_token = token_data.get('access_token')
        
        if auth_token:
            find_patient_id(auth_token)
        else:
            print("❌ No auth token found in your_token.json")
    except FileNotFoundError:
        print("❌ your_token.json not found. Run get_your_token.py first.")