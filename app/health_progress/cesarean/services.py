# app/health_progress/cesarean/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import CesareanSectionEntry

class CesareanProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: Dict[str, Any]) -> CesareanSectionEntry:
        """
        Create a new cesarean section progress entry - STORE AS JSON like abdominal
        """
        try:
            print("🔍 SERVICES: Starting create_entry...")
            
            # Convert submission_date string to date object
            submission_date_str = entry_data.get('submission_date')
            if isinstance(submission_date_str, str):
                submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d").date()
            else:
                submission_date = datetime.utcnow().date()
            
            print(f"🔍 SERVICES: submission_date: {submission_date}")
            
            # ✅ SIMPLE INTEGER patient_id like abdominal (no foreign key)
            db_entry = CesareanSectionEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                surgery_type=entry_data.get('surgery_type', 'cesarean'),
                submission_date=submission_date,
                
                # ✅ DIRECT JSON STORAGE like abdominal
                common_data=entry_data.get('common_data', {}),
                condition_data=entry_data.get('condition_data', {})
            )
            
            print("🔍 SERVICES: Database entry created, about to add to session...")
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ SERVICES: Entry created successfully with ID: {db_entry.id}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating cesarean entry: {str(e)}")

    def get_all_entries(self) -> List[CesareanSectionEntry]:
        """
        Get all cesarean entries ordered by most recent
        """
        try:
            entries = self.db.query(CesareanSectionEntry).order_by(
                CesareanSectionEntry.created_at.desc()
            ).all()
            
            print(f"✅ SERVICES: Retrieved {len(entries)} cesarean entries")
            return entries
            
        except Exception as e:
            print(f"❌ SERVICES: Error fetching all cesarean entries: {str(e)}")
            raise Exception(f"Error fetching cesarean entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a cesarean entry exists for a patient on a specific date
        """
        try:
            if isinstance(date_str, str):
                submission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                submission_date = date_str
            
            existing_entry = self.db.query(CesareanSectionEntry).filter(
                CesareanSectionEntry.patient_id == patient_id,
                CesareanSectionEntry.submission_date == submission_date
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"Error checking cesarean entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[CesareanSectionEntry]:
        """
        Get all cesarean entries for a specific patient
        """
        try:
            entries = self.db.query(CesareanSectionEntry).filter(
                CesareanSectionEntry.patient_id == patient_id
            ).order_by(CesareanSectionEntry.created_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[CesareanSectionEntry]:
        """
        Get recent cesarean entries across all patients
        """
        try:
            entries = self.db.query(CesareanSectionEntry).order_by(
                CesareanSectionEntry.created_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a cesarean entry by ID
        """
        try:
            entry = self.db.query(CesareanSectionEntry).filter(
                CesareanSectionEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting cesarean entry: {str(e)}")