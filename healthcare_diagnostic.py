import requests
import json
from typing import Dict, Any, Optional

class HealthcareAPIDiagnostic:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            })
    
    def test_endpoint(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            else:
                return {'error': f'Unsupported method: {method}'}
            
            result = {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'headers': dict(response.headers),
            }
            
            if response.status_code == 200:
                try:
                    result['data'] = response.json()
                except:
                    result['data'] = response.text
            else:
                try:
                    result['error_data'] = response.json()
                except:
                    result['error_data'] = response.text
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'url': url, 'method': method}
    
    def discover_patient_endpoints(self) -> Dict[str, Any]:
        """Test all possible patient-related endpoints"""
        endpoints_to_test = [
            # User/auth endpoints
            ('/api/auth/me', 'GET'),
            ('/api/user/profile', 'GET'),
            ('/api/users/me', 'GET'),
            
            # Patient endpoints
            ('/api/patients/current', 'GET'),
            ('/api/patients/me', 'GET'),
            ('/api/patients', 'GET'),
            ('/api/patient', 'GET'),
            
            # Registration endpoints
            ('/api/auth/registration', 'GET'),
            ('/api/patients/registration', 'GET'),
            
            # Progress entries (we know this works)
            ('/api/progress/entries', 'GET'),
        ]
        
        results = {}
        for endpoint, method in endpoints_to_test:
            print(f"Testing {method} {endpoint}...")
            results[endpoint] = self.test_endpoint(endpoint, method)
        
        return results
    
    def analyze_user_structure(self) -> Optional[Dict[str, Any]]:
        """Try to get user information and analyze the structure"""
        # Test common user endpoints
        user_endpoints = ['/api/auth/me', '/api/user/profile', '/api/users/me']
        
        for endpoint in user_endpoints:
            result = self.test_endpoint(endpoint)
            if result.get('status_code') == 200 and result.get('data'):
                print(f"✅ Found user data at {endpoint}")
                return result['data']
        
        print("❌ No user endpoints returned data")
        return None
    
    def analyze_patient_structure(self) -> Optional[Dict[str, Any]]:
        """Try to get patient information and analyze the structure"""
        # Test common patient endpoints
        patient_endpoints = ['/api/patients/me', '/api/patients/current', '/api/patient']
        
        for endpoint in patient_endpoints:
            result = self.test_endpoint(endpoint)
            if result.get('status_code') == 200 and result.get('data'):
                print(f"✅ Found patient data at {endpoint}")
                return result['data']
        
        print("❌ No patient endpoints returned data")
        return None
    
    def test_progress_submission(self) -> Dict[str, Any]:
        """Test what the progress endpoint expects"""
        test_data = {
            "patient_id": 1,
            "patient_name": "Test Patient",
            "surgery_type": "cesarean",
            "submission_date": "2024-01-01",
            "temperature": 37.0,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80
        }
        
        return self.test_endpoint('/api/progress/entries', 'POST', test_data)
    
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print("🔍 Starting Healthcare API Diagnostic...")
        print("=" * 60)
        
        # 1. Discover all endpoints
        print("\n1. 🔎 Discovering endpoints...")
        endpoint_results = self.discover_patient_endpoints()
        
        # 2. Analyze user structure
        print("\n2. 👤 Analyzing user data structure...")
        user_data = self.analyze_user_structure()
        if user_data:
            print("User data structure:", json.dumps(user_data, indent=2))
        
        # 3. Analyze patient structure  
        print("\n3. 🏥 Analyzing patient data structure...")
        patient_data = self.analyze_patient_structure()
        if patient_data:
            print("Patient data structure:", json.dumps(patient_data, indent=2))
        
        # 4. Test progress submission
        print("\n4. 📊 Testing progress submission...")
        submission_test = self.test_progress_submission()
        print("Submission test result:", json.dumps(submission_test, indent=2))
        
        # 5. Summary
        print("\n5. 📋 Diagnostic Summary:")
        print("=" * 60)
        
        working_endpoints = []
        for endpoint, result in endpoint_results.items():
            if result.get('status_code') == 200:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint} - Status {result['status_code']}")
            else:
                print(f"❌ {endpoint} - Status {result.get('status_code', 'ERROR')}")
        
        print(f"\n🎯 Working endpoints: {len(working_endpoints)}")
        for endpoint in working_endpoints:
            print(f"   - {endpoint}")
        
        return {
            'working_endpoints': working_endpoints,
            'user_data': user_data,
            'patient_data': patient_data,
            'submission_test': submission_test
        }

def main():
    # Configuration - UPDATE THESE FOR YOUR ENVIRONMENT
    BASE_URL = "http://localhost:8000"  # Change to your backend URL
    AUTH_TOKEN = "your-auth-token-here"  # Get this from your app
    
    print("Healthcare API Diagnostic Tool")
    print("Please make sure your backend is running!")
    print(f"Target URL: {BASE_URL}")
    print()
    
    # If no auth token provided, try to get one (you might need to implement this)
    if AUTH_TOKEN == "your-auth-token-here":
        print("❌ Please update AUTH_TOKEN in the script with a valid token")
        return
    
    diagnostic = HealthcareAPIDiagnostic(BASE_URL, AUTH_TOKEN)
    results = diagnostic.run_full_diagnostic()
    
    # Save results to file
    with open('api_diagnostic_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to api_diagnostic_results.json")

if __name__ == "__main__":
    main()