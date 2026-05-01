#!/usr/bin/env python3
"""
Complete Admin Management Script
"""

import requests
import secrets
import datetime
import psycopg2
import os
import sys
from urllib.parse import urlparse

RENDER_APP_URL = "https://theclapp-backend.onrender.com"
DATABASE_URL = os.environ.get('DATABASE_URL')

def generate_and_store_token():
    """Generate one-time token and store in database"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set!")
        sys.exit(1)
    
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    cur = conn.cursor()
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    
    cur.execute("""
        INSERT INTO one_time_tokens (token, purpose, expires_at)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (token, 'admin_creation', expires_at))
    
    token_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Token generated (ID: {token_id})")
    return token

def create_admin():
    print("\n" + "="*50)
    print("        CREATE ADMIN")
    print("="*50)
    
    email = input("  Email [admin@theclapp.com]: ").strip() or "admin@theclapp.com"
    password = input("  Password [Admin123!]: ").strip() or "Admin123!"
    username = input("  Username [admin]: ").strip() or "admin"
    name = input("  Name [System Administrator]: ").strip() or "System Administrator"
    
    # Generate and store token in database
    one_time_token = generate_and_store_token()
    
    print(f"\n  🔐 Generated one-time token (valid for 15 minutes)")
    
    payload = {
        "email": email,
        "password": password,
        "username": username,
        "name": name,
        "one_time_token": one_time_token
    }
    
    try:
        response = requests.post(f"{RENDER_APP_URL}/api/admin/create", json=payload)
        
        if response.status_code == 201:
            result = response.json()
            print("\n" + "="*50)
            print("✅ ADMIN CREATED SUCCESSFULLY!")
            print("="*50)
            print(f"   Admin ID: {result['admin_id']}")
            print(f"   Email: {result['email']}")
            print("="*50)
        else:
            print("\n❌ Failed to create admin")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def main():
    create_admin()

if __name__ == "__main__":
    import psycopg2
    import datetime
    from urllib.parse import urlparse
    
    main()