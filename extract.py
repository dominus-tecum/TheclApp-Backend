# token_extractor.py - Run this in your app environment
import requests

def get_auth_token():
    # Update with your actual login credentials
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = requests.post("https://45ff08be8614.ngrok-free.app/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('access_token') or response.json().get('token')
        print(f"🔑 Auth Token: {token}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

if __name__ == "__main__":
    get_auth_token()