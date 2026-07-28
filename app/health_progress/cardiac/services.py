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
        Create or update a cardiac surgery progress entry (UPSERT)
        """
        try:
            print("🔍 CARDIAC SERVICES: Starting upsert...")
            
            # Convert submission_date string to date object
            submission_date_str = entry_data.get('submission_date')
            if isinstance(submission_date_str, str):
                submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d").date()
            else:
                submission_date = datetime.utcnow().date()
            
            patient_id = entry_data.get('patient_id')
            
            # Check if entry already exists for this patient and date
            existing_entry = self.db.query(CardiacSurgeryEntry).filter(
                CardiacSurgeryEntry.patient_id == patient_id,
                CardiacSurgeryEntry.submission_date == submission_date
            ).first()
            
            if existing_entry:
                # UPDATE existing entry
                print(f"🔄 CARDIAC SERVICES: Updating existing entry ID: {existing_entry.id}")
                
                existing_entry.patient_name = entry_data.get('patient_name', '')
                existing_entry.surgery_type = entry_data.get('surgery_type', 'cardiac')
                existing_entry.common_data = entry_data.get('common_data', {})
                existing_entry.condition_data = entry_data.get('condition_data', {})
                existing_entry.photo_urls = entry_data.get('photo_urls', [])
                
                self.db.commit()
                self.db.refresh(existing_entry)
                return existing_entry
            else:
                # CREATE new entry
                print(f"✨ CARDIAC SERVICES: Creating new entry")
                
                db_entry = CardiacSurgeryEntry(
                    patient_id=patient_id,
                    patient_name=entry_data.get('patient_name', ''),
                    surgery_type=entry_data.get('surgery_type', 'cardiac'),
                    submission_date=submission_date,
                    common_data=entry_data.get('common_data', {}),
                    condition_data=entry_data.get('condition_data', {}),
                    photo_urls=entry_data.get('photo_urls', [])
                )
                
                self.db.add(db_entry)
                self.db.commit()
                self.db.refresh(db_entry)
                return db_entry
                
        except Exception as e:
            self.db.rollback()
            print(f"❌ CARDIAC SERVICES: Error: {str(e)}")
            raise Exception(f"Error upserting cardiac entry: {str(e)}")

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

    def check_existing_entry(self, patient_id: int, date_str: str):
        """
        Returns entry object or None
        """
        try:
            if isinstance(date_str, str):
                submission_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                submission_date = date_str
            
            return self.db.query(CardiacSurgeryEntry).filter(
                CardiacSurgeryEntry.patient_id == patient_id,
                CardiacSurgeryEntry.submission_date == submission_date
            ).first()
            
        except Exception as e:
            print(f"❌ CARDIAC SERVICES: Error checking cardiac entry: {e}")
            return None

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