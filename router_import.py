# check_router_imports.py
import os

def check_router_imports():
    """Check what classes routers are importing"""
    base_path = "app/health_progress"
    conditions = ['diabetes', 'abdominal']
    
    print("🔍 CHECKING ROUTER IMPORTS")
    print("=" * 50)
    
    for condition in conditions:
        router_file = os.path.join(base_path, condition, 'routers.py')
        schemas_file = os.path.join(base_path, condition, 'schemas.py')
        
        print(f"\n📁 {condition.upper()}")
        
        # Check router
        if os.path.exists(router_file):
            print(f"   Router file: {router_file}")
            with open(router_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line for keyword in ['response_model', 'entry: schemas', 'models.']):
                        print(f"      Line {i+1}: {line.strip()}")
        
        # Check schemas
        if os.path.exists(schemas_file):
            print(f"   Schemas file: {schemas_file}")
            with open(schemas_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('class '):
                        print(f"      Line {i+1}: {line.strip()}")

if __name__ == "__main__":
    check_router_imports()