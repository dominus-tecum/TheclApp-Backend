import requests
import json
from datetime import datetime

BASE_URL = "https://d669a8002236.ngrok-free.app"

def test_abdominal_submission():
    """Test the exact data structure the frontend is now sending"""
    
    print("🧪 TESTING: Abdominal Surgery Data Submission")
    
    # Exact same data structure as your fixed frontend
    abdominal_data = {
        "patient_id": 5,
        "patient_name": "Test Patient",
        "surgery_type": "abdominal",
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "common_data": {
            "temperature": "37.0",
            "blood_pressure_systolic": "",
            "blood_pressure_diastolic": "",
            "heart_rate": "",
            "respiratory_rate": "",
            "pain_level": 4,
        },
        "condition_data": {
            "selected_condition": "abdominal",
            "gi_function": "gas_only",
            "nausea_vomiting": "none",
            "appetite": "fair",
            "wound_condition": "clean_dry",
            "mobility": "walking_indoor",
            "additional_notes": "Test from Python script",
            "status": "good"
        }
    }
    
    print("📤 Sending to POST /api/progress/entries")
    print("📦 Data structure:", json.dumps(abdominal_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/progress/entries",
            json=abdominal_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ BACKEND ACCEPTS THE DATA - Database is ready!")
            return True
        elif response.status_code == 422:
            print("❌ VALIDATION ERROR - Check data structure")
            return False
        else:
            print("❌ OTHER ERROR - Check backend logs")
            return False
            
    except Exception as e:
        print(f"💥 Request failed: {e}")
        return False

if __name__ == "__main__":
    test_abdominal_submission()