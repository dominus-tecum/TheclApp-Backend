from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List
from .models import LifelongEntry

class LifelongService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_entry(self, entry_data: Dict[str, Any], organization_id: int) -> LifelongEntry:
        # Check if entry exists for this patient and date
        existing = self.db.query(LifelongEntry).filter(
            LifelongEntry.patient_id == entry_data.get('patient_id'),
            LifelongEntry.submission_date == entry_data.get('submission_date'),
            LifelongEntry.organization_id == organization_id
        ).first()
        
        if existing:
            # Update existing
            existing.common_data = entry_data.get('common_data', {})
            existing.conditions_data = entry_data.get('conditions_data', {})
            existing.status = entry_data.get('status', 'good')
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new
            db_entry = LifelongEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name'),
                organization_id=organization_id,
                submission_date=entry_data.get('submission_date'),
                common_data=entry_data.get('common_data', {}),
                conditions_data=entry_data.get('conditions_data', {}),
                status=entry_data.get('status', 'good')
            )
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            return db_entry

    def get_all_entries(self, organization_id: int) -> List[LifelongEntry]:
        return self.db.query(LifelongEntry).filter(
           LifelongEntry.organization_id == organization_id
        ).order_by(LifelongEntry.submission_date.desc()).all()

    def get_patient_entries(self, patient_id: int, organization_id: int) -> List[LifelongEntry]:
        return self.db.query(LifelongEntry).filter(
           LifelongEntry.patient_id == patient_id,
           LifelongEntry.organization_id == organization_id  # ← ADD COMMA ABOVE
        ).order_by(LifelongEntry.submission_date.desc()).all()

    def get_entry_by_date(self, patient_id: int, date: str, organization_id: int):
        return self.db.query(LifelongEntry).filter(
            LifelongEntry.patient_id == patient_id,
            LifelongEntry.submission_date == date,
            LifelongEntry.organization_id == organization_id
        ).first()
    
    def check_existing_entry(self, patient_id: int, date: str, organization_id: int) -> bool:
        return self.get_entry_by_date(patient_id, date,organization_id) is not None
    
    def delete_entry(self, entry_id: int, organization_id: int) -> bool:
        entry = self.db.query(LifelongEntry).filter(
            LifelongEntry.id == entry_id,
            LifelongEntry.organization_id == organization_id
            ).first()
        if entry:
            self.db.delete(entry)
            self.db.commit()
            return True
        return False