# data_test_fixed.py
from sqlalchemy import create_engine, text
import json
from datetime import datetime

def test_orthopedic_data_insertion():
    DATABASE_URL = "sqlite:///./hospiapp.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    print("🧪 Testing orthopedic data insertion...")
    
    # Sample data that matches your React component structure
    test_data = {
        "patient_id": 999,
        "patient_name": "Test Orthopedic Patient",
        "surgery_type": "orthopedic",
        "submission_date": "2024-01-15",
        "common_data": json.dumps({  # ✅ Convert to JSON string
            "temperature": "37.0",
            "blood_pressure_systolic": "120",
            "blood_pressure_diastolic": "80",
            "heart_rate": "75", 
            "respiratory_rate": "16",
            "pain_level": 3
        }),
        "condition_data": json.dumps({  # ✅ Convert to JSON string
            "selected_condition": "orthopedic",
            "pain_location": "Right Knee",
            "limb_color": "normal",
            "limb_temperature": "normal",
            "capillary_refill": "normal",
            "limb_movement": "normal",
            "limb_sensation": "normal",
            "distal_pulse": "present",
            "wound_condition": "clean",
            "wound_swelling": "none",
            "mobility_level": "assisted",
            "weight_bearing_status": "partial",
            "assistive_device": "crutches",
            "has_drain": False,
            "drain_output": None,
            "drain_color": None,
            "additional_notes": "Test orthopedic entry",
            "status": "good"
        })
    }
    
    try:
        with engine.connect() as conn:
            # Insert test data
            insert_sql = text("""
                INSERT INTO orthopedic_surgery_entries 
                (patient_id, patient_name, surgery_type, submission_date, common_data, condition_data)
                VALUES (:patient_id, :patient_name, :surgery_type, :submission_date, :common_data, :condition_data)
            """)
            
            conn.execute(insert_sql, test_data)
            conn.commit()
            print("✅ Test data inserted successfully!")
            
            # Retrieve and verify
            select_sql = text("SELECT * FROM orthopedic_surgery_entries WHERE patient_id = 999")
            result = conn.execute(select_sql).fetchone()
            
            if result:
                print("✅ Data retrieval successful!")
                print(f"   ID: {result.id}")
                print(f"   Patient: {result.patient_name}")
                print(f"   Surgery Type: {result.surgery_type}")
                
                # Parse JSON back to dict for display
                common_data = json.loads(result.common_data) if result.common_data else {}
                condition_data = json.loads(result.condition_data) if result.condition_data else {}
                
                print(f"   Common Data: {common_data}")
                print(f"   Condition Data Pain Location: {condition_data.get('pain_location')}")
                print(f"   Condition Data Status: {condition_data.get('status')}")
            else:
                print("❌ Could not retrieve inserted data!")
                return False
            
            # Clean up
            delete_sql = text("DELETE FROM orthopedic_surgery_entries WHERE patient_id = 999")
            conn.execute(delete_sql)
            conn.commit()
            print("✅ Test data cleaned up!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_orthopedic_data_insertion()
    if success:
        print("\n🎉 ORTHOPEDIC BACKEND IS READY!")
        print("   Your React component should now work!")
    else:
        print("\n❌ There's still an issue with the orthopedic backend.")