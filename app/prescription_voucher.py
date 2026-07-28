# app/prescription_voucher.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from app.database import get_db
from app.authentication.auth import get_current_user
from app.models import User, Organization, UserRole
from app.utils.audit import log_audit

router = APIRouter(prefix="/api/prescription", tags=["Prescription Voucher"])


# ========== USER ENDPOINTS ==========

@router.post("/share")
async def share_prescription_to_pharmacy(
    request: Request,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    print("=" * 50)
    print(f"🔍 SHARE REQUEST RECEIVED")
    print(f"🔍 Data: {data}")
    print(f"🔍 Current user: {current_user.id}")
    print("=" * 50)


    """
    User shares a prescription with a specific pharmacy.
    Prescription remains ACTIVE until pharmacy marks as sold.
    """
    from app.models import PrescriptionVoucher, PrescriptionShare
    
    # Get the prescription
    prescription = db.query(PrescriptionVoucher).filter(
        PrescriptionVoucher.id == data.get('prescription_id'),
        PrescriptionVoucher.patient_id == current_user.id,
        PrescriptionVoucher.status.in_(['active', 'shared'])
    ).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found or already sold")
    
    # Check if prescription is expired
    if prescription.expires_at and prescription.expires_at < datetime.now():
        prescription.status = 'expired'
        db.commit()
        raise HTTPException(status_code=400, detail="Prescription has expired")
    
    # Check if already shared with this pharmacy
    existing_share = db.query(PrescriptionShare).filter(
        PrescriptionShare.prescription_id == prescription.id,
        PrescriptionShare.pharmacy_id == data.get('pharmacy_id')
    ).first()
    
    if existing_share:
        raise HTTPException(status_code=400, detail="Prescription already shared with this pharmacy")
    
    # Generate unique share token
    share_token = secrets.token_urlsafe(32)
    
    # Create share record
    new_share = PrescriptionShare(
        prescription_id=prescription.id,
        pharmacy_id=data.get('pharmacy_id'),
        share_token=share_token,
        shared_at=datetime.now()
    )
    db.add(new_share)
    
    # Update prescription status to 'shared'
    if prescription.status == 'active':
        prescription.status = 'shared'
    
    db.commit()
    
    # Get pharmacy name for response
    pharmacy = db.query(Organization).filter(Organization.id == data.get('pharmacy_id')).first()
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user, 'role') else None,
        action='SHARE',
        resource_type='PRESCRIPTION',
        resource_id=prescription.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"pharmacy_id": data.get('pharmacy_id'), "medication": prescription.medication_name}
    )
    
    return {
        "success": True,
        "message": f"Prescription shared with {pharmacy.name if pharmacy else 'pharmacy'}",
        "share_token": share_token,
        "prescription_status": "active"
    }


@router.get("/my-prescriptions")
async def get_my_prescriptions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User gets all their prescriptions with status.
    Shows which prescriptions are still active and which are sold.
    """
    from app.models import PrescriptionVoucher, PrescriptionShare
    
    prescriptions = db.query(PrescriptionVoucher).filter(
        PrescriptionVoucher.patient_id == current_user.id
    ).order_by(PrescriptionVoucher.created_at.desc()).all()
    
    result = []
    for p in prescriptions:
        # Check if any shares were sold
        sold_share = db.query(PrescriptionShare).filter(
            PrescriptionShare.prescription_id == p.id,
            PrescriptionShare.sold == True
        ).first()
        
        result.append({
            "id": p.id,
            "prescription_code": p.prescription_code,
            "medication_name": p.medication_name,
            "strength": p.strength,
            "dosage": p.dosage,
            "quantity": p.quantity,
            "status": "sold" if sold_share else p.status,
            "created_at": p.created_at,
            "expires_at": p.expires_at
        })
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value if hasattr(current_user, 'role') else None,
        action='READ',
        resource_type='PRESCRIPTION',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return result


# ========== PHARMACY ENDPOINTS ==========

@router.get("/pharmacy/shared-prescriptions")
async def get_shared_prescriptions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pharmacy gets all prescriptions shared with them.
    NO patient information is returned.
    """
    from app.models import PrescriptionVoucher, PrescriptionShare
    
    # Enum comparison - CORRECT
    if current_user.role != UserRole.PHARMACY:
        raise HTTPException(status_code=403, detail="Pharmacy access only")
    
    pharmacy_id = current_user.pharmacy_id or current_user.organization_id
    
    shares = db.query(PrescriptionShare).filter(
        PrescriptionShare.pharmacy_id == pharmacy_id,
        PrescriptionShare.sold == False
    ).order_by(PrescriptionShare.shared_at.desc()).all()
    
    result = []
    for share in shares:
        prescription = db.query(PrescriptionVoucher).filter(PrescriptionVoucher.id == share.prescription_id).first()
        if prescription and prescription.status != 'sold':
            result.append({
                "share_id": share.id,
                "share_token": share.share_token,
                "prescription_id": prescription.id,
                "medication_name": prescription.medication_name,
                "strength": prescription.strength or '—',
                "dosage": prescription.dosage or '—',
                "quantity": prescription.quantity,
                "shared_at": share.shared_at,
                "viewed": share.viewed,
                "sold": share.sold
            })
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='VIEW_SHARED_PRESCRIPTIONS',
        resource_type='PRESCRIPTION',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return result


@router.get("/pharmacy/view-prescription/{share_token}")
async def view_prescription_details(
    share_token: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pharmacy views prescription details.
    ONLY medication info - NO patient name, email, or phone.
    """
    from app.models import PrescriptionVoucher, PrescriptionShare
    
    # Enum comparison - CORRECT
    if current_user.role != UserRole.PHARMACY:
        raise HTTPException(status_code=403, detail="Pharmacy access only")
    
    pharmacy_id = current_user.pharmacy_id or current_user.organization_id
    
    share = db.query(PrescriptionShare).filter(
        PrescriptionShare.share_token == share_token,
        PrescriptionShare.pharmacy_id == pharmacy_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription = db.query(PrescriptionVoucher).filter(PrescriptionVoucher.id == share.prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if share.sold:
        raise HTTPException(status_code=400, detail="Prescription already sold")
    
    # Mark as viewed
    if not share.viewed:
        share.viewed = True
        share.viewed_at = datetime.now()
        db.commit()
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='VIEW',
        resource_type='PRESCRIPTION',
        resource_id=prescription.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    # Return ONLY medication details - NO patient info
    return {
        "prescription_id": prescription.id,
        "medication_name": prescription.medication_name,
        "strength": prescription.strength or '—',
        "dosage": prescription.dosage or '—',
        "quantity": prescription.quantity,
        "shared_at": share.shared_at,
        "viewed_at": share.viewed_at,
        "status": "active"
    }


@router.post("/pharmacy/mark-sold")
async def mark_prescription_sold(
    request: Request,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pharmacy marks a prescription as SOLD.
    This DEACTIVATES the prescription permanently.
    User cannot use this prescription again.
    """
    from app.models import PrescriptionVoucher, PrescriptionShare, UserRole
    from app.medical_record.models import MedicalRecord
    
    # Enum comparison - CORRECT
    if current_user.role != UserRole.PHARMACY:
        raise HTTPException(status_code=403, detail="Pharmacy access only")
    
    pharmacy_id = current_user.pharmacy_id or current_user.organization_id
    
    share = db.query(PrescriptionShare).filter(
        PrescriptionShare.share_token == data.get('share_token'),
        PrescriptionShare.pharmacy_id == pharmacy_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share record not found")
    
    if share.sold:
        raise HTTPException(status_code=400, detail="Prescription already marked as sold")
    
    prescription = db.query(PrescriptionVoucher).filter(PrescriptionVoucher.id == share.prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Mark as sold - THIS DEACTIVATES THE PRESCRIPTION
    share.sold = True
    share.sold_at = datetime.now()
    prescription.status = 'sold'
    
    # ========== UPDATE MEDICAL RECORD STATUS ==========
    if prescription.medical_record_id:
        medical_record = db.query(MedicalRecord).filter(
            MedicalRecord.id == prescription.medical_record_id
        ).first()
        if medical_record:
            medical_record.status = 'Sold'
            print(f"✅ Updated medical record {medical_record.id} status to Sold")
    # ===================================================
    
    db.commit()
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='SELL',
        resource_type='PRESCRIPTION',
        resource_id=prescription.id,
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        new_value={"medication": prescription.medication_name, "quantity": prescription.quantity}
    )
    
    return {
        "success": True,
        "message": f"Prescription for {prescription.medication_name} marked as sold",
        "prescription_id": prescription.id,
        "prescription_status": "sold"
    }

@router.get("/pharmacy/prescription-history")
async def get_prescription_history(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pharmacy views all prescriptions they have sold (history).
    """
    from app.models import PrescriptionVoucher, PrescriptionShare
    
    # Enum comparison - CORRECT
    if current_user.role != UserRole.PHARMACY:
        raise HTTPException(status_code=403, detail="Pharmacy access only")
    
    pharmacy_id = current_user.pharmacy_id or current_user.organization_id
    
    shares = db.query(PrescriptionShare).filter(
        PrescriptionShare.pharmacy_id == pharmacy_id,
        PrescriptionShare.sold == True
    ).order_by(PrescriptionShare.sold_at.desc()).limit(50).all()
    
    result = []
    for share in shares:
        prescription = db.query(PrescriptionVoucher).filter(PrescriptionVoucher.id == share.prescription_id).first()
        if prescription:
            result.append({
                "medication_name": prescription.medication_name,
                "strength": prescription.strength or '—',
                "quantity": prescription.quantity,
                "sold_at": share.sold_at,
                "share_token": share.share_token[:8] + "..."
            })
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action='READ_HISTORY',
        resource_type='PRESCRIPTION',
        status='success',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    return result