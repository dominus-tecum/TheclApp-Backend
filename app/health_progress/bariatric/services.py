# app/health_progress/bariatric/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import BariatricEntry

class BariatricProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: Dict[str, Any]) -> BariatricEntry:
        """
        Create a new bariatric progress entry
        """
        try:
            print("🔍 BARIATRIC SERVICES: Starting create_entry...")
            
            db_entry = BariatricEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                submitted_at=datetime.utcnow(),
                urgency_status=entry_data.get('urgency_status', 'low'),
                common_data=entry_data.get('common_data', {}),
                condition_data=entry_data.get('condition_data', {})
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ BARIATRIC SERVICES: Entry created successfully with ID: {db_entry.id}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ BARIATRIC SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating bariatric entry: {str(e)}")

    def get_all_entries(self) -> List[BariatricEntry]:
        """
        Get all bariatric entries ordered by most recent
        """
        try:
            entries = self.db.query(BariatricEntry).order_by(
                BariatricEntry.submitted_at.desc()
            ).all()
            
            print(f"✅ BARIATRIC SERVICES: Retrieved {len(entries)} bariatric entries")
            return entries
            
        except Exception as e:
            print(f"❌ BARIATRIC SERVICES: Error fetching all bariatric entries: {str(e)}")
            raise Exception(f"Error fetching bariatric entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a bariatric entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(BariatricEntry).filter(
                BariatricEntry.patient_id == patient_id,
                BariatricEntry.submission_date == date_str
            ).first()
            
            return existing_entry
            
        except Exception as e:
            print(f"❌ BARIATRIC SERVICES: Error checking bariatric entry: {e}")
            return None






    def get_patient_entries(self, patient_id: int) -> List[BariatricEntry]:
        """
        Get all bariatric entries for a specific patient
        """
        try:
            entries = self.db.query(BariatricEntry).filter(
                BariatricEntry.patient_id == patient_id
            ).order_by(BariatricEntry.submitted_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[BariatricEntry]:
        """
        Get recent bariatric entries across all patients
        """
        try:
            entries = self.db.query(BariatricEntry).order_by(
                BariatricEntry.submitted_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a bariatric entry by ID
        """
        try:
            entry = self.db.query(BariatricEntry).filter(
                BariatricEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting bariatric entry: {str(e)}")