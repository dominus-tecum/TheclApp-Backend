# clean_duplicates.py
from app.database import SessionLocal
from app.health_progress.diabetes.models import DiabetesEntry
from app.health_progress.hypertension.models import HypertensionEntry
from app.health_progress.heart.models import HeartEntry
from app.health_progress.cancer.models import CancerEntry
from app.health_progress.kidney.models import KidneyEntry
from app.health_progress.burn_care.models import BurnCareEntry
from app.health_progress.urological.models import UrologicalSurgeryEntry
from app.health_progress.gynecologic.models import GynecologicSurgeryEntry
from app.health_progress.orthopedic.models import OrthopedicSurgeryEntry
from app.health_progress.cesarean.models import CesareanSectionEntry
from app.health_progress.bariatric.models import BariatricEntry
from app.health_progress.cardiac.models import CardiacSurgeryEntry
from app.health_progress.general.models import GeneralHealthEntry
from app.health_progress.lifelong.models import LifelongEntry

db = SessionLocal()

def clean_duplicates(model, table_name):
    print(f"\n🔍 Cleaning {table_name}...")
    
    # Get all entries ordered by id (oldest first)
    entries = db.query(model).order_by(model.id.asc()).all()
    
    if not entries:
        print(f"  ⚠️ No entries found in {table_name}")
        return 0
    
    seen = {}
    to_delete = []
    
    for entry in entries:
        key = (entry.patient_id, entry.submission_date)
        if key in seen:
            to_delete.append(entry.id)
            print(f"  🗑️ Will delete duplicate ID: {entry.id} for patient {entry.patient_id} on {entry.submission_date}")
        else:
            seen[key] = entry.id
            print(f"  ✅ Keeping ID: {entry.id} for patient {entry.patient_id} on {entry.submission_date}")
    
    if to_delete:
        db.query(model).filter(model.id.in_(to_delete)).delete(synchronize_session=False)
        db.commit()
        print(f"  ✅ Deleted {len(to_delete)} duplicate entries from {table_name}")
    else:
        print(f"  ✅ No duplicates found in {table_name}")
    
    return len(to_delete)

try:
    total_deleted = 0
    
    # Surgical trackers
    total_deleted += clean_duplicates(CardiacSurgeryEntry, "cardiac_surgery_entries")
    total_deleted += clean_duplicates(OrthopedicSurgeryEntry, "orthopedic_surgery_entries")
    total_deleted += clean_duplicates(CesareanSectionEntry, "cesarean_section_entries")
    total_deleted += clean_duplicates(BariatricEntry, "bariatric_entries")
    total_deleted += clean_duplicates(BurnCareEntry, "burn_care_entries")
    total_deleted += clean_duplicates(UrologicalSurgeryEntry, "urological_surgery_entries")
    total_deleted += clean_duplicates(GynecologicSurgeryEntry, "gynecologic_surgery_entries")
    
    # Chronic condition trackers
    total_deleted += clean_duplicates(DiabetesEntry, "diabetes_entries")
    total_deleted += clean_duplicates(HypertensionEntry, "hypertension_entries")
    total_deleted += clean_duplicates(HeartEntry, "heart_entries")
    total_deleted += clean_duplicates(CancerEntry, "cancer_entries")
    total_deleted += clean_duplicates(KidneyEntry, "kidney_entries")
    total_deleted += clean_duplicates(LifelongEntry, "lifelong_entries")
    
    # General health
    total_deleted += clean_duplicates(GeneralHealthEntry, "general_health_entries")
    
    print(f"\n{'='*50}")
    print(f"📊 TOTAL DUPLICATES DELETED: {total_deleted}")
    print(f"{'='*50}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()