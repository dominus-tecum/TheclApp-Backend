import requests
import json
from datetime import datetime

API_BASE_URL = "https://45ff08be8614.ngrok-free.app/api"

def test_cesarean_data():
    """Test with actual C-section recovery data"""
    
    data = {
        "patient_id": 123,
        "patient_name": "Jane Doe", 
        "surgery_type": "cesarean",
        "submission_date": datetime.now().strftime("%Y-%m-%d"),
        "common_data": {
            "temperature": "37.0",
            "blood_pressure_systolic": "120",
            "blood_pressure_diastolic": "80",
            "heart_rate": "75",
            "respiratory_rate": "16",
            "pain_level": 2
        },
        "condition_data": {
            "fundal_height": "2",
            "uterine_firmness": "firm",
            "lochia_color": "rubra",
            "lochia_amount": "moderate",
            "wound_condition": "clean",
            "urine_output": "1500",
            "breastfeeding": False
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dev-mock-token"
    }
    
    print("🔍 Testing with actual C-section data...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/progress/entries",
            json=data,
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cesarean_data()
    