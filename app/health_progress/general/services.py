from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import GeneralHealthEntry

class GeneralProgressService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_urgency_level(self, entry_data: Dict[str, Any]) -> str:
        """
        Calculate urgency level based on general health medical values
        """
        urgency_score = 0
        
        # Health trend urgency
        health_trend = entry_data.get('health_trend')
        if health_trend == 'significantly_worse':
            urgency_score += 3  # Rapid decline
        elif health_trend == 'slightly_worse':
            urgency_score += 1  # Slow decline
        
        # Overall wellbeing urgency
        wellbeing = entry_data.get('overall_wellbeing', 5)
        if wellbeing <= 2:
            urgency_score += 3  # Very poor wellbeing
        elif wellbeing <= 4:
            urgency_score += 1  # Poor wellbeing
        
        # Primary symptom severity urgency
        symptom_severity = entry_data.get('primary_symptom_severity', 0)
        if symptom_severity >= 9:
            urgency_score += 3  # Severe symptoms
        elif symptom_severity >= 7:
            urgency_score += 2  # Moderate-severe symptoms
        elif symptom_severity >= 5:
            urgency_score += 1  # Moderate symptoms
        
        # Determine urgency level
        if urgency_score >= 5:
            return "high"
        elif urgency_score >= 3:
            return "medium"
        else:
            return "low"

    def create_entry(self, entry_data: Dict[str, Any]) -> GeneralHealthEntry:
        """
        Create a new general health progress entry with flattened structure
        """
        try:
            print("🔍 GENERAL SERVICES: Starting create_entry with flattened structure...")
            
            # ✅ Calculate urgency based on medical values
            urgency_status = self.calculate_urgency_level(entry_data)
            print(f"🎯 GENERAL SERVICES: Calculated urgency: {urgency_status}")
            
            # ✅ Create entry with EXACT frontend data types
            db_entry = GeneralHealthEntry(
                # Basic info
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                status=entry_data.get('status', 'pending'),
                
                # General health specific fields
                health_trend=entry_data.get('health_trend'),
                overall_wellbeing=entry_data.get('overall_wellbeing'),
                primary_symptom_severity=entry_data.get('primary_symptom_severity'),
                primary_symptom_description=entry_data.get('primary_symptom_description'),
                notes=entry_data.get('notes'),
                
                # Condition type and timestamps
                condition_type=entry_data.get('condition_type', 'general_health'),
                submitted_at=datetime.utcnow(),
                urgency_status=urgency_status  # ✅ Use calculated urgency
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ GENERAL SERVICES: Entry created successfully with ID: {db_entry.id}, Urgency: {db_entry.urgency_status}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ GENERAL SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating general health entry: {str(e)}")

    def get_all_entries(self) -> List[GeneralHealthEntry]:
        """
        Get all general health entries ordered by most recent
        """
        try:
            entries = self.db.query(GeneralHealthEntry).order_by(
                GeneralHealthEntry.submitted_at.desc()
            ).all()
            
            print(f"✅ GENERAL SERVICES: Retrieved {len(entries)} general health entries")
            return entries
            
        except Exception as e:
            print(f"❌ GENERAL SERVICES: Error fetching all general health entries: {str(e)}")
            raise Exception(f"Error fetching general health entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a general health entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(GeneralHealthEntry).filter(
                GeneralHealthEntry.patient_id == patient_id,
                GeneralHealthEntry.submission_date == date_str
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"❌ GENERAL SERVICES: Error checking general health entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[GeneralHealthEntry]:
        """
        Get all general health entries for a specific patient
        """
        try:
            entries = self.db.query(GeneralHealthEntry).filter(
                GeneralHealthEntry.patient_id == patient_id
            ).order_by(GeneralHealthEntry.submitted_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[GeneralHealthEntry]:
        """
        Get recent general health entries across all patients
        """
        try:
            entries = self.db.query(GeneralHealthEntry).order_by(
                GeneralHealthEntry.submitted_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a general health entry by ID
        """
        try:
            entry = self.db.query(GeneralHealthEntry).filter(
                GeneralHealthEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting general health entry: {str(e)}")