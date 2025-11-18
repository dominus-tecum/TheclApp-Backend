import requests
import json
from datetime import datetime

BASE_URL = "https://d669a8002236.ngrok-free.app"

def test_backend_endpoint():
    """Test if the progress entries endpoint exists"""
    
    print("🔍 TESTING: Does POST /api/progress/entries work?")
    
    # Simple test data - surgery type doesn't matter
    test_data = {
        "patient_id": 5,
        "patient_name": "Test Patient", 
        "surgery_type": "test",
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "common_data": {
            "temperature": "37.0",
            "pain_level": 3
        },
        "condition_data": {
            "selected_condition": "test",
            "status": "good"
        }
    }
    
    print("📤 Testing endpoint: POST /api/progress/entries")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/progress/entries",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Body: {response.text}")
        
        return response.status_code
        
    except Exception as e:
        print(f"💥 Request failed: {e}")
        return None

if __name__ == "__main__":
    test_backend_endpoint()