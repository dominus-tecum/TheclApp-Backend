# fix_model_names.py
import os

def fix_model_class_names():
    """Fix the inconsistent class names in model files"""
    base_path = "app/health_progress"
    
    fixes = [
        {
            'condition': 'diabetes',
            'old_class': 'DiabetesProgressEntry',
            'new_class': 'DiabetesEntry',
            'old_table': 'diabetes_progress_entries', 
            'new_table': 'diabetes_entries'
        },
        {
            'condition': 'abdominal',
            'old_class': 'AbdominalProgressEntry', 
            'new_class': 'AbdominalEntry',
            'old_table': 'abdominal_progress_entries',
            'new_table': 'abdominal_entries'
        }
    ]
    
    print("🔧 FIXING MODEL CLASS NAMES")
    print("=" * 50)
    
    for fix in fixes:
        model_file = os.path.join(base_path, fix['condition'], 'models.py')
        
        if os.path.exists(model_file):
            print(f"\n📁 Fixing {fix['condition']}/models.py")
            print(f"   Class: {fix['old_class']} → {fix['new_class']}")
            print(f"   Table: {fix['old_table']} → {fix['new_table']}")
            
            # Read the file
            with open(model_file, 'r') as f:
                content = f.read()
            
            # Replace class name
            new_content = content.replace(f"class {fix['old_class']}", f"class {fix['new_class']}")
            
            # Replace table name  
            new_content = new_content.replace(f'__tablename__ = "{fix["old_table"]}"', f'__tablename__ = "{fix["new_table"]}"')
            
            # Write back
            with open(model_file, 'w') as f:
                f.write(new_content)
            
            print("   ✅ Fixed!")
        else:
            print(f"❌ File not found: {model_file}")

if __name__ == "__main__":
    fix_model_class_names()