from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Appointment
from app.authentication.dependencies import require_admin, require_staff, require_doctor
from app.authentication.auth import get_current_user

router = APIRouter()

# Keep your existing HTML routes
@router.get("/login", response_class=HTMLResponse)
async def staff_login():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Staff Login</title>
    </head>
    <body>
        <h1>Staff Login Page</h1>
        <p>If you can see this, the route is working!</p>
        <form>
            <input type="text" placeholder="Username">
            <input type="password" placeholder="Password">
            <button type="button">Login</button>
        </form>
    </body>
    </html>
    """

@router.get("/dashboard", response_class=HTMLResponse)
async def staff_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Staff Dashboard</title>
    </head>
    <body>
        <h1>Staff Dashboard</h1>
        <p>Welcome to the Healthcare Management System</p>
        <ul>
            <li><a href="/docs">API Docs</a></li>
            <li><a href="/staff/login">Login</a></li>
        </ul>
    </body>
    </html>
    """

# 🔥 NEW ADMIN API ENDPOINTS 🔥

# Get all appointments (Admin only)
@router.get("/appointments")
async def get_all_appointments(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all appointments - Admin only"""
    query = db.query(Appointment)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    total = query.count()
    appointments = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "appointments": appointments,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# Get pending appointments for approval
@router.get("/appointments/pending")
async def get_pending_appointments(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get appointments pending approval - Admin only"""
    pending_appointments = db.query(Appointment).filter(
        Appointment.status == "pending"
    ).all()
    
    return {"pending_appointments": pending_appointments}

# Approve or reject appointment
@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status_update: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject an appointment - Admin only"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    new_status = status_update.get("status")
    reason = status_update.get("reason", "")
    
    # Validate status
    valid_statuses = ["pending", "approved", "rejected", "cancelled", "completed"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # Update appointment status
    appointment.status = new_status
    db.commit()
    
    return {
        "message": f"Appointment {new_status} successfully",
        "appointment_id": appointment_id,
        "new_status": new_status
    }

# Get all patients (Staff only - both admin and doctor)
@router.get("/patients")
async def get_all_patients(
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get all patients - Staff only"""
    patients = db.query(User).filter(User.role == "patient").all()
    
    return {
        "patients": patients,
        "total": len(patients)
    }

# Staff dashboard data
@router.get("/dashboard-data")
async def get_staff_dashboard_data(
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get staff dashboard statistics - Staff only"""
    total_patients = db.query(User).filter(User.role == "patient").count()
    total_appointments = db.query(Appointment).count()
    pending_appointments = db.query(Appointment).filter(Appointment.status == "pending").count()
    
    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "user_role": current_user.role.value
    }

# 🔥 NEW POST ENDPOINTS 🔥

# Create prescription (Doctor only)
@router.post("/prescriptions")
async def create_prescription(
    prescription_data: dict,
    current_user: User = Depends(require_doctor),  # Only doctors can prescribe
    db: Session = Depends(get_db)
):
    """Create a prescription - Doctor only"""
    return {
        "message": "Prescription created successfully",
        "prescription": prescription_data,
        "created_by": current_user.username
    }

# Create lab order (Doctor only)  
@router.post("/lab-orders")
async def create_lab_order(
    lab_order_data: dict,
    current_user: User = Depends(require_doctor),  # Only doctors can order labs
    db: Session = Depends(get_db)
):
    """Order lab tests - Doctor only"""
    return {
        "message": "Lab order created successfully",
        "lab_order": lab_order_data,
        "ordered_by": current_user.username
    }

# Create medical note (Staff - both doctors and admins)
@router.post("/medical-notes")
async def create_medical_note(
    note_data: dict,
    current_user: User = Depends(require_staff),  # Both doctors and admins
    db: Session = Depends(get_db)
):
    """Add medical notes - Staff only"""
    return {
        "message": "Medical note added successfully",
        "note": note_data,
        "author": current_user.username,
        "author_role": current_user.role.value
    }

# Create appointment (Admin only - for scheduling)
@router.post("/appointments")
async def create_appointment(
    appointment_data: dict,
    current_user: User = Depends(require_admin),  # Only admins can create appointments
    db: Session = Depends(get_db)
):
    """Create appointment - Admin only"""
    return {
        "message": "Appointment created successfully",
        "appointment": appointment_data,
        "created_by": current_user.username
    }