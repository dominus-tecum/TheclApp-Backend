# inspect_database.py
from app.database import engine, SessionLocal
from sqlalchemy import inspect, text
import json

def inspect_database_completely():
    """Completely inspect the current database state"""
    print("🔍 COMPREHENSIVE DATABASE INSPECTION")
    print("=" * 60)
    
    inspector = inspect(engine)
    
    # 1. Check ALL tables
    all_tables = inspector.get_table_names()
    print(f"📊 TOTAL TABLES IN DATABASE: {len(all_tables)}")
    print("All tables:", sorted(all_tables))
    print()
    
    # 2. Focus on health-related tables
    health_keywords = ['health', 'progress', 'diabetes', 'abdominal', 'medical', 'patient']
    health_tables = []
    
    for table in all_tables:
        if any(keyword in table.lower() for keyword in health_keywords):
            health_tables.append(table)
    
    print(f"🏥 HEALTH-RELATED TABLES: {len(health_tables)}")
    for table in sorted(health_tables):
        print(f"   📋 {table}")
    print()
    
    # 3. Detailed table inspection
    print("📈 DETAILED TABLE STRUCTURE")
    print("=" * 60)
    
    for table_name in sorted(health_tables):
        print(f"\n🎯 TABLE: {table_name}")
        print("-" * 40)
        
        # Columns
        columns = inspector.get_columns(table_name)
        print("   COLUMNS:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col['default'] else ""
            pk = "PRIMARY KEY" if col.get('primary_key') else ""
            print(f"     ├── {col['name']:25} {str(col['type']):20} {nullable:10} {default:15} {pk}")
        
        # Indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print("   INDEXES:")
            for idx in indexes:
                unique = "UNIQUE" if idx['unique'] else ""
                print(f"     ├── {idx['name']:30} {idx['column_names']} {unique}")
        
        # Foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print("   FOREIGN KEYS:")
            for fk in foreign_keys:
                print(f"     ├── {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # 4. Check sample data counts
    print(f"\n📊 SAMPLE DATA COUNTS")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        for table_name in sorted(health_tables):
            try:
                # Use raw SQL to count rows (works for any table)
                result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                count = result.scalar()
                print(f"   📈 {table_name:35} : {count} rows")
            except Exception as e:
                print(f"   ❌ {table_name:35} : Error - {e}")
    finally:
        db.close()
    
    # 5. Check actual data samples
    print(f"\n🔍 SAMPLE DATA PREVIEW")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        for table_name in sorted(health_tables):
            try:
                result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
                row = result.fetchone()
                if row:
                    print(f"\n🎯 SAMPLE FROM {table_name}:")
                    print("-" * 40)
                    # Convert row to dict for pretty printing
                    row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(zip(result.keys(), row))
                    for key, value in row_dict.items():
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, indent=2) if value else "NULL"
                        print(f"     {key:25} : {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                else:
                    print(f"   📭 {table_name:35} : No data")
            except Exception as e:
                print(f"   ❌ {table_name:35} : Error reading data - {e}")
    finally:
        db.close()

def check_specific_models():
    """Check if specific models can be imported"""
    print(f"\n🔧 MODEL IMPORT CHECK")
    print("=" * 60)
    
    models_to_check = [
        ("General", "app.health_progress.general.models", "GeneralHealthEntry"),
        ("Diabetes", "app.health_progress.diabetes.models", "DiabetesEntry"),
        ("Hypertension", "app.health_progress.hypertension.models", "HypertensionEntry"),
        ("Heart", "app.health_progress.heart.models", "HeartEntry"),
        ("Cancer", "app.health_progress.cancer.models", "CancerEntry"),
        ("Kidney", "app.health_progress.kidney.models", "KidneyEntry"),
        ("Abdominal", "app.health_progress.abdominal.models", "AbdominalEntry"),
    ]
    
    for name, module_path, class_name in models_to_check:
        try:
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            print(f"   ✅ {name:15} : {class_name} - OK")
            
            # Check table name
            table_name = model_class.__tablename__
            print(f"        Table: {table_name}")
            
        except ImportError as e:
            print(f"   ❌ {name:15} : Import error - {e}")
        except AttributeError as e:
            print(f"   ❌ {name:15} : Class not found - {e}")
        except Exception as e:
            print(f"   ❌ {name:15} : Error - {e}")

if __name__ == "__main__":
    inspect_database_completely()
    check_specific_models()
    
    print(f"\n🎯 NEXT STEPS:")
    print("   1. Check if new table names match expected names")
    print("   2. Verify model imports are working")
    print("   3. Compare current tables vs expected tables")