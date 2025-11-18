# app/health_progress/kidney/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.database import SessionLocal
from .models import KidneyEntry

class KidneyProgressService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_urgency_level(self, entry_data: Dict[str, Any]) -> str:
        """
        Calculate urgency level based on kidney disease medical values
        """
        urgency_score = 0
        
        # Blood pressure urgency (hypertension concerns)
        systolic = entry_data.get('blood_pressure_systolic')
        diastolic = entry_data.get('blood_pressure_diastolic')
        
        # Convert string blood pressure to int for calculation
        try:
            systolic_int = int(systolic) if systolic else None
            diastolic_int = int(diastolic) if diastolic else None
        except (ValueError, TypeError):
            systolic_int = None
            diastolic_int = None
        
        if systolic_int and systolic_int >= 180:
            urgency_score += 3  # Hypertensive crisis
        elif systolic_int and systolic_int >= 160:
            urgency_score += 2  # Stage 2 hypertension
        elif systolic_int and systolic_int >= 140:
            urgency_score += 1  # Stage 1 hypertension
            
        if diastolic_int and diastolic_int >= 120:
            urgency_score += 3  # Hypertensive crisis
        elif diastolic_int and diastolic_int >= 100:
            urgency_score += 2  # Stage 2 hypertension
        elif diastolic_int and diastolic_int >= 90:
            urgency_score += 1  # Stage 1 hypertension
        
        # Breathing difficulty (fluid overload concern)
        breathing = entry_data.get('breathing_difficulty', 0)
        if breathing >= 8:
            urgency_score += 3  # Severe breathing issues
        elif breathing >= 6:
            urgency_score += 2  # Moderate breathing issues
        elif breathing >= 4:
            urgency_score += 1  # Mild breathing issues
    
        # Swelling level (edema concern)
        swelling = entry_data.get('swelling_level', 0)
        if swelling >= 8:
            urgency_score += 2  # Severe edema
        elif swelling >= 6:
            urgency_score += 1  # Moderate edema
        
        # Urine output (kidney function indicator)
        urine_output = entry_data.get('urine_output', '')
        if urine_output and ('less' in urine_output.lower() or 'decreased' in urine_output.lower()):
            urgency_score += 2
        elif urine_output and ('very low' in urine_output.lower() or 'none' in urine_output.lower()):
            urgency_score += 3
        
        # Severe symptoms that need attention
        fatigue = entry_data.get('fatigue_level', 0)
        nausea = entry_data.get('nausea_level', 0)
        itching = entry_data.get('itching_level', 0)
        
        if fatigue >= 8:
            urgency_score += 1
        if nausea >= 8:
            urgency_score += 2  # Nausea can indicate uremia
        if itching >= 8:
            urgency_score += 1
        
        # Determine urgency level
        if urgency_score >= 6:
            return "high"
        elif urgency_score >= 3:
            return "medium"
        else:
            return "low"

    def create_entry(self, entry_data: Dict[str, Any]) -> KidneyEntry:
        """
        Create a new kidney disease progress entry with flattened structure
        """
        try:
            print("🔍 KIDNEY SERVICES: Starting create_entry with flattened structure...")
            
            # ✅ Calculate urgency based on medical values
            urgency_status = self.calculate_urgency_level(entry_data)
            print(f"🎯 KIDNEY SERVICES: Calculated urgency: {urgency_status}")
            
            # ✅ Create entry with EXACT frontend data types
            db_entry = KidneyEntry(
                # Basic info
                patient_id=entry_data.get('patient_id'),
                patient_name=entry_data.get('patient_name', ''),
                submission_date=entry_data.get('submission_date'),
                status=entry_data.get('status', 'pending'),
                
                # Common data (exact frontend types)
                blood_pressure_systolic=entry_data.get('blood_pressure_systolic'),
                blood_pressure_diastolic=entry_data.get('blood_pressure_diastolic'),
                energy_level=entry_data.get('energy_level'),
                sleep_hours=entry_data.get('sleep_hours'),  # Keep as string
                sleep_quality=entry_data.get('sleep_quality'),
                medications=entry_data.get('medications'),  # Keep as dict
                symptoms=entry_data.get('symptoms'),        # Keep as dict
                notes=entry_data.get('notes'),
                
                # Kidney-specific fields
                weight=entry_data.get('weight'),
                swelling_level=entry_data.get('swelling_level'),
                urine_output=entry_data.get('urine_output'),
                fluid_intake=entry_data.get('fluid_intake'),
                breathing_difficulty=entry_data.get('breathing_difficulty'),
                fatigue_level=entry_data.get('fatigue_level'),
                nausea_level=entry_data.get('nausea_level'),
                itching_level=entry_data.get('itching_level'),
                
                # Condition type and timestamps
                condition_type=entry_data.get('condition_type', 'kidney'),
                submitted_at=datetime.utcnow(),
                urgency_status=urgency_status  # ✅ Use calculated urgency
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            print(f"✅ KIDNEY SERVICES: Entry created successfully with ID: {db_entry.id}, Urgency: {db_entry.urgency_status}")
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ KIDNEY SERVICES: Error: {str(e)}")
            raise Exception(f"Error creating kidney entry: {str(e)}")

    def get_all_entries(self) -> List[KidneyEntry]:
        """
        Get all kidney disease entries ordered by most recent
        """
        try:
            entries = self.db.query(KidneyEntry).order_by(
                KidneyEntry.submitted_at.desc()
            ).all()
            
            print(f"✅ KIDNEY SERVICES: Retrieved {len(entries)} kidney entries")
            return entries
            
        except Exception as e:
            print(f"❌ KIDNEY SERVICES: Error fetching all kidney entries: {str(e)}")
            raise Exception(f"Error fetching kidney entries: {str(e)}")

    def check_existing_entry(self, patient_id: int, date_str: str) -> bool:
        """
        Check if a kidney disease entry exists for a patient on a specific date
        """
        try:
            existing_entry = self.db.query(KidneyEntry).filter(
                KidneyEntry.patient_id == patient_id,
                KidneyEntry.submission_date == date_str
            ).first()
            
            return existing_entry is not None
            
        except Exception as e:
            print(f"❌ KIDNEY SERVICES: Error checking kidney entry: {e}")
            return False

    def get_patient_entries(self, patient_id: int) -> List[KidneyEntry]:
        """
        Get all kidney disease entries for a specific patient
        """
        try:
            entries = self.db.query(KidneyEntry).filter(
                KidneyEntry.patient_id == patient_id
            ).order_by(KidneyEntry.submitted_at.desc()).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching patient entries: {str(e)}")

    def get_recent_entries(self, limit: int = 50) -> List[KidneyEntry]:
        """
        Get recent kidney disease entries across all patients
        """
        try:
            entries = self.db.query(KidneyEntry).order_by(
                KidneyEntry.submitted_at.desc()
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching recent entries: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a kidney disease entry by ID
        """
        try:
            entry = self.db.query(KidneyEntry).filter(
                KidneyEntry.id == entry_id
            ).first()
            
            if entry:
                self.db.delete(entry)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting kidney entry: {str(e)}")