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
        try:
            print("🔍 DIABETES SERVICES: Starting create_entry...")

            print(f"🔍 Looking for patient_id: {entry_data.get('patient_id')}, submission_date: {entry_data.get('submission_date')}")
            print(f"🔍 Type of patient_id in DB: {DiabetesEntry.patient_id.type}")
            print(f"🔍 Type of submission_date in DB: {DiabetesEntry.submission_date.type}")


            
            # ✅ CHECK FOR EXISTING ENTRY ON SAME DATE
            existing_entry = self.db.query(DiabetesEntry).filter(
                DiabetesEntry.patient_id == entry_data.get('patient_id'),
                DiabetesEntry.submission_date == entry_data.get('submission_date')
            ).first()
            
            if existing_entry:
                print(f"🔄 DIABETES SERVICES: Updating existing entry for {entry_data.get('submission_date')}")
                existing_entry.blood_glucose = entry_data.get('blood_glucose')
                existing_entry.blood_pressure_systolic = entry_data.get('blood_pressure_systolic')
                existing_entry.blood_pressure_diastolic = entry_data.get('blood_pressure_diastolic')
                existing_entry.energy_level = entry_data.get('energy_level')
                existing_entry.sleep_hours = entry_data.get('sleep_hours')
                existing_entry.sleep_quality = entry_data.get('sleep_quality')
                existing_entry.medications = entry_data.get('medications')
                existing_entry.symptoms = entry_data.get('symptoms')
                existing_entry.notes = entry_data.get('notes')
                existing_entry.status = entry_data.get('status')
                existing_entry.condition_type = entry_data.get('condition_type', 'diabetes')
                
                self.db.commit()
                self.db.refresh(existing_entry)
                return existing_entry
            else:
                # Create new entry
                db_entry = DiabetesEntry(
                    patient_id=entry_data.get('patient_id'),
                    patient_name=entry_data.get('patient_name', ''),
                    submission_date=entry_data.get('submission_date'),
                    blood_glucose=entry_data.get('blood_glucose'),
                    blood_pressure_systolic=entry_data.get('blood_pressure_systolic'),
                    blood_pressure_diastolic=entry_data.get('blood_pressure_diastolic'),
                    energy_level=entry_data.get('energy_level'),
                    sleep_hours=entry_data.get('sleep_hours'),
                    sleep_quality=entry_data.get('sleep_quality'),
                    medications=entry_data.get('medications'),
                    symptoms=entry_data.get('symptoms'),
                    notes=entry_data.get('notes'),
                    status=entry_data.get('status'),
                    condition_type=entry_data.get('condition_type', 'diabetes')
                )
                
                self.db.add(db_entry)
                self.db.commit()
                self.db.refresh(db_entry)
                print(f"✅ DIABETES SERVICES: Entry created successfully with ID: {db_entry.id}")
                return db_entry
                
        except Exception as e:
            self.db.rollback()
            print(f"❌ DIABETES SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating/updating diabetes entry: {str(e)}")

    def get_all_entries(self) -> List[DiabetesEntry]:
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
        try:
            entries = self.db.query(DiabetesEntry).filter(
                DiabetesEntry.patient_id == patient_id
            ).order_by(DiabetesEntry.created_at.desc()).all()
            return entries
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[DiabetesEntry]:
        try:
            entries = self.db.query(DiabetesEntry).order_by(
                DiabetesEntry.created_at.desc()
            ).limit(limit).all()
            return entries
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
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