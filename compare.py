import requests
import json
from datetime import datetime

# Your backend URL
BASE_URL = "https://d669a8002236.ngrok-free.app"

def test_backend_endpoints():
    """Test what endpoints are available and what they expect"""
    endpoints = [
        "/progress/entries",
        "/progress/entries/5/2025-11-05",
        "/health",
        "/api/auth/me"
    ]
    
    print("🔍 Testing backend endpoints...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"📍 {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def test_submission_with_different_payloads():
    """Test different payload structures to see what the backend accepts"""
    
    # Payload 1: What your frontend is currently sending
    frontend_payload = {
        "patient_id": 5,
        "patient_name": "Test Patient",
        "surgery_type": "cesarean",
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "common_data": {
            "temperature": "37.0",
            "blood_pressure_systolic": "120",
            "blood_pressure_diastolic": "80",
            "heart_rate": "80",
            "respiratory_rate": "16",
            "pain_level": 3
        },
        "condition_data": {
            "fundal_height": "2",
            "uterine_firmness": "firm",
            "lochia_color": "rubra",
            "lochia_amount": "moderate",
            "lochia_odor": "normal",
            "wound_condition": "clean",
            "wound_tenderness": "mild",
            "urine_output": "1500",
            "urinary_retention": False,
            "bowel_sounds": "present",
            "flatus_passed": True,
            "bowel_movement": True,
            "mobility_level": "assisted",
            "ambulation_distance": "room",
            "breastfeeding": True,
            "breast_engorgement": "none",
            "breast_tenderness": "none",
            "nipple_condition": "normal",
            "feeding_frequency": "regular",
            "additional_notes": "Test submission from Python",
            "selected_condition": "cesarean",
            "status": "good"
        }
    }
    
    # Payload 2: Simplified version
    simple_payload = {
        "patient_id": 5,
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "data": frontend_payload  # Nest the entire payload
    }
    
    # Payload 3: Flat structure (no nested common_data/condition_data)
    flat_payload = {
        "patient_id": 5,
        "patient_name": "Test Patient",
        "surgery_type": "cesarean",
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "temperature": "37.0",
        "pain_level": 3,
        "uterine_firmness": "firm",
        "lochia_color": "rubra",
        "status": "good"
    }
    
    payloads = [
        ("Frontend Structure", frontend_payload),
        ("Simple Nested", simple_payload),
        ("Flat Structure", flat_payload)
    ]
    
    print("\n🧪 Testing different payload structures...")
    
    for payload_name, payload in payloads:
        print(f"\n📤 Testing {payload_name}:")
        print(f"   Payload: {json.dumps(payload, indent=2)[:200]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/progress/entries",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS! This payload works")
                return payload  # Return the working payload
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def check_existing_entry():
    """Check if the existing entry endpoint works"""
    print("\n🔍 Checking existing entry endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/progress/entries/5/2025-11-05")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def inspect_backend_response_headers():
    """Check response headers for clues about expected format"""
    print("\n📋 Inspecting response headers...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/progress/entries",
            json={},  # Send empty payload to see error message
            headers={"Content-Type": "application/json"}
        )
        
        print("   Headers:")
        for header, value in response.headers.items():
            print(f"     {header}: {value}")
            
        print(f"   Status: {response.status_code}")
        print(f"   Error message: {response.text}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting backend API investigation...")
    print(f"📡 Base URL: {BASE_URL}")
    
    # 1. Test what endpoints exist
    test_backend_endpoints()
    
    # 2. Check existing entry endpoint
    check_existing_entry()
    
    # 3. Inspect error responses
    inspect_backend_response_headers()
    
    # 4. Test different payload structures
    working_payload = test_submission_with_different_payloads()
    
    if working_payload:
        print(f"\n🎉 Found working payload structure!")
        print(json.dumps(working_payload, indent=2))
    else:
        print(f"\n💥 No payload structure worked. The backend might need different endpoints or authentication.")