from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from . import models, schemas

logger = logging.getLogger(__name__)

class MedicalRecordService:
    
    @staticmethod
    def get_medical_records(  # ✅ CHANGED: Renamed to plural
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        patient_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[models.MedicalRecord]:
        """Get all medical records with optional filtering"""
        try:
            query = db.query(models.MedicalRecord)
            
            if patient_id:
                query = query.filter(models.MedicalRecord.patient_id == patient_id)
            if category:
                query = query.filter(models.MedicalRecord.category == category)
                
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting medical records: {e}")
            return []
    
    @staticmethod
    def get_medical_record_by_id(db: Session, record_id: str) -> Optional[models.MedicalRecord]:  # ✅ CHANGED: Renamed to avoid conflict
        """Get medical record by ID"""
        try:
            return db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
        except Exception as e:
            logger.error(f"Error getting record by ID {record_id}: {e}")
            return None
    
    @staticmethod
    def create_medical_record(db: Session, record_data: dict) -> models.MedicalRecord:  # ✅ CHANGED: Accept dict instead of schema
        """Create new medical record - accepts dict for flexibility"""
        try:
            # If it's already a schema object, convert to dict
            if hasattr(record_data, 'dict'):
                record_data = record_data.dict()
            
            # Ensure date is set if not provided
            if 'date' not in record_data or not record_data['date']:
                record_data['date'] = datetime.now().strftime("%Y-%m-%d")
            
            db_record = models.MedicalRecord(**record_data)
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            return db_record
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating medical record: {e}")
            raise e
    
    @staticmethod
    def update_medical_record(
        db: Session, 
        record_id: str, 
        record_update: dict  # ✅ CHANGED: Accept dict instead of schema
    ) -> Optional[models.MedicalRecord]:
        """Update medical record - accepts dict for flexibility"""
        try:
            db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
            if not db_record:
                return None
                
            # If it's a schema object, convert to dict
            if hasattr(record_update, 'dict'):
                update_data = record_update.dict(exclude_unset=True)
            else:
                update_data = record_update
                
            for field, value in update_data.items():
                if hasattr(db_record, field):
                    setattr(db_record, field, value)
                    
            db.commit()
            db.refresh(db_record)
            return db_record
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating medical record {record_id}: {e}")
            raise e
    
    @staticmethod
    def delete_medical_record(db: Session, record_id: str) -> bool:
        """Delete medical record"""
        try:
            db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
            if not db_record:
                return False
                
            db.delete(db_record)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting medical record {record_id}: {e}")
            raise e
    
    # Specialized methods - UPDATED to handle dict input
    @staticmethod
    def create_lab_result(db: Session, lab_data: dict) -> models.MedicalRecord:  # ✅ CHANGED: Accept dict
        """Create lab result from dict data"""
        try:
            record_data = {
                "patient_id": lab_data.get('patient_id'),
                "patient_name": lab_data.get('patient_name'),
                "type": lab_data.get('test_type', 'Lab Test'),
                "category": "Lab Results",
                "doctor": lab_data.get('doctor', 'Unknown Doctor'),
                "date": lab_data.get('date') or datetime.now().strftime("%Y-%m-%d"),
                "status": lab_data.get('status', 'Completed'),
                "details": lab_data.get('results', {}),
            }
            
            # Add optional fields
            if 'lab_order_id' in lab_data:
                record_data['lab_order_id'] = lab_data['lab_order_id']
            if 'interpretation' in lab_data:
                if 'details' not in record_data:
                    record_data['details'] = {}
                record_data['details']['interpretation'] = lab_data['interpretation']
                
            return MedicalRecordService.create_medical_record(db, record_data)
        except Exception as e:
            logger.error(f"Error creating lab result: {e}")
            raise e
    
    @staticmethod
    def create_prescription(db: Session, prescription_data: dict) -> models.MedicalRecord:  # ✅ CHANGED: Accept dict
        """Create prescription from dict data"""
        try:
            record_data = {
                "patient_id": prescription_data.get('patient_id'),
                "patient_name": prescription_data.get('patient_name'),
                "type": f"Prescription - {prescription_data.get('medication', 'Unknown Medication')}",
                "category": "Prescriptions",
                "doctor": prescription_data.get('doctor', 'Unknown Doctor'),
                "date": prescription_data.get('date') or datetime.now().strftime("%Y-%m-%d"),
                "status": prescription_data.get('status', 'Active'),
                "details": {
                    "medication": prescription_data.get('medication'),
                    "dosage": prescription_data.get('dosage'),
                    "frequency": prescription_data.get('frequency'),
                    "duration": prescription_data.get('duration'),
                    "instructions": prescription_data.get('instructions', 'Take as directed')
                }
            }
            return MedicalRecordService.create_medical_record(db, record_data)
        except Exception as e:
            logger.error(f"Error creating prescription: {e}")
            raise e
    
    @staticmethod
    def get_records_by_category(db: Session, category: str) -> List[models.MedicalRecord]:
        """Get records by category"""
        try:
            return db.query(models.MedicalRecord).filter(models.MedicalRecord.category == category).all()
        except Exception as e:
            logger.error(f"Error getting records by category {category}: {e}")
            return []
    
    @staticmethod
    def get_patient_records(db: Session, patient_id: str) -> List[models.MedicalRecord]:
        """Get records by patient ID"""
        try:
            return db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id == patient_id).all()
        except Exception as e:
            logger.error(f"Error getting records for patient {patient_id}: {e}")
            return []