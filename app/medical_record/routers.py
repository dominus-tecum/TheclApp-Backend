from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# REQUEST SCHEMAS FOR PROPER API DOCUMENTATION
class MedicalRecordCreateRequest(BaseModel):
    patient_id: str
    patient_name: str
    type: str
    category: str
    doctor: str
    date: str
    status: str
    details: Dict[str, Any]
    lab_order_id: Optional[str] = None
    prescription_id: Optional[str] = None
    appointment_id: Optional[str] = None

class MedicalRecordUpdateRequest(BaseModel):
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class LabResultRequest(BaseModel):
    patient_id: str
    patient_name: str
    test_type: str
    doctor: str
    results: Dict[str, Any]
    interpretation: Optional[str] = None
    lab_order_id: Optional[str] = None
    status: Optional[str] = "Completed"

class PrescriptionRequest(BaseModel):
    patient_id: str
    patient_name: str
    medication: str
    dosage: str
    frequency: str
    duration: str
    doctor: str
    instructions: Optional[str] = None
    status: Optional[str] = "Active"

# Test if imports work
try:
    from app.medical_record import services
    logger.info("✅ Services import successful")
except ImportError as e:
    logger.error(f"❌ Services import failed: {e}")

try:
    from app.medical_record import schemas
    logger.info("✅ Schemas import successful") 
except ImportError as e:
    logger.error(f"❌ Schemas import failed: {e}")

try:
    from app.medical_record import models
    logger.info("✅ Models import successful")
except ImportError as e:
    logger.error(f"❌ Models import failed: {e}")

@router.get("/test-imports")
def test_imports():
    """Test if all imports work"""
    return {
        "services": "services" in dir(),
        "schemas": "schemas" in dir(), 
        "models": "models" in dir()
    }

# EXISTING ENDPOINTS - KEEP THESE
@router.get("/")
def get_medical_records(
    db: Session = Depends(get_db),
    patient_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Get medical records - with filtering support"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        
        # Apply filters if provided
        filtered_records = records
        if patient_id:
            filtered_records = [r for r in filtered_records if getattr(r, 'patient_id', None) == patient_id]
        if category:
            filtered_records = [r for r in filtered_records if getattr(r, 'category', None) == category]
            
        return {
            "message": "Medical records retrieved successfully",
            "records": filtered_records,
            "total_count": len(records),
            "filtered_count": len(filtered_records)
        }
    except Exception as e:
        logger.error(f"Error fetching medical records: {e}")
        return {
            "message": f"Error: {e}",
            "records": []
        }

@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        from app.medical_record import models
        count = db.query(models.MedicalRecord).count()
        return {
            "status": "success",
            "table_exists": True,
            "record_count": count,
            "message": f"Database has {count} medical records"
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }

# NEW ENDPOINTS WITH PROPER REQUEST SCHEMAS

@router.get("/health/status")
def health_status():
    """Health check endpoint for medical records service"""
    return {
        "status": "healthy", 
        "service": "medical-records",
        "message": "Medical records service is running"
    }

@router.get("/{record_id}")
def get_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Get specific medical record by ID"""
    try:
        from app.medical_record import services
        record = services.MedicalRecordService.get_medical_record_by_id(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Medical record not found")
        return {
            "message": "Record retrieved successfully",
            "record": record
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching medical record")

@router.post("/")
def create_medical_record(record_data: MedicalRecordCreateRequest, db: Session = Depends(get_db)):
    """Create new medical record"""
    try:
        from app.medical_record import services
        record = services.MedicalRecordService.create_medical_record(db, record_data.dict())
        return {
            "message": "Medical record created successfully",
            "record": record
        }
    except Exception as e:
        logger.error(f"Error creating record: {e}")
        raise HTTPException(status_code=500, detail="Error creating medical record")

@router.put("/{record_id}")
def update_medical_record(record_id: str, record_data: MedicalRecordUpdateRequest, db: Session = Depends(get_db)):
    """Update medical record"""
    try:
        from app.medical_record import services
        record = services.MedicalRecordService.update_medical_record(db, record_id, record_data.dict())
        return {
            "message": "Medical record updated successfully",
            "record": record
        }
    except Exception as e:
        logger.error(f"Error updating record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating medical record")

@router.delete("/{record_id}")
def delete_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Delete medical record"""
    try:
        from app.medical_record import services
        result = services.MedicalRecordService.delete_medical_record(db, record_id)
        return {
            "message": "Medical record deleted successfully",
            "deleted_id": record_id
        }
    except Exception as e:
        logger.error(f"Error deleting record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting medical record")

# Lab Results specific endpoints - FIXED VERSION

@router.post("/lab-results")
def create_lab_result(lab_data: LabResultRequest, db: Session = Depends(get_db)):
    """Create lab result"""
    try:
        from app.medical_record import services
        lab_data_dict = lab_data.dict()
        
        # ✅ FIXED: Store all lab-specific fields in details
        lab_data_dict['category'] = 'Lab Results'
        lab_data_dict['type'] = lab_data.test_type  # Use for the main type field
        
        # Create proper details structure with ALL lab-specific data
        lab_data_dict['details'] = {
            "test_type": lab_data.test_type,        # ✅ Preserve original test_type
            "results": lab_data.results,            # ✅ Store results in details
            "interpretation": lab_data.interpretation  # ✅ Store interpretation in details
        }
        
        # ✅ FIXED: Remove ALL lab-specific fields to avoid model errors
        fields_to_remove = ['test_type', 'results', 'interpretation']
        for field in fields_to_remove:
            if field in lab_data_dict:
                del lab_data_dict[field]
            
        # Set date if not provided
        if 'date' not in lab_data_dict or not lab_data_dict['date']:
            lab_data_dict['date'] = datetime.now().strftime("%Y-%m-%d")
            
        record = services.MedicalRecordService.create_medical_record(db, lab_data_dict)
        return {
            "message": "Lab result created successfully",
            "result": record
        }
    except Exception as e:
        logger.error(f"Error creating lab result: {e}")
        raise HTTPException(status_code=500, detail="Error creating lab result")

@router.get("/lab-results")
def get_lab_results(db: Session = Depends(get_db)):
    """Get all lab results"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        lab_results = [r for r in records if getattr(r, 'category', None) == 'Lab Results']
        return {
            "message": "Lab results retrieved successfully",
            "results": lab_results,
            "count": len(lab_results)
        }
    except Exception as e:
        logger.error(f"Error fetching lab results: {e}")
        raise HTTPException(status_code=500, detail="Error fetching lab results")

# Prescriptions specific endpoints

@router.post("/prescriptions")
def create_prescription(prescription_data: PrescriptionRequest, db: Session = Depends(get_db)):
    """Create prescription"""
    try:
        from app.medical_record import services
        prescription_dict = prescription_data.dict()
        
        print(f"📋 Raw prescription data: {prescription_dict}")
        
        # ✅ FIXED: Map prescription fields to MedicalRecord model
        prescription_dict['category'] = 'Prescriptions'
        prescription_dict['type'] = f"Prescription - {prescription_data.medication}"
        prescription_dict['status'] = prescription_data.status or 'Active'
        
        # Create proper details structure with ALL prescription data
        prescription_dict['details'] = {
            "medication": prescription_data.medication,
            "dosage": prescription_data.dosage,
            "frequency": prescription_data.frequency,
            "duration": prescription_data.duration,
            "instructions": prescription_data.instructions or "Take as directed"
        }
        
        # ✅ FIXED: Remove ALL prescription-specific fields to avoid model errors
        fields_to_remove = ['medication', 'dosage', 'frequency', 'duration', 'instructions']
        for field in fields_to_remove:
            if field in prescription_dict:
                print(f"🗑️ Removing field: {field}")
                del prescription_dict[field]
            
        # Set date if not provided
        if 'date' not in prescription_dict or not prescription_dict['date']:
            prescription_dict['date'] = datetime.now().strftime("%Y-%m-%d")
            
        print(f"✅ Final data for MedicalRecord: {prescription_dict}")
        print(f"✅ Details content: {prescription_dict['details']}")
            
        record = services.MedicalRecordService.create_medical_record(db, prescription_dict)
        return {
            "message": "Prescription created successfully",
            "prescription": record
        }
    except Exception as e:
        logger.error(f"Error creating prescription: {e}")
        print(f"❌ Detailed error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating prescription")

@router.get("/prescriptions")
def get_prescriptions(db: Session = Depends(get_db)):
    """Get all prescriptions"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        prescriptions = [r for r in records if getattr(r, 'category', None) == 'Prescriptions']
        return {
            "message": "Prescriptions retrieved successfully",
            "prescriptions": prescriptions,
            "count": len(prescriptions)
        }
    except Exception as e:
        logger.error(f"Error fetching prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching prescriptions")

# Patient-specific records
@router.get("/patient/{patient_id}/records")
def get_patient_records(patient_id: str, db: Session = Depends(get_db)):
    """Get all records for a specific patient"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        patient_records = [r for r in records if getattr(r, 'patient_id', None) == patient_id]
        return {
            "message": f"Records retrieved for patient {patient_id}",
            "patient_id": patient_id,
            "records": patient_records,
            "count": len(patient_records)
        }
    except Exception as e:
        logger.error(f"Error fetching patient records: {e}")
        raise HTTPException(status_code=500, detail="Error fetching patient records")

# Category-specific records
@router.get("/category/{category}/records")
def get_records_by_category(category: str, db: Session = Depends(get_db)):
    """Get all records for a specific category"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        category_records = [r for r in records if getattr(r, 'category', '').lower() == category.lower()]
        return {
            "message": f"Records retrieved for category {category}",
            "category": category,
            "records": category_records,
            "count": len(category_records)
        }
    except Exception as e:
        logger.error(f"Error fetching category records: {e}")
        raise HTTPException(status_code=500, detail="Error fetching category records")