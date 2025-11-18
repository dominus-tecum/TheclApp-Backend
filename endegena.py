from app.database import SessionLocal
from app.health_progress.burn_care.models import BurnCareEntry

db = SessionLocal()
entries = db.query(BurnCareEntry).all()
print(f"Entries in hospiapp.db: {len(entries)}")
for entry in entries:
    print(f"ID: {entry.id}, Date: {entry.submission_date}, Condition Type: {getattr(entry, 'condition_type', 'MISSING')}")
db.close()