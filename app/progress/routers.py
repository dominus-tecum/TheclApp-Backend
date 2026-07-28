from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_user

# Import your schemas and services
from app.progress.schemas import (
    ProgressEntryCreate, 
    ProgressEntryResponse,
    DashboardStats,
    RecentEntry
)
from app.progress.services import ProgressService

router = APIRouter()

@router.post("/entries", response_model=ProgressEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_progress_entry(
    entry_data: dict,  # Using dict to handle flexible LifelongScreen data
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new progress entry from LifelongScreen.tsx
    Handles the enhanced data structure for chronic conditions
    """
    progress_service = ProgressService(db)
    try:
        # Transform LifelongScreen data to match your schema
        transformed_data = {
            "common_data": {
                "pain_level": entry_data.get("commonData", {}).get("painLevel", 5),
                "energy_level": entry_data.get("commonData", {}).get("energyLevel", 5),
                "sleep_hours": entry_data.get("commonData", {}).get("sleepHours", 7),
                "sleep_quality": entry_data.get("commonData", {}).get("sleepQuality", 3),
                "activity_level": entry_data.get("commonData", {}).get("activityLevel", "normal"),
                "medications": {
                    "morning": entry_data.get("commonData", {}).get("medications", {}).get("morning", False),
                    "afternoon": entry_data.get("commonData", {}).get("medications", {}).get("afternoon", False),
                    "evening": entry_data.get("commonData", {}).get("medications", {}).get("evening", False),
                    "side_effects": entry_data.get("commonData", {}).get("medications", {}).get("sideEffects", "")
                },
                "symptoms": {
                    "fatigue": entry_data.get("commonData", {}).get("symptoms", {}).get("fatigue", False),
                    "nausea": entry_data.get("commonData", {}).get("symptoms", {}).get("nausea", False),
                    "breathing_issues": entry_data.get("commonData", {}).get("symptoms", {}).get("breathingIssues", False),
                    "pain": entry_data.get("commonData", {}).get("symptoms", {}).get("pain", False),
                    "swelling": entry_data.get("commonData", {}).get("symptoms", {}).get("swelling", False),
                    "other": entry_data.get("commonData", {}).get("symptoms", {}).get("other", "")
                },
                "notes": entry_data.get("commonData", {}).get("notes", "")
            },
            "condition_data": {
                "selected_condition": entry_data.get("conditionData", {}).get("selectedCondition"),
                "blood_glucose": entry_data.get("conditionData", {}).get("bloodGlucose"),
                "blood_pressure_systolic": entry_data.get("conditionData", {}).get("bloodPressureSystolic"),
                "blood_pressure_diastolic": entry_data.get("conditionData", {}).get("bloodPressureDiastolic"),
                "heart_weight": entry_data.get("conditionData", {}).get("heartWeight"),
                "heart_swelling": entry_data.get("conditionData", {}).get("heartSwelling"),
                "heart_breathing": entry_data.get("conditionData", {}).get("heartBreathing"),
                "cancer_side_effects": entry_data.get("conditionData", {}).get("cancerSideEffects"),
                "kidney_weight": entry_data.get("conditionData", {}).get("kidneyWeight"),
                "kidney_swelling": entry_data.get("conditionData", {}).get("kidneySwelling"),
                "kidney_urine_output": entry_data.get("conditionData", {}).get("kidneyUrineOutput"),
                "kidney_fluid_intake": entry_data.get("conditionData", {}).get("kidneyFluidIntake")
            },
            "status": entry_data.get("status", "draft"),
            "submitted_at": entry_data.get("submittedAt")
        }
        
        return progress_service.create_progress_entry(transformed_data, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create progress entry: {str(e)}"
        )

@router.get("/patients/me/conditions")
async def get_patient_conditions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's chronic conditions for LifelongScreen.tsx
    Returns conditions that match our 5 chronic categories
    """
    progress_service = ProgressService(db)
    try:
        # Get all patient conditions
        all_conditions = progress_service.get_patient_conditions(current_user["id"])
        
        # Map to our 5 chronic condition categories
        chronic_conditions = []
        condition_mapping = {
            'diabetes': 'diabetes',
            'hypertension': 'hypertension', 
            'heart_disease': 'heart',
            'cardiovascular': 'heart',
            'cancer': 'cancer',
            'kidney_disease': 'kidney',
            'ckd': 'kidney'
        }
        
        for condition in all_conditions:
            mapped_condition = condition_mapping.get(condition.lower())
            if mapped_condition and mapped_condition not in chronic_conditions:
                chronic_conditions.append(mapped_condition)
        
        return {"conditions": chronic_conditions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load patient conditions: {str(e)}"
        )

@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for LifelongScreen users
    """
    progress_service = ProgressService(db)
    return progress_service.get_dashboard_stats(current_user["id"])

@router.get("/recent-entries", response_model=List[RecentEntry])
async def get_recent_entries(
    limit: Optional[int] = 5,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent progress entries for dashboard
    """
    progress_service = ProgressService(db)
    return progress_service.get_recent_entries(current_user["id"], limit)

@router.get("/entries", response_model=List[ProgressEntryResponse])
async def get_progress_entries(
    filter: Optional[str] = "all",
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress entries for history screen
    """
    progress_service = ProgressService(db)
    return progress_service.get_progress_entries(current_user["id"], filter, limit)