# get_your_token.py - Get auth token with your credentials
import requests
import json

def get_token():
    base_url = "https://45ff08be8614.ngrok-free.app"
    
    # USE YOUR ACTUAL PASSWORD HERE
    credentials = {
        "email": "abc@gmail.com",
        "password": "Asd"  # ← REPLACE THIS WITH YOUR ACTUAL PASSWORD
    }
    
    print("🔐 Getting your auth token...")
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=credentials,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"Access Token: {token_data.get('access_token')}")
            
            # Save the token
            with open('your_token.json', 'w') as f:
                json.dump(token_data, f, indent=2)
            print("💾 Token saved to 'your_token.json'")
            return token_data
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

if __name__ == "__main__":
    get_token()