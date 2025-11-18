# reset_and_test.py
from app.database import engine
from sqlalchemy import text

def reset_tables_and_test():
    """Reset tables and test model imports"""
    print("🔄 RESETTING TABLES AND TESTING")
    print("=" * 50)
    
    # 1. Drop old tables
    tables_to_drop = [
        'abdominal_progress_entries',
        'diabetes_progress_entries', 
        'progress_entries'
    ]
    
    print("🗑️  Dropping old tables...")
    with engine.connect() as conn:
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"   ✅ Dropped: {table}")
            except Exception as e:
                print(f"   ❌ Failed to drop {table}: {e}")
        conn.commit()
    
    # 2. Test model imports
    print(f"\n🔧 TESTING MODEL IMPORTS")
    models_to_check = [
        ("General", "app.health_progress.general.models", "GeneralHealthEntry"),
        ("Diabetes", "app.health_progress.diabetes.models", "DiabetesEntry"),
        ("Hypertension", "app.health_progress.hypertension.models", "HypertensionEntry"),
        ("Heart", "app.health_progress.heart.models", "HeartEntry"),
        ("Cancer", "app.health_progress.cancer.models", "CancerEntry"),
        ("Kidney", "app.health_progress.kidney.models", "KidneyEntry"),
        ("Abdominal", "app.health_progress.abdominal.models", "AbdominalEntry"),
    ]
    
    all_ok = True
    for name, module_path, class_name in models_to_check:
        try:
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            print(f"   ✅ {name:15} : {class_name} - OK")
            # Check table name
            table_name = model_class.__tablename__
            print(f"        Table: {table_name}")
        except Exception as e:
            print(f"   ❌ {name:15} : Error - {e}")
            all_ok = False
    
    if all_ok:
        print(f"\n🎉 ALL MODELS IMPORT SUCCESSFULLY!")
        print(f"🚀 Restart your FastAPI server to create new tables")
        print(f"🌐 Then visit: https://64b139983773.ngrok-free.app/docs")
    else:
        print(f"\n⚠️  Some model imports failed - check the errors above")

if __name__ == "__main__":
    reset_tables_and_test()