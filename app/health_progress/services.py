from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from . import models, schemas

class ProgressService:
    def __init__(self, db: Session):
        self.db = db

    def create_progress_entry(self, entry_data: dict, patient_id: int) -> models.ProgressEntry:
        """Create a new progress entry for LifelongScreen"""
        try:
            # Create the database entry
            db_entry = models.ProgressEntry(
                patient_id=patient_id,
                common_data=entry_data["common_data"],
                condition_data=entry_data["condition_data"],
                status=entry_data.get("status", schemas.EntryStatus.DRAFT),
                submitted_at=entry_data.get("submitted_at")
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            return db_entry
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_patient_conditions(self, patient_id: int) -> List[str]:
        """Get patient's chronic conditions mapped to 5 categories"""
        # Mock data - replace with actual database query
        chronic_conditions = []
        
        # In a real app, you'd query the database:
        # conditions = self.db.query(models.PatientCondition).filter(
        #     models.PatientCondition.patient_id == patient_id,
        #     models.PatientCondition.is_active == True
        # ).all()
        
        # For now, return mock conditions for testing
        mock_conditions = ["diabetes", "hypertension", "heart_disease"]
        
        # Map to our 5 categories
        condition_mapping = {
            'diabetes': 'diabetes',
            'hypertension': 'hypertension', 
            'heart_disease': 'heart',
            'cardiovascular': 'heart',
            'cancer': 'cancer',
            'kidney_disease': 'kidney',
            'ckd': 'kidney'
        }
        
        for condition in mock_conditions:
            mapped_condition = condition_mapping.get(condition.lower())
            if mapped_condition and mapped_condition not in chronic_conditions:
                chronic_conditions.append(mapped_condition)
        
        return chronic_conditions

    def get_progress_entries(self, patient_id: int, filter: str = "all", limit: int = 50) -> List[models.ProgressEntry]:
        """Get progress entries with filtering"""
        query = self.db.query(models.ProgressEntry).filter(
            models.ProgressEntry.patient_id == patient_id
        )
        
        if filter != "all":
            query = query.filter(models.ProgressEntry.status == filter)
        
        return query.order_by(models.ProgressEntry.submitted_at.desc()).limit(limit).all()

    def get_recent_entries(self, patient_id: int, limit: int = 5) -> List[models.ProgressEntry]:
        """Get recent progress entries for dashboard"""
        return self.db.query(models.ProgressEntry).filter(
            models.ProgressEntry.patient_id == patient_id
        ).order_by(models.ProgressEntry.submitted_at.desc()).limit(limit).all()

    def get_dashboard_stats(self, patient_id: int) -> schemas.DashboardStats:
        """Get dashboard statistics for LifelongScreen"""
        # Mock data - replace with actual calculations
        total_entries = self.db.query(models.ProgressEntry).filter(
            models.ProgressEntry.patient_id == patient_id,
            models.ProgressEntry.status == schemas.EntryStatus.SUBMITTED
        ).count()
        
        # Calculate compliance rate (example: 85%)
        compliance_rate = min(85.0 + (total_entries * 2), 100.0)
        
        # Calculate streak (example: 7 days)
        streak_days = min(7 + (total_entries // 3), 30)
        
        # Get last submission
        last_entry = self.db.query(models.ProgressEntry).filter(
            models.ProgressEntry.patient_id == patient_id
        ).order_by(models.ProgressEntry.submitted_at.desc()).first()
        
        last_submission = last_entry.submitted_at if last_entry else None
        
        # Get patient conditions for summary
        conditions = self.get_patient_conditions(patient_id)
        condition_summary = [condition.capitalize() for condition in conditions]
        
        return schemas.DashboardStats(
            compliance_rate=compliance_rate,
            streak_days=streak_days,
            last_submission=last_submission,
            pending_reviews=2,  # Mock data
            condition_summary=condition_summary
        )

    def get_progress_entry(self, entry_id: int, patient_id: int) -> Optional[models.ProgressEntry]:
        """Get specific progress entry"""
        return self.db.query(models.ProgressEntry).filter(
            models.ProgressEntry.id == entry_id,
            models.ProgressEntry.patient_id == patient_id
        ).first()

    def update_progress_entry(self, entry_id: int, patient_id: int, update_data: schemas.ProgressEntryUpdate) -> Optional[models.ProgressEntry]:
        """Update progress entry"""
        entry = self.get_progress_entry(entry_id, patient_id)
        if not entry:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(entry, field, value)
        
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete_progress_entry(self, entry_id: int, patient_id: int) -> bool:
        """Delete progress entry"""
        entry = self.get_progress_entry(entry_id, patient_id)
        if not entry:
            return False
        
        self.db.delete(entry)
        self.db.commit()
        return True