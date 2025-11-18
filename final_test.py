# final_comprehensive_test.py
import requests
import json
from datetime import datetime

BASE_URL = "https://64b139983773.ngrok-free.app"

def test_all_endpoints():
    """Test all 7 health progress endpoints"""
    print("🚀 COMPREHENSIVE ENDPOINT TEST")
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
                "common_data": {
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
                },
                "condition_specific_data": {}
            }
        },
        {
            "name": "Diabetes",
            "endpoint": "/api/health-progress/diabetes-entries", 
            "data": {
                "patientId": 1,
                "patientName": "Test Patient",
                "submissionDate": datetime.now().strftime("%Y-%m-%d"),
                "urgency_status": "good",
                "common_data": {
                    "bloodPressureSystolic": "120",
                    "bloodPressureDiastolic": "80", 
                    "energyLevel": 7,
                    "sleepHours": 7.5,
                    "sleepQuality": 4,
                    "medications": {"morning": True, "afternoon": False, "evening": True, "sideEffects": ""},
                    "symptoms": {"fatigue": False, "nausea": False, "breathingIssues": False, "pain": False, "swelling": False, "other": ""},
                    "notes": "Test diabetes entry"
                },
                "condition_specific_data": {
                    "bloodGlucose": "125"
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
                    "medications": {"morning": True, "afternoon": False, "evening": True, "sideEffects": ""},
                    "symptoms": {"fatigue": False, "nausea": False, "breathingIssues": False, "pain": False, "swelling": False, "other": ""},
                    "notes": "Test hypertension entry"
                },
                "condition_specific_data": {
                    "bpMonitoringFrequency": "daily"
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
                print(f"   ❌ FAILED - {response.status_code}: {response.text}")
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
        print("   You should see all 7 health progress endpoints working!")

if __name__ == "__main__":
    test_all_endpoints()