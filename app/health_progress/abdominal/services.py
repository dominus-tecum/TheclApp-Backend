from sqlalchemy.orm import Session
from . import models
from typing import List
import logging

logger = logging.getLogger(__name__)

class AbdominalProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: dict) -> models.AbdominalEntry:
        """
        Create abdominal progress entry from raw JSON data (mobile app format)
        """
        try:
            logger.info(f"📱 Received data from mobile app: {list(entry_data.keys())}")
            
            # ✅ Handle raw JSON data from mobile app
            db_entry = models.AbdominalEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name'),
                submission_date=entry_data.get('submission_date'),
                common_data=entry_data.get('common_data', {}),  # Direct from JSON
                condition_data=entry_data.get('condition_data', {})  # Direct from JSON
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            logger.info(f"✅ Abdominal progress entry created for patient {entry_data.get('patient_id')}")
            logger.info(f"📊 Common data stored: {entry_data.get('common_data', {})}")
            logger.info(f"📊 Condition data stored: {entry_data.get('condition_data', {})}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Database error creating abdominal entry: {str(e)}")
            raise

    def get_patient_entries(self, patient_id: int) -> List[models.AbdominalEntry]:
        """
        Get all entries for a specific patient
        """
        return self.db.query(models.AbdominalEntry)\
            .filter(models.AbdominalEntry.patient_id == patient_id)\
            .order_by(models.AbdominalEntry.submission_date.desc())\
            .all()

    def get_entry_by_id(self, entry_id: int) -> models.AbdominalEntry:
        """
        Get a specific entry by ID
        """
        return self.db.query(models.AbdominalEntry)\
            .filter(models.AbdominalEntry.id == entry_id)\
            .first()

    def check_existing_entry(self, patient_id: int, date: str) -> bool:
        """
        Check if an entry already exists for a patient on a specific date
        """
        existing = self.db.query(models.AbdominalEntry)\
            .filter(
                models.AbdominalEntry.patient_id == patient_id,
                models.AbdominalEntry.submission_date == date
            )\
            .first()
        return existing is not None

    def get_all_entries(self) -> List[models.AbdominalEntry]:
        """
        Get all abdominal progress entries for dashboard display
        """
        return self.db.query(models.AbdominalEntry)\
            .order_by(models.AbdominalEntry.created_at.desc())\
            .all()