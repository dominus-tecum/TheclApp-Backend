from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime

from app.database import get_db
from app.health_progress.models import ProgressEntry
from app.health_progress.schemas import (
    ProgressEntryCreate, 
    ProgressEntryResponse,
    DailyHealthEntryCreate,
    DailyHealthEntryResponse,
    DashboardStats,
    PatientConditionsResponse,
    SurgeryType,
    HealthTrend,
    EntryStatus
)

router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.post("/entries", response_model=ProgressEntryResponse)
async def create_progress_entry(
    entry_data: ProgressEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new progress entry from any of the 9 surgery trackers
    """
    try:
        # Prepare the data for your existing model structure
        common_data = {
            **entry_data.common_data,
            "surgery_type": entry_data.surgery_type,
            "patient_name": entry_data.patient_name,
            "submission_date": entry_data.submission_date,
            "surgery_date": entry_data.surgery_date,
            "day_post_op": entry_data.day_post_op,
            "notes": entry_data.notes
        }
        
        condition_data = {
            **entry_data.condition_data,
            "selected_condition": entry_data.surgery_type
        }
        
        # Create new progress entry using your existing model
        db_entry = ProgressEntry(
            patient_id=entry_data.patient_id,
            common_data=common_data,
            condition_data=condition_data,
            status=entry_data.status.value  # Get the string value from enum
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        # Enhance response with frontend-needed fields
        response_data = {
            **db_entry.__dict__,
            "patient_name": entry_data.patient_name,
            "surgery_type": entry_data.surgery_type
        }
        
        return ProgressEntryResponse(**response_data)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create progress entry: {str(e)}"
        )

# NEW endpoint for general health tracker
@router.post("/daily-entries", response_model=DailyHealthEntryResponse)
async def create_daily_health_entry(
    entry_data: DailyHealthEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a daily health entry from the General Health Follow-Up tracker
    Matches the frontend structure exactly
    """
    try:
        # Convert patientId to integer (your model expects integer)
        try:
            patient_id = int(entry_data.patientId)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="patientId must be a numeric value"
            )
        
        # Prepare data for your existing model structure
        common_data = {
            "patient_name": entry_data.patientName,
            "submission_date": entry_data.submissionDate,
            "submitted_at": entry_data.submittedAt,
            "condition_type": entry_data.conditionType,
            "health_trend": entry_data.healthTrend,
            "overall_wellbeing": entry_data.overallWellbeing,
            "notes": entry_data.notes
        }
        
        condition_data = {
            "selected_condition": "general_health",
            "primary_symptom": entry_data.primarySymptom,
            "health_trend": entry_data.healthTrend,
            "overall_wellbeing": entry_data.overallWellbeing
        }
        
        # Create new progress entry using your existing model
        db_entry = ProgressEntry(
            patient_id=patient_id,
            common_data=common_data,
            condition_data=condition_data,
            status=entry_data.status
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return DailyHealthEntryResponse(**db_entry.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create daily health entry: {str(e)}"
        )

# Update the existing entries endpoint to handle both types
@router.get("/entries", response_model=List[ProgressEntryResponse])
async def get_progress_entries(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    surgery_type: Optional[SurgeryType] = Query(None, description="Filter by surgery type"),
    db: Session = Depends(get_db)
):
    """Get progress entries with optional filtering"""
    query = db.query(ProgressEntry)
    
    if patient_id:
        query = query.filter(ProgressEntry.patient_id == patient_id)
    
    entries = query.order_by(ProgressEntry.created_at.desc()).all()
    
    # Transform to include surgery_type and patient_name from common_data
    response_entries = []
    for entry in entries:
        entry_dict = entry.__dict__
        common_data = entry.common_data or {}
        entry_dict["surgery_type"] = common_data.get("surgery_type")
        entry_dict["patient_name"] = common_data.get("patient_name")
        response_entries.append(ProgressEntryResponse(**entry_dict))
    
    # Filter by surgery_type if provided
    if surgery_type:
        response_entries = [
            entry for entry in response_entries 
            if entry.surgery_type == surgery_type
        ]
    
    return response_entries

# Add endpoint to check existing entries (used by your frontend)
@router.get("/entries/{patient_id}/{date}")
async def check_existing_entry(
    patient_id: str,
    date: str,
    db: Session = Depends(get_db)
):
    """Check if an entry already exists for a patient on a specific date"""
    try:
        patient_id_int = int(patient_id)
    except ValueError:
        return {"exists": False}
    
    entries = db.query(ProgressEntry).filter(
        ProgressEntry.patient_id == patient_id_int
    ).all()
    
    for entry in entries:
        common_data = entry.common_data or {}
        if common_data.get("submission_date") == date:
            return {"exists": True, "entry_id": entry.id}
    
    return {"exists": False}

@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for healthcare providers"""
    total_entries = db.query(ProgressEntry).count()
    
    # FIXED: Count urgent and monitor entries correctly
    urgent_entries = 0
    monitor_entries = 0
    
    all_entries = db.query(ProgressEntry).all()
    for entry in all_entries:
        # Check both common_data and condition_data for status
        common_data = entry.common_data or {}
        condition_data = entry.condition_data or {}
        
        # Look for status in condition_data first, then common_data
        status = condition_data.get("status") or common_data.get("status")
        
        if status == "urgent":
            urgent_entries += 1
        elif status == "monitor":
            monitor_entries += 1
    
    # Count entries by surgery type
    surgery_types = [st.value for st in SurgeryType]
    surgery_stats = {}
    
    for surgery_type in surgery_types:
        count = 0
        entries = db.query(ProgressEntry).all()
        for entry in entries:
            if entry.common_data and entry.common_data.get("surgery_type") == surgery_type:
                count += 1
        surgery_stats[surgery_type] = count
    
    return DashboardStats(
        total_entries=total_entries,
        urgent_entries=urgent_entries,
        monitor_entries=monitor_entries,
        surgery_type_stats=surgery_stats
    )

@router.get("/recent-entries", response_model=List[ProgressEntryResponse])
async def get_recent_entries(
    limit: int = Query(10, description="Number of recent entries to return"),
    db: Session = Depends(get_db)
):
    """Get most recent progress entries"""
    entries = db.query(ProgressEntry).order_by(
        ProgressEntry.created_at.desc()
    ).limit(limit).all()
    
    response_entries = []
    for entry in entries:
        entry_dict = entry.__dict__
        common_data = entry.common_data or {}
        entry_dict["surgery_type"] = common_data.get("surgery_type")
        entry_dict["patient_name"] = common_data.get("patient_name")
        response_entries.append(ProgressEntryResponse(**entry_dict))
    
    return response_entries

@router.get("/patients/me/conditions", response_model=PatientConditionsResponse)
async def get_patient_conditions(
    patient_id: int = Query(..., description="Patient ID"),
    db: Session = Depends(get_db)
):
    """Get conditions and progress for a specific patient"""
    entries = db.query(ProgressEntry).filter(
        ProgressEntry.patient_id == patient_id
    ).order_by(ProgressEntry.created_at.desc()).all()
    
    if not entries:
        return PatientConditionsResponse(
            patient_id=patient_id,
            patient_name="",
            conditions=[],
            recent_progress=[]
        )
    
    # Get unique surgery types/conditions for this patient
    conditions = []
    for entry in entries:
        if entry.common_data and entry.common_data.get("surgery_type"):
            conditions.append(entry.common_data.get("surgery_type"))
    
    unique_conditions = list(set(conditions))
    
    # Transform recent entries for response
    recent_progress = []
    for entry in entries[:5]:  # Last 5 entries
        entry_dict = entry.__dict__
        common_data = entry.common_data or {}
        entry_dict["surgery_type"] = common_data.get("surgery_type")
        entry_dict["patient_name"] = common_data.get("patient_name")
        recent_progress.append(ProgressEntryResponse(**entry_dict))
    
    patient_name = entries[0].common_data.get("patient_name", "") if entries else ""
    
    return PatientConditionsResponse(
        patient_id=patient_id,
        patient_name=patient_name,
        conditions=unique_conditions,
        recent_progress=recent_progress
    )