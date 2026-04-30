from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import CancerEntry

class CancerProgressService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_urgency_level(self, entry_data: Dict[str, Any]) -> str:
        """
        Calculate urgency level based on cancer medical values
        """
        urgency_score = 0
        
        # Pain level urgency
        pain_level = entry_data.get('pain_level', 0)
        if pain_level >= 8:
            urgency_score += 3  # Severe pain
        elif pain_level >= 6:
            urgency_score += 2  # Moderate pain
        elif pain_level >= 4:
            urgency_score += 1  # Mild pain
        
        # Side effects urgency
        side_effects = entry_data.get('side_effects', 0)
        if side_effects >= 8:
            urgency_score += 3  # Severe side effects
        elif side_effects >= 6:
            urgency_score += 2  # Moderate side effects
        elif side_effects >= 4:
            urgency_score += 1  # Mild side effects
        
        # Blood pressure urgency
        systolic = entry_data.get('blood_pressure_systolic')
        diastolic = entry_data.get('blood_pressure_diastolic')
        
        try:
            systolic_int = int(systolic) if systolic else None
            diastolic_int = int(diastolic) if diastolic else None
        except (ValueError, TypeError):
            systolic_int = None
            diastolic_int = None
        
        if systolic_int and systolic_int >= 180:
            urgency_score += 2  # Hypertensive crisis
        elif systolic_int and systolic_int >= 160:
            urgency_score += 1  # Stage 2 hypertension
            
        if diastolic_int and diastolic_int >= 120:
            urgency_score += 2  # Hypertensive crisis
        elif diastolic_int and diastolic_int >= 100:
            urgency_score += 1  # Stage 2 hypertension
        
        # Energy level (fatigue from treatment)
        energy_level = entry_data.get('energy_level', 5)
        if energy_level <= 3:
            urgency_score += 1  # Severe fatigue
        
        # Determine urgency level
        if urgency_score >= 6:
            return "high"
        elif urgency_score >= 3:
            return "medium"
        else:
            return "low"

    def create_entry(self, entry_data: Dict[str, Any]) -> CancerEntry:
        """
        Create or update a cancer progress entry with flattened structure
        """
        try:
            print("🔍 CANCER SERVICES: Starting create_entry with flattened structure...")
            
            # ✅ CHECK FOR EXISTING ENTRY FIRST
            existing_entry = self.db.query(CancerEntry).filter(
                CancerEntry.patient_id == entry_data.get('patient_id'),
                CancerEntry.submission_date == entry_data.get('submission_date')
            ).first()
            
            if existing_entry:
                print(f"🔄 CANCER SERVICES: Updating existing entry for {entry_data.get('submission_date')}")
                
                # UPDATE existing entry
                existing_entry.blood_pressure_systolic = entry_data.get('blood_pressure_systolic')
                existing_entry.blood_pressure_diastolic = entry_data.get('blood_pressure_diastolic')
                existing_entry.energy_level = entry_data.get('energy_level')
                existing_entry.sleep_hours = entry_data.get('sleep_hours')
                existing_entry.sleep_quality = entry_data.get('sleep_quality')
                existing_entry.medications = entry_data.get('medications')
                existing_entry.symptoms = entry_data.get('symptoms')
                existing_entry.notes = entry_data.get('notes')
                existing_entry.status = entry_data.get('status', 'pending')
                existing_entry.pain_level = entry_data.get('pain_level')
                existing_entry.pain_location = entry_data.get('pain_location')
                existing_entry.side_effects = entry_data.get('side_effects')
                existing_entry.submitted_at = datetime.utcnow()
                
                # Recalculate urgency
                urgency_status = self.calculate_urgency_level(entry_data)
                existing_entry.urgency_status = urgency_status
                
                self.db.commit()
                self.db.refresh(existing_entry)
                print(f"✅ CANCER SERVICES: Entry updated successfully with ID: {existing_entry.id}")
                return existing_entry
            
            # If no existing entry, create new
            print("🆕 CANCER SERVICES: Creating new entry...")
            
            # ✅ Calculate urgency based on medical values
            urgency_status = self.calculate_urgency_level(entry_data)
            print(f"🎯 CANCER SERVICES: Calculated urgency: {urgency_status}")
            
            # ✅ Create entry with EXACT frontend data types
            db_entry = CancerEntry(
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                status=entry_data.get('status', 'pending'),
                blood_pressure_systolic=entry_data.get('blood_pressure_systolic'),
                blood_pressure_diastolic=entry_data.get('blood_pressure_diastolic'),
                energy_level=entry_data.get('energy_level'),
                sleep_hours=entry_data.get('sleep_hours'),
                sleep_quality=entry_data.get('sleep_quality'),
                medications=entry_data.get('medications'),
                symptoms=entry_data.get('symptoms'),
                notes=entry_data.get('notes'),
                pain_level=entry_data.get('pain_level'),
                pain_location=entry_data.get('pain_location'),
                side_effects=entry_data.get('side_effects'),
                condition_type=entry_data.get('condition_type', 'cancer'),
                submitted_at=datetime.utcnow(),
                urgency_status=urgency_status
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ CANCER SERVICES: Entry created successfully with ID: {db_entry.id}, Urgency: {db_entry.urgency_status}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ CANCER SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating/updating cancer entry: {str(e)}")











    def get_all_entries(self) -> List[CancerEntry]:
        """
        Get all cancer entries ordered by most recent
        """
        try:
            entries = self.db.query(CancerEntry).order_by(
                CancerEntry.submitted_at.desc()
            ).all()
            
            print(f"✅ CANCER SERVICES: Retrieved {len(entries)} cancer entries")
            return entries
            
        except Exception as e:
            print(f"❌ CANCER SERVICES: Error fetching all cancer entries: {str(e)}")
            raise Exception(f"Error fetching cancer entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a cancer entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(CancerEntry).filter(
                CancerEntry.patient_id == patient_id,
                CancerEntry.submission_date == date_str
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"❌ CANCER SERVICES: Error checking cancer entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[CancerEntry]:
        """
        Get all cancer entries for a specific patient
        """
        try:
            entries = self.db.query(CancerEntry).filter(
                CancerEntry.patient_id == patient_id
            ).order_by(CancerEntry.submitted_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[CancerEntry]:
        """
        Get recent cancer entries across all patients
        """
        try:
            entries = self.db.query(CancerEntry).order_by(
                CancerEntry.submitted_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a cancer entry by ID
        """
        try:
            entry = self.db.query(CancerEntry).filter(
                CancerEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting cancer entry: {str(e)}")