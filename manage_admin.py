#!/usr/bin/env python3
"""
Complete Admin Management Script
Uses self-contained one-time tokens - NO persistent secret key needed!
"""

import requests
import os
import sys
import jwt
import datetime
import secrets

# ============================================================
# CONFIGURATION - ONLY YOUR RENDER URL NEEDED
# ============================================================

RENDER_APP_URL = "https://theclapp-backend.onrender.com"  # YOUR ACTUAL URL

# ============================================================

BASE_URL = f"{RENDER_APP_URL}/api/admin"

def generate_one_time_token():
    """
    Generate a self-contained one-time token for admin creation.
    NO shared secret needed - token is self-validating.
    """
    
    # Generate a random secret for THIS TOKEN ONLY
    token_secret = secrets.token_urlsafe(32)
    
    # Create payload that expires in 15 minutes
    payload = {
        "purpose": "admin_creation",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "iat": datetime.datetime.utcnow(),
        "jti": secrets.token_urlsafe(16),  # Unique token ID
        "secret": token_secret  # One-time secret embedded in token
    }
    
    # Sign with the embedded secret (not a shared global secret)
    token = jwt.encode(payload, token_secret, algorithm="HS256")
    return token, token_secret

def create_admin():
    """Create admin using self-contained one-time token"""
    print("\n" + "="*50)
    print("        CREATE ADMIN")
    print("="*50)
    
    # Generate a fresh one-time token for this operation
    admin_token, token_secret = generate_one_time_token()
    
    print("\n  🔐 Generated one-time token (valid for 15 minutes)\n")
    
    email = input("  Email [admin@theclapp.com]: ").strip() or "admin@theclapp.com"
    password = input("  Password [Admin123!]: ").strip() or "Admin123!"
    username = input("  Username [admin]: ").strip() or "admin"
    name = input("  Name [System Administrator]: ").strip() or "System Administrator"
    
    payload = {
        "email": email,
        "password": password,
        "username": username,
        "name": name,
        "admin_token": admin_token,
        "token_secret": token_secret  # Send the secret along with the token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create", json=payload)
        
        if response.status_code == 201:
            result = response.json()
            print("\n" + "="*50)
            print("✅ ADMIN CREATED SUCCESSFULLY!")
            print("="*50)
            print(f"   Message: {result['message']}")
            print(f"   Admin ID: {result['admin_id']}")
            print(f"   Email: {result['email']}")
            print(f"   Role: {result['role']}")
            print("="*50)
        else:
            print("\n❌ Failed to create admin")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"   Error: {error_detail}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Failed to connect to Render app")
        print(f"   Make sure your app is running at: {RENDER_APP_URL}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def remove_admin():
    """Remove admin (requires existing admin to authenticate)"""
    print("\n" + "="*50)
    print("        REMOVE ADMIN")
    print("="*50)
    
    print("\n  Authentication required for admin removal")
    admin_email = input("  Your admin email: ").strip()
    admin_password = input("  Your admin password: ").strip()
    
    try:
        login_response = requests.post(
            f"{RENDER_APP_URL}/api/auth/login",
            json={"email": admin_email, "password": admin_password}
        )
        
        if login_response.status_code != 200:
            print("\n❌ Authentication failed")
            input("\nPress Enter...")
            return
        
        access_token = login_response.json().get('access_token')
        
        email_to_remove = input("\n  Email of admin to remove: ").strip()
        confirm = input(f"  Remove {email_to_remove}? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("\n  Removal cancelled.")
            input("\nPress Enter...")
            return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.delete(
            f"{BASE_URL}/remove",
            json={"email": email_to_remove},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*50)
            print("✅ ADMIN REMOVED SUCCESSFULLY!")
            print("="*50)
            print(f"   {result['message']}")
            print("="*50)
        else:
            print("\n❌ Failed to remove admin")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"   Error: {error_detail}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def update_admin_status():
    """Update admin status (requires existing admin to authenticate)"""
    print("\n" + "="*50)
    print("        UPDATE ADMIN STATUS")
    print("="*50)
    
    admin_email = input("  Your admin email: ").strip()
    admin_password = input("  Your admin password: ").strip()
    
    try:
        login_response = requests.post(
            f"{RENDER_APP_URL}/api/auth/login",
            json={"email": admin_email, "password": admin_password}
        )
        
        if login_response.status_code != 200:
            print("\n❌ Authentication failed")
            input("\nPress Enter...")
            return
        
        access_token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {access_token}"}
        
        email = input("\n  Admin email to update: ").strip()
        
        info_response = requests.get(
            f"{BASE_URL}/info",
            params={"email": email},
            headers=headers
        )
        
        if info_response.status_code != 200:
            print(f"\n❌ Admin not found: {email}")
            input("\nPress Enter...")
            return
        
        current = info_response.json()
        print(f"\n  Current Status: {current['status']}")
        print(f"  Current Active: {current['is_active']}")
        
        print("\n  New Status Options:")
        print("    1. approved (active)")
        print("    2. suspended (inactive)")
        print("    3. pending (awaiting approval)")
        
        choice = input("\n  Choose status (1-3): ").strip()
        
        if choice == "1":
            new_status = "approved"
            is_active = True
        elif choice == "2":
            new_status = "suspended"
            is_active = False
        elif choice == "3":
            new_status = "pending"
            is_active = False
        else:
            print("❌ Invalid choice")
            input("\nPress Enter...")
            return
        
        update_payload = {
            "status": new_status,
            "is_active": is_active
        }
        
        response = requests.put(
            f"{RENDER_APP_URL}/api/users/{current['id']}",
            json=update_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print("\n✅ ADMIN STATUS UPDATED!")
            print(f"   Email: {email}")
            print(f"   New Status: {new_status}")
            print(f"   Active: {is_active}")
        else:
            print(f"\n❌ Update failed: {response.json().get('detail', 'Unknown error')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def show_admin():
    """Show admin info (no authentication required)"""
    print("\n" + "="*50)
    print("        ADMIN INFORMATION")
    print("="*50)
    
    email = input("  Email [admin@theclapp.com]: ").strip() or "admin@theclapp.com"
    
    try:
        response = requests.get(f"{BASE_URL}/info", params={"email": email})
        
        if response.status_code == 200:
            admin = response.json()
            print("\n" + "="*50)
            print("📋 ADMIN INFORMATION")
            print("="*50)
            print(f"   ID: {admin['id']}")
            print(f"   Email: {admin['email']}")
            print(f"   Username: {admin['username']}")
            print(f"   Name: {admin['name']}")
            print(f"   Role: {admin['role']}")
            print(f"   Status: {admin['status']}")
            print(f"   Active: {admin['is_active']}")
            print("="*50)
        else:
            print("\n❌ Admin not found")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def main():
    while True:
        clear_screen()
        print("\n" + "="*50)
        print("   ADMIN MANAGEMENT SYSTEM")
        print("="*50)
        print(f"   Render App: {RENDER_APP_URL}")
        print("="*50)
        print("  [1]  CREATE ADMIN (auto-generates one-time token)")
        print("  [2]  REMOVE ADMIN (requires login)")
        print("  [3]  UPDATE ADMIN STATUS (requires login)")
        print("  [4]  SHOW ADMIN INFO")
        print("  [5]  EXIT")
        print("="*50)
        
        choice = input("\n  Enter your choice (1-5): ").strip()
        
        if choice == "1":
            create_admin()
        elif choice == "2":
            remove_admin()
        elif choice == "3":
            update_admin_status()
        elif choice == "4":
            show_admin()
        elif choice == "5":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  ❌ Invalid choice! Please enter 1-5")
            input("\n  Press Enter to continue...")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        import requests
        import jwt
    except ImportError as e:
        print(f"❌ Missing module: {e}")
        print("\nInstall required packages:")
        print("  pip install requests pyjwt")
        sys.exit(1)
    
    main()