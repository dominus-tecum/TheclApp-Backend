# check_router_contents.py
import os

def check_router_contents():
    """Check the actual content of router files"""
    base_path = "app/health_progress"
    conditions = ['diabetes', 'abdominal']
    
    print("🔍 CHECKING ROUTER FILE CONTENTS")
    print("=" * 50)
    
    for condition in conditions:
        router_file = os.path.join(base_path, condition, 'routers.py')
        
        print(f"\n📁 {condition.upper()} ROUTER")
        print("=" * 30)
        
        if os.path.exists(router_file):
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
            except UnicodeDecodeError:
                with open(router_file, 'r', encoding='latin-1') as f:
                    content = f.read()
                    print(content)
        else:
            print("❌ Router file not found!")

if __name__ == "__main__":
    check_router_contents()