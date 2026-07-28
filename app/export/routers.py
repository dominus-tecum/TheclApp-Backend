# d:/TheclApp/BACKEND/app/export/routers.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
import json
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from sqlalchemy import text
from app.database import get_db
from app.models import User
from app.authentication.auth import get_current_user
from app.utils.audit import log_audit

router = APIRouter(prefix="/api/export", tags=["export"])

# ========== JSON EXPORT ENDPOINT ==========
@router.get("/patient-data")
async def export_patient_data(
    request: Request,
    current_user: dict = Depends(get_current_user),  # ← CHANGE to dict
    db: Session = Depends(get_db)
):
    """Export all patient data in JSON format (UAE PDPL Right to Access)"""
    
    patient_id = current_user.id
    
    # Get user data from database to get full object
    user_obj = db.query(User).filter(User.id == patient_id).first()
    
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user data
    user_data = {
        "id": patient_id,
        "username": user_obj.username,
        "email": user_obj.email,
        "name": user_obj.name,
        "phone_number": user_obj.phone_number,
        "role": user_obj.role.value if hasattr(user_obj.role, 'value') else str(user_obj.role),
        "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None,
        
    }
    
        # Get patient profile
    from app.models import PatientProfile
    patient = db.query(PatientProfile).filter(
        PatientProfile.user_id == patient_id,
        PatientProfile.deleted_at.is_(None)
    ).first()
    
    patient_data = {}
    if patient:
        patient_data = {
            "id": patient.id,
            "name": patient.name,
            "birth_date": patient.birth_date,
            "phone_number": patient.phone_number,
            "high_risk": patient.high_risk,
            "created_at": patient.created_at.isoformat() if patient.created_at else None
        }
    
    # Get fertility entries
    from app.fertility.models import FertilityEntry
    fertility_entries = db.query(FertilityEntry).filter(
        FertilityEntry.patient_id == str(patient_id),
        FertilityEntry.deleted_at.is_(None)
    ).all()
    
    fertility_data = []
    for entry in fertility_entries:
        fertility_data.append({
            "id": entry.id,
            "cycle_day": entry.cycle_day,
            "submission_date": entry.submission_date,
            "bbt_temperature": entry.bbt_temperature,
            "cervical_fluid_type": entry.cervical_fluid_type,
            "lh_test_result": entry.lh_test_result,
            "fertility_status": entry.fertility_status,
            "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None
        })
    
    # Get prenatal entries
    from app.prenatal.models import PrenatalEntry
    prenatal_entries = db.query(PrenatalEntry).filter(
        PrenatalEntry.patient_id == str(patient_id),
        PrenatalEntry.deleted_at.is_(None)
    ).all()
    
    prenatal_data = []
    for entry in prenatal_entries:
        prenatal_data.append({
            "id": entry.id,
            "submission_date": entry.submission_date,
            "gestational_age": entry.gestational_age,
            "blood_pressure_systolic": entry.blood_pressure_systolic,
            "blood_pressure_diastolic": entry.blood_pressure_diastolic,
            "fetal_movement": entry.fetal_movement,
            "status": entry.status,
            "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None
        })
    
    # Get women's health entries
    from app.health_progress.womens_reproductive.models import WomensHealthEntry
    womens_health_entries = db.query(WomensHealthEntry).filter(
        WomensHealthEntry.patient_id == str(patient_id),
        WomensHealthEntry.deleted_at.is_(None)
    ).all()
    
    womens_health_data = []
    for entry in womens_health_entries:
        womens_health_data.append({
            "id": entry.id,
            "submission_date": entry.submission_date,
            "main_concerns": entry.main_concerns,
            "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None
        })
    
    # Get men's health entries
    from app.health_progress.mens_sexual_health.models import MensHealthEntry
    mens_health_entries = db.query(MensHealthEntry).filter(
        MensHealthEntry.patient_id == str(patient_id),
        MensHealthEntry.deleted_at.is_(None)
    ).all()
    
    mens_health_data = []
    for entry in mens_health_entries:
        mens_health_data.append({
            "id": entry.id,
            "submission_date": entry.submission_date,
            "main_concerns": entry.main_concerns,
            "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None
        })
    
    # Get lifelong entries
    from app.health_progress.lifelong.models import LifelongEntry
    lifelong_entries = db.query(LifelongEntry).filter(
        LifelongEntry.patient_id == patient_id,
        LifelongEntry.deleted_at.is_(None)
    ).all()
    
    lifelong_data = []
    for entry in lifelong_entries:
        lifelong_data.append({
            "id": entry.id,
            "submission_date": entry.submission_date,
            "common_data": entry.common_data,
            "conditions_data": entry.conditions_data,
            "status": entry.status,
            "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None
        })
    
    # Get audit logs (for transparency)
    from app.models import AuditLog
    audit_logs = db.query(AuditLog).filter(
        AuditLog.user_id == patient_id
    ).order_by(AuditLog.created_at.desc()).limit(100).all()
    
    audit_data = []
    for log in audit_logs:
        audit_data.append({
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
    
    # Compile all data
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "patient": {
            "user": user_data,
            "profile": patient_data
        },
        "health_data": {
            "fertility": fertility_data,
            "prenatal": prenatal_data,
            "womens_health": womens_health_data,
            "mens_health": mens_health_data,
            "lifelong_entries": lifelong_data
        },
        "audit_trail": audit_data
    }
    
    # Log the export action for compliance
    log_audit(
        db=db,
        user_id=patient_id,
        action="EXPORT",
        resource_type="patient_data",
        resource_id=str(patient_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        
    )
    
    return export_data


# ========== CSV EXPORT ENDPOINT ==========
@router.get("/patient-data/csv")
async def export_patient_data_csv(
    request: Request,
    current_user: dict = Depends(get_current_user),  # ← CHANGE to dict
    db: Session = Depends(get_db)
):
    """Export all patient data in CSV format"""
    
    # Get the JSON data first
    json_data = await export_patient_data(request, current_user, db)
    
    # Convert to CSV
    output = StringIO()
    
    # Flatten the data for CSV
    csv_data = []
    
    # Add fertility entries
    for entry in json_data.get("health_data", {}).get("fertility", []):
        row = {
            "type": "fertility",
            "submission_date": entry.get("submission_date"),
            "bbt_temperature": entry.get("bbt_temperature"),
            "cervical_fluid_type": entry.get("cervical_fluid_type"),
            "lh_test_result": entry.get("lh_test_result"),
            "fertility_status": entry.get("fertility_status")
        }
        csv_data.append(row)
    
    # Add prenatal entries
    for entry in json_data.get("health_data", {}).get("prenatal", []):
        row = {
            "type": "prenatal",
            "submission_date": entry.get("submission_date"),
            "gestational_age": entry.get("gestational_age"),
            "blood_pressure_systolic": entry.get("blood_pressure_systolic"),
            "blood_pressure_diastolic": entry.get("blood_pressure_diastolic"),
            "fetal_movement": entry.get("fetal_movement"),
            "status": entry.get("status")
        }
        csv_data.append(row)
    
    # Write CSV
    if csv_data:
        fieldnames = csv_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    patient_id = current_user.id
    
    # Log audit
    log_audit(
        db=db,
        user_id=patient_id,
        action="EXPORT_CSV",
        resource_type="patient_data",
        resource_id=str(patient_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        
    )
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=patient_data_{datetime.utcnow().date()}.csv"}
    )


# ========== DATA DELETION ENDPOINT (Right to be Forgotten) ==========
@router.delete("/patient-data")
async def delete_patient_data(
    request: Request,
    current_user: dict = Depends(get_current_user),  # ← CHANGE to dict
    db: Session = Depends(get_db)
):
    """
    Soft delete all patient data (UAE PDPL Right to be Forgotten)
    Data remains in database for legal/medical retention but is not accessible
    """
    patient_id = current_user.id
    deleted_at = datetime.utcnow()
    
    # List of all tables to soft delete
    tables_to_delete = [
        # User tables
        ("users", "id", patient_id),
        
        # Patient tables
        ("patients", "user_id", patient_id),
        
        # Fertility tables
        ("fertility_entries", "patient_id", str(patient_id)),
        ("fertility_profiles", "patient_id", str(patient_id)),
        ("fertility_insights", "patient_id", str(patient_id)),
        
        # Prenatal tables
        ("prenatal_entries", "patient_id", str(patient_id)),
        
        # Postnatal tables
        ("postnatal_entries", "patient_id", str(patient_id)),
        ("postnatal_profiles", "patient_id", str(patient_id)),
        
        # Women's Health
        ("womens_health_entries", "patient_id", str(patient_id)),
        ("womens_health_intake", "patient_id", str(patient_id)),
        ("womens_health_photos", "patient_id", str(patient_id)),
        
        # Men's Health
        ("mens_health_entries", "patient_id", str(patient_id)),
        ("mens_health_intake", "patient_id", str(patient_id)),
        ("mens_health_photos", "patient_id", str(patient_id)),
        ("mens_health_calibration", "patient_id", str(patient_id)),
        
        # Lifelong entries
        ("lifelong_entries", "patient_id", patient_id),
        
        # Surgery entries
        ("abdominal_entries", "patient_id", patient_id),
        ("bariatric_entries", "patient_id", patient_id),
        ("burn_care_entries", "patient_id", patient_id),
        ("cardiac_surgery_entries", "patient_id", patient_id),
        ("cesarean_section_entries", "patient_id", patient_id),
        ("general_entries", "patient_id", patient_id),
        ("gynecologic_surgery_entries", "patient_id", patient_id),
        ("orthopedic_surgery_entries", "patient_id", patient_id),
        ("urological_surgery_entries", "patient_id", patient_id),
        
        # Chronic condition entries
        ("cancer_entries", "patient_id", patient_id),
        ("diabetes_entries", "patient_id", patient_id),
        ("heart_entries", "patient_id", patient_id),
        ("hypertension_entries", "patient_id", patient_id),
        ("kidney_entries", "patient_id", patient_id),
        
        # Medical records
        ("medical_records", "patient_id", patient_id),
        ("medical_record", "patient_id", patient_id),
        
        # Patient relationships
        ("patient_consents", "user_id", patient_id),  # ← FIXED: patient_consents uses user_id
        ("patient_doctor_assignments", "patient_id", patient_id),
        ("patient_profiles", "user_id", patient_id),  # ← FIXED: patient_profiles uses user_id
        
        # Prescriptions
        ("prescriptions", "user_id", patient_id),  # ← FIXED: prescriptions uses user_id
        
        # Appointments
        ("appointments", "user_id", patient_id),  # ← FIXED: appointments uses user_id
        
        # Cycle analyses
        ("cycle_analyses", "patient_id", str(patient_id)),
    ]
    
    deleted_counts = {}
    
    for table_name, id_column, id_value in tables_to_delete:
        try:
            # Use raw SQL for dynamic table names
            query = text(f"UPDATE {table_name} SET deleted_at = :deleted_at WHERE {id_column} = :id_value AND deleted_at IS NULL")
            result = db.execute(query, {"deleted_at": deleted_at, "id_value": id_value})
            deleted_counts[table_name] = result.rowcount
        except Exception as e:
            print(f"Error deleting from {table_name}: {e}")
            deleted_counts[table_name] = 0
    
    db.commit()
    
    # Log the deletion for compliance
    log_audit(
        db=db,
        user_id=patient_id,
        action="DELETE_REQUEST",
        resource_type="patient_data",
        resource_id=str(patient_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        
    )
    
    return {
        "message": "Your data has been soft deleted. You will no longer have access to the platform.",
        "records_affected": deleted_counts,
        "total_records": sum(deleted_counts.values()),
        "note": "Data remains stored for legal/medical retention requirements as per UAE Health Data Law.",
        "contact_admin": "To reactivate your account, please contact clinic administrator."
    }    

# ========== ACCOUNT REACTIVATION (Admin only) ==========
@router.post("/reactivate/{user_id}")
async def reactivate_account(
    user_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),  # ← CHANGE to dict
    db: Session = Depends(get_db)
):
    """
    Reactivate a soft-deleted account (Admin only)
    """
    # Check if current user is admin
    user_role = current_user.role.value
    if user_role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # List of all tables to reactivate
    tables_to_reactivate = [
        ("users", "id", user_id),
        ("patients", "user_id", user_id),
        ("fertility_entries", "patient_id", str(user_id)),
        ("prenatal_entries", "patient_id", str(user_id)),
        ("womens_health_entries", "patient_id", str(user_id)),
        ("mens_health_entries", "patient_id", str(user_id)),
        ("lifelong_entries", "patient_id", user_id),
    ]
    
    reactivated_counts = {}
    
    for table_name, id_column, id_value in tables_to_reactivate:
        try:
            query = text(f"UPDATE {table_name} SET deleted_at = NULL WHERE {id_column} = :id_value AND deleted_at IS NOT NULL")
            result = db.execute(query, {"id_value": id_value})
            reactivated_counts[table_name] = result.rowcount
        except Exception as e:
            print(f"Error reactivating {table_name}: {e}")
            reactivated_counts[table_name] = 0
    
    db.commit()
    
    # Log the reactivation
    log_audit(
        db=db,
        user_id=current_user.id,
        action="REACTIVATE",
        resource_type="patient_data",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        
    )
    
    return {
        "message": f"Account for user {user_id} has been reactivated",
        "records_affected": reactivated_counts
    }