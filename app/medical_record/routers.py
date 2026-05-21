from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.utils.audit import log_audit
from app.dependencies import get_current_user
from app.models import User
from app.organization.dependencies import get_current_organization
from app.models import Organization

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

# EXISTING ENDPOINTS - WITH AUDIT LOGGING
@router.get("/")
def get_medical_records(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # ← CHANGED: User to dict
    org: Organization = Depends(get_current_organization),
    patient_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Get medical records - with filtering support"""
    try:
        from app.medical_record import services
        
        # ← ADDED: Super admin check
        if current_user.get('is_super_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # ← ADDED: Doctor filter
        if current_user.get('role') == 'doctor':
            from app.models import PatientDoctorAssignment
            assignments = db.query(PatientDoctorAssignment.patient_id).filter(
                PatientDoctorAssignment.doctor_id == current_user.get('id'),
                PatientDoctorAssignment.end_date == None
            ).all()
            assigned_patient_ids = [a[0] for a in assignments]
            
            if not assigned_patient_ids:
                return {
                    "message": "Medical records retrieved successfully",
                    "records": [],
                    "total_count": 0,
                    "filtered_count": 0
                }
            
            # Get records only for assigned patients
            records = db.query(MedicalRecord).filter(
                MedicalRecord.organization_id == org.id,
                MedicalRecord.patient_id.in_(assigned_patient_ids)
            ).all()
        else:
            records = services.MedicalRecordService.get_medical_records(db, org.id)
        
        # Apply filters if provided
        filtered_records = records
        if patient_id:
            filtered_records = [r for r in filtered_records if getattr(r, 'patient_id', None) == patient_id]
        if category:
            filtered_records = [r for r in filtered_records if getattr(r, 'category', None) == category]
        
        # ✅ CONVERT SQLAlchemy objects to dictionaries
        records_list = []
        for record in filtered_records:
            records_list.append({
                "id": record.id,
                "patient_id": record.patient_id,
                "patient_name": record.patient_name,
                "type": record.type,
                "category": record.category,
                "doctor": record.doctor,
                "date": record.date,
                "status": record.status,
                "details": record.details,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "updated_at": record.updated_at.isoformat() if record.updated_at else None
            })
        
        # ✅ AUDIT LOG (YOUR EXISTING CODE - with .get() changes)
        log_audit(
            db=db,
            user_id=current_user.get('id'),  # ← CHANGED
            username=current_user.get('username'),  # ← CHANGED
            user_role=current_user.get('role'),  # ← CHANGED
            action='READ',
            resource_type='MEDICAL_RECORDS',
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": "Medical records retrieved successfully",
            "records": records_list,
            "total_count": len(records),
            "filtered_count": len(records_list)
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

@router.get("/health/status")
def health_status():
    """Health check endpoint for medical records service"""
    return {
        "status": "healthy", 
        "service": "medical-records",
        "message": "Medical records service is running"
    }

@router.get("/{record_id}")
def get_medical_record(
    record_id: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Get specific medical record by ID"""
    try:
        from app.medical_record import services
        record = services.MedicalRecordService.get_medical_record_by_id(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Medical record not found")
        
        # ✅ CONVERT SQLAlchemy object to dictionary
        record_dict = {
            "id": record.id,
            "patient_id": record.patient_id,
            "patient_name": record.patient_name,
            "type": record.type,
            "category": record.category,
            "doctor": record.doctor,
            "date": record.date,
            "status": record.status,
            "details": record.details,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        }
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='MEDICAL_RECORD',
            resource_id=int(record_id) if record_id.isdigit() else None,
            patient_id=int(record.patient_id) if hasattr(record, 'patient_id') and record.patient_id else None,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": "Record retrieved successfully",
            "record": record_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching medical record")

@router.post("/")
def create_medical_record(
    record_data: MedicalRecordCreateRequest, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Create new medical record"""
    try:
        from app.medical_record import services
        record = services.MedicalRecordService.create_medical_record(db, record_data.dict(), org.id)
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='MEDICAL_RECORD',
            patient_id=int(record_data.patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=record_data.dict()
        )
        
        return {
            "message": "Medical record created successfully",
            "record": record
        }
    except Exception as e:
        logger.error(f"Error creating record: {e}")
        raise HTTPException(status_code=500, detail="Error creating medical record")

@router.put("/{record_id}")
def update_medical_record(
    record_id: str, 
    record_data: MedicalRecordUpdateRequest, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Update medical record"""
    try:
        from app.medical_record import services
        # Get old record for audit
        old_record = services.MedicalRecordService.get_medical_record_by_id(db, record_id)
        
        record = services.MedicalRecordService.update_medical_record(db, record_id, record_data.dict())
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='UPDATE',
            resource_type='MEDICAL_RECORD',
            resource_id=int(record_id) if record_id.isdigit() else None,
            patient_id=int(old_record.patient_id) if old_record and hasattr(old_record, 'patient_id') else None,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            old_value=old_record.dict() if old_record else None,
            new_value=record_data.dict()
        )
        
        return {
            "message": "Medical record updated successfully",
            "record": record
        }
    except Exception as e:
        logger.error(f"Error updating record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating medical record")

@router.delete("/{record_id}")
def delete_medical_record(
    record_id: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Delete medical record"""
    try:
        from app.medical_record import services
        # Get record for audit before deletion
        old_record = services.MedicalRecordService.get_medical_record_by_id(db, record_id)
        
        result = services.MedicalRecordService.delete_medical_record(db, record_id)
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='DELETE',
            resource_type='MEDICAL_RECORD',
            resource_id=int(record_id) if record_id.isdigit() else None,
            patient_id=int(old_record.patient_id) if old_record and hasattr(old_record, 'patient_id') else None,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            old_value=old_record.dict() if old_record else None
        )
        
        return {
            "message": "Medical record deleted successfully",
            "deleted_id": record_id
        }
    except Exception as e:
        logger.error(f"Error deleting record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting medical record")

@router.post("/lab-results")
def create_lab_result(
    lab_data: LabResultRequest, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Create lab result"""
    try:
        from app.medical_record import services
        lab_data_dict = lab_data.dict()
        
        lab_data_dict['category'] = 'Lab Results'
        lab_data_dict['type'] = lab_data.test_type
        
        lab_data_dict['details'] = {
            "test_type": lab_data.test_type,
            "results": lab_data.results,
            "interpretation": lab_data.interpretation
        }
        
        fields_to_remove = ['test_type', 'results', 'interpretation']
        for field in fields_to_remove:
            if field in lab_data_dict:
                del lab_data_dict[field]
            
        if 'date' not in lab_data_dict or not lab_data_dict['date']:
            lab_data_dict['date'] = datetime.now().strftime("%Y-%m-%d")
            
        record = services.MedicalRecordService.create_medical_record(db, lab_data_dict)
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='LAB_RESULT',
            patient_id=int(lab_data.patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=lab_data_dict
        )
        
        return {
            "message": "Lab result created successfully",
            "result": record
        }
    except Exception as e:
        logger.error(f"Error creating lab result: {e}")
        raise HTTPException(status_code=500, detail="Error creating lab result")

@router.get("/lab-results")
def get_lab_results(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Get all lab results"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        lab_results = [r for r in records if getattr(r, 'category', None) == 'Lab Results']
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='LAB_RESULTS',
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": "Lab results retrieved successfully",
            "results": lab_results,
            "count": len(lab_results)
        }
    except Exception as e:
        logger.error(f"Error fetching lab results: {e}")
        raise HTTPException(status_code=500, detail="Error fetching lab results")

@router.post("/prescriptions")
def create_prescription(
    prescription_data: PrescriptionRequest, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Create prescription"""
    try:
        from app.medical_record import services
        prescription_dict = prescription_data.dict()
        
        print(f"📋 Raw prescription data: {prescription_dict}")
        
        prescription_dict['category'] = 'Prescriptions'
        prescription_dict['type'] = f"Prescription - {prescription_data.medication}"
        prescription_dict['status'] = prescription_data.status or 'Active'
        
        prescription_dict['details'] = {
            "medication": prescription_data.medication,
            "dosage": prescription_data.dosage,
            "frequency": prescription_data.frequency,
            "duration": prescription_data.duration,
            "instructions": prescription_data.instructions or "Take as directed"
        }
        
        fields_to_remove = ['medication', 'dosage', 'frequency', 'duration', 'instructions']
        for field in fields_to_remove:
            if field in prescription_dict:
                print(f"🗑️ Removing field: {field}")
                del prescription_dict[field]
            
        if 'date' not in prescription_dict or not prescription_dict['date']:
            prescription_dict['date'] = datetime.now().strftime("%Y-%m-%d")
            
        print(f"✅ Final data for MedicalRecord: {prescription_dict}")
        print(f"✅ Details content: {prescription_dict['details']}")
            
        record = services.MedicalRecordService.create_medical_record(db, prescription_dict)
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='CREATE',
            resource_type='PRESCRIPTION',
            patient_id=int(prescription_data.patient_id),
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            new_value=prescription_dict
        )
        
        return {
            "message": "Prescription created successfully",
            "prescription": record
        }
    except Exception as e:
        logger.error(f"Error creating prescription: {e}")
        print(f"❌ Detailed error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating prescription")

@router.get("/prescriptions")
def get_prescriptions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Get all prescriptions"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        prescriptions = [r for r in records if getattr(r, 'category', None) == 'Prescriptions']
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='PRESCRIPTIONS',
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": "Prescriptions retrieved successfully",
            "prescriptions": prescriptions,
            "count": len(prescriptions)
        }
    except Exception as e:
        logger.error(f"Error fetching prescriptions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching prescriptions")

@router.get("/patient/{patient_id}/records")
def get_patient_records(
    patient_id: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Get all records for a specific patient"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        patient_records = [r for r in records if getattr(r, 'patient_id', None) == patient_id]
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='PATIENT_RECORDS',
            patient_id=int(patient_id) if patient_id.isdigit() else None,
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": f"Records retrieved for patient {patient_id}",
            "patient_id": patient_id,
            "records": patient_records,
            "count": len(patient_records)
        }
    except Exception as e:
        logger.error(f"Error fetching patient records: {e}")
        raise HTTPException(status_code=500, detail="Error fetching patient records")

@router.get("/category/{category}/records")
def get_records_by_category(
    category: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """Get all records for a specific category"""
    try:
        from app.medical_record import services
        records = services.MedicalRecordService.get_medical_records(db)
        category_records = [r for r in records if getattr(r, 'category', '').lower() == category.lower()]
        
        # ✅ AUDIT LOG
        log_audit(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            action='READ',
            resource_type='CATEGORY_RECORDS',
            status='success',
            purpose='TREATMENT',
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )
        
        return {
            "message": f"Records retrieved for category {category}",
            "category": category,
            "records": category_records,
            "count": len(category_records)
        }
    except Exception as e:
        logger.error(f"Error fetching category records: {e}")
        raise HTTPException(status_code=500, detail="Error fetching category records")

