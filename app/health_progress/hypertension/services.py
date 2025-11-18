# app/health_progress/hypertension/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import HypertensionEntry

class HypertensionProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry_data: Dict[str, Any]) -> HypertensionEntry:
        """
        Create a new hypertension progress entry - USE FLAT FIELDS
        """
        try:
            print("🔍 HYPERTENSION SERVICES: Starting create_entry...")
            print(f"📥 HYPERTENSION SERVICES: Received data: {entry_data}")
            
            # ✅ USE FLAT FIELDS DIRECTLY
            db_entry = HypertensionEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                blood_pressure_systolic=entry_data.get('blood_pressure_systolic'),
                blood_pressure_diastolic=entry_data.get('blood_pressure_diastolic'),
                energy_level=entry_data.get('energy_level'),
                sleep_hours=entry_data.get('sleep_hours'),
                sleep_quality=entry_data.get('sleep_quality'),
                medications=entry_data.get('medications', {}),
                symptoms=entry_data.get('symptoms', {}),
                notes=entry_data.get('notes', ''),
                status=entry_data.get('status', 'monitor'),
                condition_type='hypertension'
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ HYPERTENSION SERVICES: Entry created successfully with ID: {db_entry.id}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ HYPERTENSION SERVICES: Error creating entry: {str(e)}")
            raise Exception(f"Error creating hypertension entry: {str(e)}")

    def get_all_entries(self) -> List[HypertensionEntry]:
        """
        Get all hypertension entries ordered by most recent
        """
        try:
            entries = self.db.query(HypertensionEntry).order_by(
                HypertensionEntry.created_at.desc()
            ).all()
            
            print(f"✅ HYPERTENSION SERVICES: Retrieved {len(entries)} hypertension entries")
            return entries
            
        except Exception as e:
            print(f"❌ HYPERTENSION SERVICES: Error fetching all hypertension entries: {str(e)}")
            raise Exception(f"Error fetching hypertension entries: {str(e)}")

    def get_entry_by_patient_and_date(self, patient_id: int, date_str: str) -> Optional[HypertensionEntry]:
        """
        Get hypertension entry for specific patient and date
        """
        try:
            print(f"🔍 HYPERTENSION SERVICES: Getting entry for patient {patient_id} on {date_str}")
            
            entry = self.db.query(HypertensionEntry).filter(
                HypertensionEntry.patient_id == patient_id,
                HypertensionEntry.submission_date == date_str
            ).first()
            
            print(f"✅ HYPERTENSION SERVICES: Entry found: {entry is not None}")
            return entry
            
        except Exception as e:
            print(f"❌ HYPERTENSION SERVICES: Error getting entry by patient and date: {str(e)}")
            raise Exception(f"Error getting hypertension entry: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a hypertension entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(HypertensionEntry).filter(
                HypertensionEntry.patient_id == patient_id,
                HypertensionEntry.submission_date == date_str
            ).first()
            
            exists = existing_entry is not None
            print(f"🔍 HYPERTENSION SERVICES: Entry exists for patient {patient_id} on {date_str}: {exists}")
            return exists
            
        except Exception as e:
            print(f"❌ HYPERTENSION SERVICES: Error checking hypertension entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[HypertensionEntry]:
        """
        Get all hypertension entries for a specific patient
        """
        try:
            entries = self.db.query(HypertensionEntry).filter(
                HypertensionEntry.patient_id == patient_id
            ).order_by(HypertensionEntry.created_at.desc()).all()
            
            print(f"✅ HYPERTENSION SERVICES: Retrieved {len(entries)} entries for patient {patient_id}")
            return entries
            
        except Exception as e:
            print(f"❌ HYPERTENSION SERVICES: Error fetching patient entries: {str(e)}")
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[HypertensionEntry]:
        """
        Get recent hypertension entries across all patients
        """
        try:
            entries = self.db.query(HypertensionEntry).order_by(
                HypertensionEntry.created_at.desc()
            ).limit(limit).all()
            
            print(f"✅ HYPERTENSION SERVICES: Retrieved {len(entries)} recent entries")
            return entries
            
        except Exception as e:
            print(f"❌ HYPERTENSION SERVICES: Error fetching recent entries: {str(e)}")
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a hypertension entry by ID
        """
        try:
            entry = self.db.query(HypertensionEntry).filter(
                HypertensionEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                print(f"✅ HYPERTENSION SERVICES: Deleted entry with ID: {entry_id}")
                return True
            
            print(f"⚠️ HYPERTENSION SERVICES: Entry with ID {entry_id} not found")
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ HYPERTENSION SERVICES: Error deleting hypertension entry: {str(e)}")
            raise Exception(f"Error deleting hypertension entry: {str(e)}")

    def update_entry(self, entry_id: int, update_data: Dict[str, Any]) -> Optional[HypertensionEntry]:
        """
        Update an existing hypertension entry - USE FLAT FIELDS
        """
        try:
            entry = self.db.query(HypertensionEntry).filter(
                HypertensionEntry.id == entry_id
            ).first()
            
            if not entry:
                print(f"⚠️ HYPERTENSION SERVICES: Entry with ID {entry_id} not found for update")
                return None
            
            # ✅ UPDATE FLAT FIELDS DIRECTLY
            flat_fields = [
                'blood_pressure_systolic', 'blood_pressure_diastolic', 'energy_level',
                'sleep_hours', 'sleep_quality', 'medications', 'symptoms', 'notes',
                'status', 'patient_name', 'submission_date', 'condition_type'
            ]
            
            for field in flat_fields:
                if field in update_data:
                    setattr(entry, field, update_data[field])
            
            self.db.commit()
            self.db.refresh(entry)
            
            print(f"✅ HYPERTENSION SERVICES: Updated entry with ID: {entry_id}")
            return entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ HYPERTENSION SERVICES: Error updating hypertension entry: {str(e)}")
            raise Exception(f"Error updating hypertension entry: {str(e)}")