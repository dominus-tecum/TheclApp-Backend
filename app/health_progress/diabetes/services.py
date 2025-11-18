# app/health_progress/diabetes/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import DiabetesEntry

class DiabetesProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: Dict[str, Any]) -> DiabetesEntry:
        """
        Create a new diabetes progress entry - MATCHES ACTUAL DB SCHEMA
        """
        try:
            print("🔍 DIABETES SERVICES: Starting create_entry...")
            
            # ✅ USE ACTUAL DB SCHEMA - NO submitted_at, NO urgency_status
            db_entry = DiabetesEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                common_data=entry_data.get('common_data', {}),
                condition_data=entry_data.get('condition_data', {})
                # created_at will be auto-set by default
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ DIABETES SERVICES: Entry created successfully with ID: {db_entry.id}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ DIABETES SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating diabetes entry: {str(e)}")

    def get_all_entries(self) -> List[DiabetesEntry]:
        """
        Get all diabetes entries ordered by most recent
        """
        try:
            entries = self.db.query(DiabetesEntry).order_by(
                DiabetesEntry.created_at.desc()
            ).all()
            
            print(f"✅ DIABETES SERVICES: Retrieved {len(entries)} diabetes entries")
            return entries
            
        except Exception as e:
            print(f"❌ DIABETES SERVICES: Error fetching all diabetes entries: {str(e)}")
            raise Exception(f"Error fetching diabetes entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a diabetes entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(DiabetesEntry).filter(
                DiabetesEntry.patient_id == patient_id,
                DiabetesEntry.submission_date == date_str
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"❌ DIABETES SERVICES: Error checking diabetes entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[DiabetesEntry]:
        """
        Get all diabetes entries for a specific patient
        """
        try:
            entries = self.db.query(DiabetesEntry).filter(
                DiabetesEntry.patient_id == patient_id
            ).order_by(DiabetesEntry.created_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[DiabetesEntry]:
        """
        Get recent diabetes entries across all patients
        """
        try:
            entries = self.db.query(DiabetesEntry).order_by(
                DiabetesEntry.created_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a diabetes entry by ID
        """
        try:
            entry = self.db.query(DiabetesEntry).filter(
                DiabetesEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting diabetes entry: {str(e)}")