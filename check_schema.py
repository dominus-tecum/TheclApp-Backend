# check_schemas.py
import os
import json

def check_schema_requirements():
    """Check what fields each schema actually requires"""
    base_path = "app/health_progress"
    conditions = ['general', 'diabetes', 'hypertension', 'heart', 'cancer', 'kidney', 'abdominal']
    
    print("🔍 CHECKING SCHEMA REQUIREMENTS")
    print("=" * 60)
    
    for condition in conditions:
        schema_file = os.path.join(base_path, condition, 'schemas.py')
        
        print(f"\n📁 {condition.upper()} SCHEMA")
        print("-" * 40)
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Look for Create schema class
                in_create_class = False
                for line in lines:
                    if line.strip().startswith('class ') and 'Create' in line:
                        in_create_class = True
                        print(f"📝 Create Schema: {line.strip()}")
                        continue
                    
                    if in_create_class:
                        if line.strip().startswith('class '):
                            break
                        if ':' in line and '=' not in line:  # Field definition
                            field_line = line.strip()
                            if field_line and not field_line.startswith('#'):
                                print(f"   📋 {field_line}")

if __name__ == "__main__":
    check_schema_requirements()