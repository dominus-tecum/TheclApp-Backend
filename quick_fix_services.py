# quick_fix_services.py
import os

def quick_fix():
    """Quick fix for service files"""
    base_path = "app/health_progress"
    
    fixes = [
        ('diabetes', 'DiabetesProgressEntry', 'DiabetesEntry'),
        ('abdominal', 'AbdominalProgressEntry', 'AbdominalEntry')
    ]
    
    print("🔧 QUICK FIX FOR SERVICE FILES")
    print("=" * 50)
    
    for condition, old_class, new_class in fixes:
        service_file = os.path.join(base_path, condition, 'services.py')
        
        print(f"\n📁 Fixing {condition}/services.py")
        
        if os.path.exists(service_file):
            # Read the file
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the class name
            new_content = content.replace(old_class, new_class)
            
            # Write back
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"   ✅ Replaced {old_class} → {new_class}")
        else:
            print("   ❌ Service file not found")

if __name__ == "__main__":
    quick_fix()