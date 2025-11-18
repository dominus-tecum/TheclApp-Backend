# check_existing_users.py - Check if there are any existing users in the database
import requests
import json

def try_common_credentials():
    """Try common test credentials"""
    base_url = "https://45ff08be8614.ngrok-free.app"
    
    common_credentials = [
        {"email": "admin@example.com", "password": "admin"},
        {"email": "test@example.com", "password": "test"},
        {"email": "demo@example.com", "password": "demo"},
        {"email": "user@example.com", "password": "password"},
        {"email": "admin@hospital.com", "password": "admin123"},
        {"username": "admin", "password": "admin"},
        {"username": "test", "password": "test"}
    ]
    
    print("🔐 Trying common test credentials...")
    
    for creds in common_credentials:
        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json=creds,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"  {creds} -> Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ LOGIN SUCCESSFUL!")
                token_data = response.json()
                print(f"  Token: {token_data.get('access_token', 'Check response')}")
                
                with open('successful_login.json', 'w') as f:
                    json.dump(token_data, f, indent=2)
                return token_data
                
        except Exception as e:
            print(f"  Error: {e}")
    
    return None

if __name__ == "__main__":
    token_data = try_common_credentials()
    
    if token_data:
        print(f"\n🎉 Use this token for API discovery: {token_data.get('access_token')}")
    else:
        print("\n❌ No existing users found. We'll need to register a user next.")