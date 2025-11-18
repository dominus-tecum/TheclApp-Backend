# correct_schema_test.py
import requests
import json
from datetime import datetime

BASE_URL = "https://64b139983773.ngrok-free.app"

def test_all_endpoints():
    """Test all endpoints with correct schema formats"""
    print("🚀 CORRECT SCHEMA ENDPOINT TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "General Health",
            "endpoint": "/api/health-progress/general-entries",
            "data": {
                "patientId": 1,
                "patientName": "Test Patient",
                "submissionDate": datetime.now().strftime("%Y-%m-%d"),
                "urgency_status": "good",
                "general_data": {
                    "bloodPressureSystolic": "120",
                    "bloodPressureDiastolic": "80",
                    "heartRate": "72",
                    "energyLevel": 7,
                    "sleepHours": 7.5,
                    "sleepQuality": 4,
                    "medications": {"morning": True, "afternoon": False, "evening": True, "sideEffects": ""},
                    "symptoms": {"fatigue": False, "nausea": False, "breathingIssues": False, "pain": False, "swelling": False, "other": ""},
                    "overallFeeling": "good",
                    "activityLevel": "normal",
                    "notes": "Test general entry"
                }
            }
        },
        {
            "name": "Diabetes",
            "endpoint": "/api/health-progress/diabetes-entries", 
            "data": {
                "patient_id": 1,
                "patient_name": "Test Patient",
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "common_data": {
                    "blood_pressure_systolic": "120",
                    "blood_pressure_diastolic": "80", 
                    "energy_level": 7,
                    "sleep_hours": 7.5,
                    "sleep_quality": 4,
                    "pain_level": 2,
                    "temperature": "37.0",
                    "medications": {"morning": True, "afternoon": False, "evening": True, "side_effects": ""},
                    "symptoms": {"fatigue": False, "nausea": False, "breathing_issues": False, "pain": False, "swelling": False, "other": ""},
                    "notes": "Test diabetes entry"
                },
                "condition_data": {
                    "blood_glucose": "125"
                }
            }
        },
        {
            "name": "Hypertension",
            "endpoint": "/api/health-progress/hypertension-entries",
            "data": {
                "patientId": 1,
                "patientName": "Test Patient", 
                "submissionDate": datetime.now().strftime("%Y-%m-%d"),
                "urgency_status": "monitor",
                "common_data": {
                    "bloodPressureSystolic": "140",
                    "bloodPressureDiastolic": "90",
                    "energyLevel": 6,
                    "sleepHours": 7,
                    "sleepQuality": 3,
                    "pain_level": 1,
                    "medications": {"morning": True, "afternoon": False, "evening": True, "sideEffects": ""},
                    "symptoms": {"fatigue": False, "nausea": False, "breathingIssues": False, "pain": False, "swelling": False, "other": ""},
                    "notes": "Test hypertension entry"
                },
                "condition_specific_data": {
                    "bpMonitoringFrequency": "daily"
                }
            }
        },
        {
            "name": "Heart Disease",
            "endpoint": "/api/health-progress/heart-entries",
            "data": {
                "patientId": 1,
                "patientName": "Test Patient",
                "submissionDate": datetime.now().strftime("%Y-%m-%d"),
                "urgency_status": "monitor",
                "common_data": {
                    "bloodPressureSystolic": "130",
                    "bloodPressureDiastolic": "85",
                    "energyLevel": 5,
                    "sleepHours": 6.5,
                    "sleepQuality": 3,
                    "pain_level": 3,
                    "medications": {"morning": True, "afternoon": False, "evening": True, "sideEffects": ""},
                    "symptoms": {"fatigue": True, "nausea": False, "breathingIssues": True, "pain": True, "swelling": False, "other": ""},
                    "notes": "Test heart disease entry"
                },
                "condition_specific_data": {
                    "heartChestPain": 3,
                    "heartPainLocation": "chest",
                    "heartWeight": "180",
                    "heartSwelling": 1,
                    "heartBreathing": 4,
                    "heartActivityLevel": "light"
                }
            }
        },
        {
            "name": "Abdominal Surgery",
            "endpoint": "/api/progress/abdominal-entries",
            "data": {
                "patient_id": 1,
                "patient_name": "Test Patient",
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "common_data": {
                    "blood_pressure_systolic": "120",
                    "blood_pressure_diastolic": "80",
                    "energy_level": 6,
                    "sleep_hours": 7,
                    "sleep_quality": 3,
                    "pain_level": 4,
                    "temperature": "36.8",
                    "medications": {"morning": True, "afternoon": False, "evening": True, "side_effects": ""},
                    "symptoms": {"fatigue": True, "nausea": False, "breathing_issues": False, "pain": True, "swelling": True, "other": ""},
                    "notes": "Test abdominal entry"
                },
                "condition_data": {
                    "gi_function": "normal",
                    "nausea_vomiting": "none", 
                    "appetite": "good",
                    "wound_condition": "healing_well",
                    "mobility": "moderate",
                    "additional_notes": "Test abdominal surgery entry"
                }
            }
        }
    ]
    
    results = {}
    
    for test in test_cases:
        print(f"\n🧪 Testing {test['name']}...")
        try:
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            if response.status_code == 200:
                print(f"   ✅ SUCCESS - Entry created!")
                results[test['name']] = True
            else:
                print(f"   ❌ FAILED - {response.status_code}")
                if response.status_code == 422:
                    # Show validation errors
                    errors = response.json().get('detail', [])
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"      {error['loc']}: {error['msg']}")
                else:
                    print(f"   Error: {response.text[:200]}...")
                results[test['name']] = False
        except Exception as e:
            print(f"   ❌ ERROR - {e}")
            results[test['name']] = False
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n🎯 Results: {successful}/{total} endpoints working")
    
    if successful > 0:
        print(f"\n🌐 Visit your API documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    test_all_endpoints()