from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import date, datetime
import json
import logging

from app.database import get_db
from app.health_progress.burn_care.models import BurnCareEntry
from app.health_progress.burn_care.schemas import BurnCareCreate, BurnCareResponse, BurnCareCheckResponse
from app.health_progress.burn_care.services import BurnCareService

router = APIRouter()
logger = logging.getLogger(__name__)

# Debug endpoint to see raw request data
@router.post("/burn-care/entries/debug")
async def debug_burn_care_entry(request: Request, db: Session = Depends(get_db)):
    """
    Temporary endpoint to debug raw request data and validation issues
    """
    try:
        # Get raw request body
        raw_body = await request.body()
        raw_body_str = raw_body.decode('utf-8') if raw_body else "Empty body"
        
        print("🚨 === RAW REQUEST DEBUG ===")
        print("🚨 RAW REQUEST BODY:", raw_body_str)
        
        # Try to parse as JSON
        json_data = {}
        try:
            json_data = await request.json()
            print("🚨 PARSED JSON DATA:")
            for key, value in json_data.items():
                print(f"🚨   {key}: {value} (type: {type(value).__name__})")
        except Exception as json_error:
            print(f"🚨 JSON PARSE ERROR: {json_error}")
            return {
                "error": "JSON parse error",
                "raw_body": raw_body_str,
                "json_error": str(json_error)
            }
        
        # Try to validate with Pydantic schema
        validation_errors = []
        try:
            validated_data = BurnCareCreate(**json_data)
            print("🚨 SCHEMA VALIDATION: SUCCESS")
            print("🚨 Validated data:", validated_data.dict())
        except Exception as validation_error:
            print(f"🚨 SCHEMA VALIDATION ERROR: {validation_error}")
            validation_errors = str(validation_error)
            
        return {
            "status": "debug_complete",
            "raw_body": raw_body_str,
            "parsed_json": json_data,
            "validation_errors": validation_errors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"🚨 DEBUG ENDPOINT ERROR: {e}")
        return {"error": f"Debug endpoint failed: {str(e)}"}

@router.post("/burn-care/entries", response_model=BurnCareResponse)
async def create_burn_care_entry(
    entry: BurnCareCreate,
    db: Session = Depends(get_db)
):
    """
    Create burn care entry - accept frontend data as-is
    """
    try:
        logger.info("=== BURN CARE POST REQUEST ===")
        logger.info(f"Received burn care entry for patient: {entry.patient_id}")
        
        # Log each field to see what's being sent
        entry_dict = entry.dict()
        for field, value in entry_dict.items():
            logger.info(f"Field: {field} = {value} (type: {type(value).__name__})")
        
        # Validate required fields
        if not entry.patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient ID is required"
            )
        
        if not entry.submission_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission date is required"
            )
        
       
        
        # Create the entry
        result = BurnCareService.create_burn_care_entry(db=db, entry=entry)
        logger.info(f"Entry saved successfully with ID: {result.id}")
        
        # Convert nested database data to flat response
        response_data = BurnCareResponse(
            id=result.id,
            patient_id=result.patient_id,
            patient_name=result.patient_name,
            surgery_type=result.surgery_type,
            condition_type=result.condition_type,
            submission_date=result.submission_date,
            submitted_at=result.submitted_at if hasattr(result, 'submitted_at') else datetime.utcnow(),
            dayPost_op=result.common_data.get("day_post_op", 0),
            pain_level=result.common_data.get("pain_level", 0),
            temperature=result.common_data.get("temperature", ""),
            status=result.common_data.get("status", "good"),
            itching=result.condition_data.get("itching", "none"),
            wound_appearance=result.condition_data.get("wound_appearance", "pink"),
            drainage=result.condition_data.get("drainage", "none"),
            rom_exercises=result.condition_data.get("rom_exercises", False),
            joint_tightness=result.condition_data.get("joint_tightness", "none"),
            mobility=result.condition_data.get("mobility", "bed_bound"),
            compression_garment=result.condition_data.get("compression_garment", False),
            scar_appearance=result.condition_data.get("scar_appearance", "red_raised"),
            protein_intake=result.condition_data.get("protein_intake", ""),
            fluid_intake=result.condition_data.get("fluid_intake", ""),
            additional_notes=result.condition_data.get("additional_notes", ""),
            created_at=result.created_at,
            updated_at=result.updated_at
        )
        
        logger.info(f"Response prepared for entry ID: {result.id}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in create_burn_care_entry: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create burn care entry: {str(e)}"
        )

@router.get("/burn-care/entries/{patient_id}/{date}", response_model=BurnCareCheckResponse)
async def check_existing_entry(
    patient_id: str,
    date: date,
    db: Session = Depends(get_db)
):
    """
    Check if burn care entry exists for specific patient and date
    """
    try:
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient ID is required"
            )
        
        existing_entry = BurnCareService.check_existing_entry(db, patient_id, date)
        
        return BurnCareCheckResponse(
            exists=existing_entry is not None,
            entry_id=existing_entry.id if existing_entry else None,
            patient_id=patient_id,
            date=date
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking existing entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking for existing entry: {str(e)}"
        )

@router.get("/burn-care/entries")
async def get_all_burn_care_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get ALL burn care entries for dashboard with pagination
    """
    try:
        entries = BurnCareService.get_all_burn_care_entries(db, skip=skip, limit=limit)
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date.isoformat() if entry.submission_date else None,
                "surgery_type": entry.surgery_type,
                "condition_type": entry.condition_type,
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
            })
        
        total_count = db.query(BurnCareEntry).count()
        
        return {
            "entries": formatted_entries,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "returned": len(entries),
            "condition_type": "burn_care"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving burn care entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving burn care entries: {str(e)}"
        )

@router.get("/burn-care/entries/patient/{patient_id}")
async def get_patient_burn_care_entries(
    patient_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all burn care entries for a specific patient with pagination
    """
    try:
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient ID is required"
            )
        
        entries = db.query(BurnCareEntry).filter(
            BurnCareEntry.patient_id == patient_id
        ).offset(skip).limit(limit).all()
        
        total_count = db.query(BurnCareEntry).filter(
            BurnCareEntry.patient_id == patient_id
        ).count()
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": entry.patient_name,
                "submission_date": entry.submission_date.isoformat() if entry.submission_date else None,
                "surgery_type": entry.surgery_type,
                "condition_type": entry.condition_type,
                "common_data": entry.common_data,
                "condition_data": entry.condition_data,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
            })
        
        return {
            "entries": formatted_entries,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "returned": len(entries),
            "patient_id": patient_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patient entries: {str(e)}"
        )

@router.get("/burn-care/entries/{entry_id}", response_model=BurnCareResponse)
async def get_burn_care_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific burn care entry by ID
    """
    try:
        if not entry_id or entry_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid entry ID is required"
            )
        
        entry = db.query(BurnCareEntry).filter(BurnCareEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Burn care entry with ID {entry_id} not found"
            )
        
        # Convert nested database data to flat response
        return BurnCareResponse(
            id=entry.id,
            patient_id=entry.patient_id,
            patient_name=entry.patient_name,
            surgery_type=entry.surgery_type,
            condition_type=entry.condition_type,
            submission_date=entry.submission_date,
            submitted_at=entry.submitted_at if hasattr(entry, 'submitted_at') else datetime.utcnow(),
            dayPost_op=entry.common_data.get("day_post_op", 0),
            pain_level=entry.common_data.get("pain_level", 0),
            temperature=entry.common_data.get("temperature", ""),
            status=entry.common_data.get("status", "good"),
            itching=entry.condition_data.get("itching", "none"),
            wound_appearance=entry.condition_data.get("wound_appearance", "pink"),
            drainage=entry.condition_data.get("drainage", "none"),
            rom_exercises=entry.condition_data.get("rom_exercises", False),
            joint_tightness=entry.condition_data.get("joint_tightness", "none"),
            mobility=entry.condition_data.get("mobility", "bed_bound"),
            compression_garment=entry.condition_data.get("compression_garment", False),
            scar_appearance=entry.condition_data.get("scar_appearance", "red_raised"),
            protein_intake=entry.condition_data.get("protein_intake", ""),
            fluid_intake=entry.condition_data.get("fluid_intake", ""),
            additional_notes=entry.condition_data.get("additional_notes", ""),
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving burn care entry {entry_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving burn care entry: {str(e)}"
        )

# Health check endpoint
@router.get("/burn-care/health")
async def health_check():
    """
    Health check for burn care endpoints
    """
    return {
        "status": "healthy",
        "service": "burn_care",
        "timestamp": datetime.utcnow().isoformat()
    }