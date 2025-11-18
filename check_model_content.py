# check_model_contents.py
import os

def read_model_files():
    """Read and display the actual contents of model files"""
    base_path = "app/health_progress"
    conditions = ['general', 'diabetes', 'hypertension', 'heart', 'cancer', 'kidney', 'abdominal']
    
    print("🔍 READING ACTUAL MODEL FILE CONTENTS")
    print("=" * 60)
    
    for condition in conditions:
        model_file = os.path.join(base_path, condition, 'models.py')
        print(f"\n📁 {condition.upper()}/models.py")
        print("-" * 40)
        
        if os.path.exists(model_file):
            with open(model_file, 'r') as f:
                content = f.read()
                # Show the first 20 lines to see the class definition
                lines = content.split('\n')
                for i, line in enumerate(lines[:25]):  # Show first 25 lines
                    print(f"{i+1:3}: {line}")
        else:
            print("❌ File does not exist!")

if __name__ == "__main__":
    read_model_files()