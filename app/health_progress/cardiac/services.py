# app/health_progress/cardiac/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import CardiacSurgeryEntry

class CardiacProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: Dict[str, Any]) -> CardiacSurgeryEntry:
        """
        Create a new cardiac surgery progress entry - STORE AS JSON like cesarean
        """
        try:
            print("🔍 CARDIAC SERVICES: Starting create_entry...")
            
            # Convert submission_date string to date object
            submission_date_str = entry_data.get('submission_date')
            if isinstance(submission_date_str, str):
                submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d").date()
            else:
                submission_date = datetime.utcnow().date()
            
            print(f"🔍 CARDIAC SERVICES: submission_date: {submission_date}")
            
            # ✅ SIMPLE INTEGER patient_id like cesarean (no foreign key)
            db_entry = CardiacSurgeryEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                surgery_type=entry_data.get('surgery_type', 'cardiac'),
                submission_date=submission_date,
                
                # ✅ DIRECT JSON STORAGE like cesarean
                common_data=entry_data.get('common_data', {}),
                condition_data=entry_data.get('condition_data', {})
            )
            
            print("🔍 CARDIAC SERVICES: Database entry created, about to add to session...")
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ CARDIAC SERVICES: Entry created successfully with ID: {db_entry.id}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ CARDIAC SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating cardiac entry: {str(e)}")

    def get_all_entries(self) -> List[CardiacSurgeryEntry]:
        """
        Get all cardiac entries ordered by most recent
        """
        try:
            entries = self.db.query(CardiacSurgeryEntry).order_by(
                CardiacSurgeryEntry.created_at.desc()
            ).all()
            
            print(f"✅ CARDIAC SERVICES: Retrieved {len(entries)} cardiac entries")
            return entries
            
        except Exception as e:
            print(f"❌ CARDIAC SERVICES: Error fetching all cardiac entries: {str(e)}")
            raise Exception(f"Error fetching cardiac entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a cardiac entry exists for a patient on a specific date
        """
        try:
            if isinstance(date_str, str):
                submission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                submission_date = date_str
            
            existing_entry = self.db.query(CardiacSurgeryEntry).filter(
                CardiacSurgeryEntry.patient_id == patient_id,
                CardiacSurgeryEntry.submission_date == submission_date
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"❌ CARDIAC SERVICES: Error checking cardiac entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[CardiacSurgeryEntry]:
        """
        Get all cardiac entries for a specific patient
        """
        try:
            entries = self.db.query(CardiacSurgeryEntry).filter(
                CardiacSurgeryEntry.patient_id == patient_id
            ).order_by(CardiacSurgeryEntry.created_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[CardiacSurgeryEntry]:
        """
        Get recent cardiac entries across all patients
        """
        try:
            entries = self.db.query(CardiacSurgeryEntry).order_by(
                CardiacSurgeryEntry.created_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a cardiac entry by ID
        """
        try:
            entry = self.db.query(CardiacSurgeryEntry).filter(
                CardiacSurgeryEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting cardiac entry: {str(e)}")