# check_router_issues.py
import os
import importlib.util

def check_router_issues():
    """Check what's actually in the router files"""
    base_path = "app/health_progress"
    problem_conditions = ['diabetes', 'abdominal']
    
    print("🔍 CHECKING ROUTER ISSUES")
    print("=" * 50)
    
    for condition in problem_conditions:
        router_file = os.path.join(base_path, condition, 'routers.py')
        
        print(f"\n📁 {condition.upper()}")
        print(f"   Router file: {router_file}")
        
        if os.path.exists(router_file):
            # Read with error handling
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                with open(router_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Look for the problematic imports
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'ProgressEntry' in line:
                    print(f"   Line {i+1}: {line.strip()}")
        
        # Also check schemas
        schemas_file = os.path.join(base_path, condition, 'schemas.py')
        if os.path.exists(schemas_file):
            try:
                with open(schemas_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                with open(schemas_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'ProgressEntry' in line or 'class ' in line:
                    print(f"   Schema Line {i+1}: {line.strip()}")

if __name__ == "__main__":
    check_router_issues()