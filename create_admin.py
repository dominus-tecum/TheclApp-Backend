# manage_admin.py
import bcrypt
import sqlite3
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_admin():
    """Create new admin"""
    conn = sqlite3.connect("hospiapp.db")
    cursor = conn.cursor()
    
    # Remove existing admin first if any
    cursor.execute("DELETE FROM users WHERE email = 'admin@theclapp.com'")
    
    # Generate password hash
    password = "Admin123!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Insert admin with UPPERCASE role
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, name, status, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "admin",
        "admin@theclapp.com",
        hashed.decode('utf-8'),
        "ADMIN",
        "System Administrator",
        "approved",
        1
    ))
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ ADMIN CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"   Email: admin@theclapp.com")
    print(f"   Password: {password}")
    print(f"   Role: ADMIN")
    print(f"   Status: approved")
    print("="*50 + "\n")
    input("Press Enter to continue...")

def remove_admin():
    """Remove existing admin"""
    conn = sqlite3.connect("hospiapp.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, role FROM users WHERE email = 'admin@theclapp.com'")
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("DELETE FROM users WHERE email = 'admin@theclapp.com'")
        conn.commit()
        print("\n" + "="*50)
        print("✅ ADMIN REMOVED SUCCESSFULLY!")
        print("="*50)
        print(f"   ID: {existing[0]}")
        print(f"   Email: {existing[1]}")
        print(f"   Role: {existing[2]}")
        print("="*50 + "\n")
    else:
        print("\n" + "="*50)
        print("❌ ADMIN NOT FOUND - Nothing to remove")
        print("="*50 + "\n")
    
    conn.close()
    input("Press Enter to continue...")

def show_admin():
    """Show admin info if exists"""
    conn = sqlite3.connect("hospiapp.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, role, status FROM users WHERE email = 'admin@theclapp.com'")
    admin = cursor.fetchone()
    
    print("\n" + "="*50)
    if admin:
        print("📋 ADMIN INFORMATION")
        print("="*50)
        print(f"   ID: {admin[0]}")
        print(f"   Email: {admin[1]}")
        print(f"   Role: {admin[2]}")
        print(f"   Status: {admin[3]}")
    else:
        print("❌ NO ADMIN FOUND")
        print("   Please create an admin using option 1")
    print("="*50 + "\n")
    
    conn.close()
    input("Press Enter to continue...")

def main():
    while True:
        clear_screen()
        print("\n" + "="*50)
        print("        ADMIN MANAGEMENT SYSTEM")
        print("="*50)
        print("  [1]  CREATE ADMIN")
        print("  [2]  REMOVE ADMIN")
        print("  [3]  SHOW ADMIN INFO")
        print("  [4]  EXIT")
        print("="*50)
        
        choice = input("\n  Enter your choice (1-4): ").strip()
        
        if choice == "1":
            create_admin()
        elif choice == "2":
            remove_admin()
        elif choice == "3":
            show_admin()
        elif choice == "4":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  ❌ Invalid choice! Please enter 1-4")
            input("\n  Press Enter to continue...")

if __name__ == "__main__":
    main()