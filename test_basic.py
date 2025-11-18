import requests
import json

LOCAL_URL = "http://localhost:8000"

def test_basic_endpoints():
    """Test if basic endpoints are working"""
    print("🔍 Testing basic endpoints...")
    
    endpoints = [
        "/",
        "/health",
        "/api/progress/entries",
        "/api/progress/dashboard-stats"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{LOCAL_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/api/progress/dashboard-stats":
                    stats = response.json()
                    print(f"     📊 Stats - Total: {stats.get('total_entries', 0)}")
                elif endpoint == "/api/progress/entries":
                    entries = response.json()
                    print(f"     📝 Found {len(entries)} entries")
                    
        except Exception as e:
            print(f"   {endpoint}: ❌ {e}")

if __name__ == "__main__":
    test_basic_endpoints()