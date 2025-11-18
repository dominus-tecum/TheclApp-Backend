import requests
import json
from datetime import datetime

# Your API base URL
API_BASE_URL = "https://45ff08be8614.ngrok-free.app/api"

def test_daily_entries_endpoint():
    """Test the daily entries endpoint with different data payloads"""
    
    # Test payload 1: Minimal required fields
    payload1 = {
        "patientId": "user_123",
        "patientName": "Test User",
        "surgeryType": "cesarean_section",
        "submissionDate": datetime.now().strftime("%Y-%m-%d"),
        "submittedAt": datetime.now().isoformat(),
        "temperature": 37.0,
        "bloodPressureSystolic": 120,
        "bloodPressureDiastolic": 80,
        "heartRate": 75,
        "respiratoryRate": 16,
        "status": "good"
    }
    
    # Test payload 2: Full data (similar to your React app)
    payload2 = {
        "patientId": "user_123",
        "patientName": "Jane Doe",
        "surgeryType": "cesarean_section",
        "submissionDate": datetime.now().strftime("%Y-%m-%d"),
        "submittedAt": datetime.now().isoformat(),
        "dayPostOp": 5,
        "status": "good",
        
        # Vital Signs
        "temperature": 37.0,
        "bloodPressureSystolic": 120,
        "bloodPressureDiastolic": 80,
        "heartRate": 75,
        "respiratoryRate": 16,
        
        # Uterine Recovery
        "fundalHeight": "2",
        "uterineFirmness": "firm",
        "lochiaColor": "rubra",
        "lochiaAmount": "moderate",
        "lochiaOdor": "normal",
        
        # Incision Site
        "woundCondition": "clean",
        "woundTenderness": "mild",
        
        # Urinary & Bowel
        "urineOutput": 1500,
        "urinaryRetention": False,
        "bowelSounds": "present",
        "flatusPassed": True,
        "bowelMovement": True,
        
        # Pain & Mobility
        "painLevel": 2,
        "mobilityLevel": "assisted",
        "ambulationDistance": "room",
        
        # Breast & Lactation
        "breastfeeding": False,
        "breastEngorgement": "none",
        "breastTenderness": "none",
        "nippleCondition": "normal",
        "feedingFrequency": "none",
        
        "additionalNotes": "Test submission from Python script"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dev-mock-token"
    }
    
    print("🔍 Testing API endpoint...")
    print(f"URL: {API_BASE_URL}/progress/daily-entries")
    
    # Test with minimal payload
    print("\n🧪 TEST 1: Minimal payload")
    print("Payload:", json.dumps(payload1, indent=2))
    
    try:
        response1 = requests.post(
            f"{API_BASE_URL}/progress/daily-entries",
            json=payload1,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response1.status_code}")
        print(f"Response: {response1.text}")
        
        if response1.status_code == 422:
            print("❌ 422 Error - Validation failed")
            try:
                error_data = response1.json()
                print("Error details:", json.dumps(error_data, indent=2))
            except:
                print("Raw error response:", response1.text)
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test with full payload
    print("\n" + "="*50)
    print("🧪 TEST 2: Full payload")
    print("Payload:", json.dumps(payload2, indent=2))
    
    try:
        response2 = requests.post(
            f"{API_BASE_URL}/progress/daily-entries",
            json=payload2,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response2.status_code}")
        print(f"Response: {response2.text}")
        
        if response2.status_code == 422:
            print("❌ 422 Error - Validation failed")
            try:
                error_data = response2.json()
                print("Error details:", json.dumps(error_data, indent=2))
            except:
                print("Raw error response:", response2.text)
        elif response2.status_code == 200:
            print("✅ Success!")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_get_endpoints():
    """Test GET endpoints to see if they work"""
    print("\n" + "="*50)
    print("🧪 Testing GET endpoints...")
    
    endpoints = [
        "/progress/entries",
        "/progress/patients/me/conditions"
    ]
    
    headers = {
        "Authorization": "Bearer dev-mock-token"
    }
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting GET {endpoint}")
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Debug Tests...")
    print(f"API Base URL: {API_BASE_URL}")
    
    test_get_endpoints()
    test_daily_entries_endpoint()