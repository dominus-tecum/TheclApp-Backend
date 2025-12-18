from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.database import get_db
from app.fertility.models import (
    FertilityEntry, FertilityProfile, Patient,
    # ALL ENUMS used in insights functions:
    CervicalFluidType, LHTestResult, FertilityStatus, CyclePhase,
    SymptomSeverity, LibidoLevel, MoodLevel, EnergyLevel, StressLevel,
    CervicalFluidAmount, CervicalPosition, CervicalFirmness, CervicalOpening,
    MenstrualFlow, IntercoursePosition, ContraceptionType
)

from app.fertility.schemas import (
    FertilityEntryCreate, FertilityEntryUpdate, FertilityEntryResponse,
    FertilityProfileCreate, FertilityProfileUpdate, FertilityProfileResponse,
    PatientResponse, PaginationParams, FertilityEntryFilter,
    CycleSummaryRequest, CycleSummaryResponse,
    DoctorVisitSummaryRequest, DoctorVisitSummaryResponse,
    PartnerUpdateRequest, PartnerUpdateResponse,
    PaginatedResponse, ValidationResult
)
from app.fertility.services import (
    FertilityEntryService, FertilityProfileService,
    CycleAnalysisService, PatientService, ExportService
)
from app.authentication.auth import get_current_user

router = APIRouter()



# Dependency to get current patient ID
# In app/fertility/routers.py, update the function:
def get_current_patient_id(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> int:
    """Get current patient ID from user"""

    print(f"🔍 [GET-PATIENT-ID] Current user: {current_user}")
    print(f"🔍 [GET-PATIENT-ID] Current user ID: {current_user.get('id')}")
    print(f"🔍 [GET-PATIENT-ID] Current user ID type: {type(current_user.get('id'))}")


    # DEBUG: Show all patients in DB
    all_patients = db.query(Patient).all()
    print(f"🔍 [GET-PATIENT-ID] All patients in DB:")
    for p in all_patients:
        print(f"  - id={p.id}, user_id={p.user_id} (type: {type(p.user_id)})")
   
        
    patient_service = PatientService(db)
    patient = patient_service.get_patient_by_user_id(str(current_user.get("id")))

    print(f"🔍 [GET-PATIENT-ID] Patient found: {patient}")
    
    if not patient:

        
        print(f"🔍 [GET-PATIENT-ID] Creating new patient...")
        patient_data = {
            "user_id": str(current_user.get("id")),
            "name": current_user.get("name", "User"),
            "email": current_user.get("email", "")
        }
        patient = patient_service.create_patient(patient_data)
    
    print(f"✅ [GET-PATIENT-ID] Returning patient ID: {patient.id}")
    return patient.id




# Add this to your routers.py (around line 30, after the imports)



@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(
    patient_id: str,  # CHANGED FROM int TO str
    db: Session = Depends(get_db)
):
    """Get patient by ID or user_id (handles both string '3' and integer 1)"""
    print(f"🔍 [PATIENT-BY-ID] Called with patient_id='{patient_id}' (type: {type(patient_id)})")
    
    patient_service = PatientService(db)
    patient = None
    
    # First try to find by user_id (string "3")
    patient = patient_service.get_patient_by_user_id(patient_id)
    print(f"🔍 [PATIENT-BY-ID] Search by user_id='{patient_id}': {'FOUND' if patient else 'NOT FOUND'}")
    
    # If not found, try as integer patient_id
    if not patient:
        try:
            patient_id_int = int(patient_id)
            patient = patient_service.get_patient(patient_id_int)
            print(f"🔍 [PATIENT-BY-ID] Search by patient_id={patient_id_int}: {'FOUND' if patient else 'NOT FOUND'}")
        except ValueError:
            print(f"🔍 [PATIENT-BY-ID] '{patient_id}' is not a valid integer")
            pass
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get fertility profile
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient.id)
    
    # Map to EXACT PatientResponse field names
    return {
        "id": patient.id,  # Must be int (not string)
        "user_id": patient.user_id,  # Must be string
        "name": patient.name,  # Not "patient_name"
        "email": patient.email,
        "birth_date": str(patient.birth_date) if patient.birth_date else None,  # Convert to string
        "phone_number": getattr(patient, 'phone_number', None),
        "created_at": patient.created_at,
        "updated_at": getattr(patient, 'updated_at', None),
        "fertility_profile": {
            "id": profile.id if profile else None,
            "patient_id": patient.id,
            "cycle_length": profile.cycle_length if profile else 28,
            "period_length": profile.period_length if profile else 5,
            "last_period_date": profile.last_period_date if profile else None,
            "trying_to_conceive": profile.trying_to_conceive if profile else True,
            "fertility_issues": profile.fertility_issues if profile else [],
            "high_risk": profile.high_risk if profile else False,
            "created_at": profile.created_at if profile else datetime.now(),
            "updated_at": profile.updated_at if profile else None
        } if profile else None
    }










@router.get("/entries/{patient_id}/{date}")
def get_entry_by_patient_and_date(
    patient_id: str,
    date: str,
    db: Session = Depends(get_db)
):
    """Check if entry exists for patient on specific date"""
    print(f"🔍 [CHECK-ENTRY] Checking entry for patient {patient_id} on {date}")
    
    entry_service = FertilityEntryService(db)
    entry = entry_service.get_entry_by_date(patient_id, date)
    
    if entry:
        print(f"✅ [CHECK-ENTRY] Entry found: {entry.id}")
        return {"exists": True, "id": entry.id, "entry": entry_to_dict(entry)}
    else:
        print(f"❌ [CHECK-ENTRY] No entry found")
        return {"exists": False}






# In app/fertility/routers.py, update the function:
@router.get("/entries", response_model=PaginatedResponse)
def get_fertility_entries(
    patient_id: int = Depends(get_current_patient_id),
    filters: FertilityEntryFilter = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """Get fertility entries with filtering and pagination"""
    print(f"🔍 [FERTILITY-ENTRIES] ENTRY POINT - Request received")
    print(f"🔍 [FERTILITY-ENTRIES] Patient ID from dependency: {patient_id}")
    
    # If we get here, auth succeeded!
    print(f"✅ [FERTILITY-ENTRIES] Authentication SUCCESS")
    
    entry_service = FertilityEntryService(db)
    entries, total = entry_service.get_entries(patient_id, filters, pagination)
    
    print(f"🔍 [FERTILITY-ENTRIES] Found {len(entries)} entries")
    
    # CONVERT SQLAlchemy objects to dictionaries
    entry_dicts = []
    for entry in entries:
        entry_dict = {}
        # Manually extract all fields
        entry_dict["id"] = entry.id
        entry_dict["patient_id"] = entry.patient_id
        entry_dict["patient_name"] = entry.patient_name
        entry_dict["cycle_day"] = entry.cycle_day
        entry_dict["predicted_ovulation_day"] = entry.predicted_ovulation_day
        entry_dict["fertility_window_start"] = entry.fertility_window_start
        entry_dict["fertility_window_end"] = entry.fertility_window_end
        entry_dict["fertility_status"] = entry.fertility_status.value if entry.fertility_status else None
        entry_dict["cycle_phase"] = entry.cycle_phase.value if entry.cycle_phase else None
        entry_dict["bbt_temperature"] = entry.bbt_temperature
        entry_dict["bbt_time"] = entry.bbt_time
        entry_dict["cervical_fluid_type"] = entry.cervical_fluid_type.value if entry.cervical_fluid_type else None
        entry_dict["cervical_fluid_amount"] = entry.cervical_fluid_amount.value if entry.cervical_fluid_amount else None
        entry_dict["lh_test_result"] = entry.lh_test_result.value if entry.lh_test_result else None
        entry_dict["libido_level"] = entry.libido_level.value if entry.libido_level else None
        entry_dict["mood"] = entry.mood.value if entry.mood else None
        entry_dict["energy_level"] = entry.energy_level.value if entry.energy_level else None
        entry_dict["intercourse_today"] = entry.intercourse_today
        entry_dict["contraception_used"] = entry.contraception_used.value if entry.contraception_used else None
        entry_dict["stress_level"] = entry.stress_level.value if entry.stress_level else None
        entry_dict["sleep_hours"] = entry.sleep_hours
        entry_dict["medications"] = entry.medications
        entry_dict["additional_notes"] = entry.additional_notes
        entry_dict["submission_date"] = entry.submission_date
        entry_dict["submitted_at"] = entry.submitted_at.isoformat() if entry.submitted_at else None
        entry_dict["updated_at"] = entry.updated_at.isoformat() if entry.updated_at else None
        
        entry_dicts.append(entry_dict)
    
    print(f"🔍 [FERTILITY-ENTRIES] Converted {len(entry_dicts)} entries to dictionaries")
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return PaginatedResponse(
        items=entry_dicts,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )


@router.get("/entries/{entry_id}", response_model=FertilityEntryResponse)
def get_fertility_entry(
    entry_id: int,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get a specific fertility entry"""
    entry_service = FertilityEntryService(db)
    entry = entry_service.get_entry(entry_id, patient_id)
    return entry


@router.put("/entries/{entry_id}", response_model=FertilityEntryResponse)
def update_fertility_entry(
    entry_id: int,
    update_data: FertilityEntryUpdate,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Update a fertility entry"""
    entry_service = FertilityEntryService(db)
    entry = entry_service.update_entry(entry_id, patient_id, update_data)
    return entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fertility_entry(
    entry_id: int,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Delete a fertility entry"""
    entry_service = FertilityEntryService(db)
    entry_service.delete_entry(entry_id, patient_id)
    return


@router.get("/entries/date/{date_str}", response_model=Optional[FertilityEntryResponse])
def get_entry_by_date(
    date_str: str,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get fertility entry by date"""
    entry_service = FertilityEntryService(db)
    entry = entry_service.get_entry_by_date(patient_id, date_str)
    return entry


@router.get("/entries/cycle/{cycle_number}", response_model=List[FertilityEntryResponse])
def get_cycle_entries(
    cycle_number: int,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get all entries for a specific cycle"""
    entry_service = FertilityEntryService(db)
    entries = entry_service.get_cycle_entries(patient_id, cycle_number)
    return entries


# Fertility Profile Routes
@router.post("/profile", response_model=FertilityProfileResponse, status_code=status.HTTP_201_CREATED)
def create_fertility_profile(
    profile_data: FertilityProfileCreate,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Create a fertility profile"""
    profile_service = FertilityProfileService(db)
    profile = profile_service.create_profile(patient_id, profile_data)
    return profile


@router.get("/profile", response_model=Optional[FertilityProfileResponse])
def get_fertility_profile(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get fertility profile"""
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient_id)
    return profile


@router.put("/profile", response_model=FertilityProfileResponse)
def update_fertility_profile(
    update_data: FertilityProfileUpdate,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Update fertility profile"""
    profile_service = FertilityProfileService(db)
    profile = profile_service.update_profile(patient_id, update_data)
    return profile


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_fertility_profile(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Delete fertility profile"""
    profile_service = FertilityProfileService(db)
    profile_service.delete_profile(patient_id)
    return


# Cycle Analysis Routes
@router.post("/analyze/cycle", response_model=CycleSummaryResponse)
def analyze_cycle(
    analysis_request: CycleSummaryRequest,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Analyze fertility cycle and generate summary"""
    analysis_service = CycleAnalysisService(db)
    
    # Get patient info
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Generate summary
    summary = analysis_service.generate_cycle_summary(
        patient_id=patient_id,
        cycle_id=analysis_request.cycle_id,
        start_date=analysis_request.start_date,
        end_date=analysis_request.end_date
    )
    
    return CycleSummaryResponse(
        patient_id=patient_id,
        patient_name=patient.name,
        **summary
    )


@router.post("/analyze/doctor-summary", response_model=DoctorVisitSummaryResponse)
def generate_doctor_summary(
    summary_request: DoctorVisitSummaryRequest,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Generate doctor visit summary"""
    analysis_service = CycleAnalysisService(db)
    
    # Get patient info
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Generate summary
    summary = analysis_service.generate_doctor_summary(
        patient_id=patient_id,
        timeframe=summary_request.timeframe
    )
    
    return DoctorVisitSummaryResponse(**summary)


@router.post("/analyze/partner-update", response_model=PartnerUpdateResponse)
def generate_partner_update(
    update_request: PartnerUpdateRequest,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Generate partner update"""
    # Get patient info
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Get latest entry
    entry_service = FertilityEntryService(db)
    entries, _ = entry_service.get_entries(patient_id)
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fertility entries found"
        )
    
    latest_entry = entries[0]
    
    # Get fertility profile
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient_id)
    
    # Calculate fertility probability
    from services import FertilityCycleCalculator
    calculator = FertilityCycleCalculator()
    
    fertility_window = {"start": 0, "end": 0}
    if profile and profile.last_period_date and profile.cycle_length:
        fertility_window = calculator.calculate_fertility_window(profile.cycle_length)
    
    # Count fertile signs
    fertile_signs = 0
    if latest_entry.cervical_fluid_type == "egg_white":
        fertile_signs += 2
    if latest_entry.lh_test_result in ["peak", "high"]:
        fertile_signs += 2
    if latest_entry.libido_level in ["high", "very_high"]:
        fertile_signs += 1
    
    fertility_probability = calculator.calculate_fertility_probability(
        latest_entry.cycle_day,
        fertility_window,
        fertile_signs
    )
    
    # Prepare observations
    observations = {}
    if update_request.include_details:
        observations = {
            "cervical_fluid": latest_entry.cervical_fluid_type,
            "lh_test": latest_entry.lh_test_result,
            "libido": latest_entry.libido_level,
            "mood": latest_entry.mood,
            "cycle_day": latest_entry.cycle_day
        }
    
    # Generate recommendations
    recommendations = None
    if update_request.include_recommendations:
        recommendations = []
        if latest_entry.fertility_status == "fertile":
            recommendations.append("Optimal time for intercourse - consider today or tomorrow")
        elif latest_entry.fertility_status == "possibly_fertile":
            recommendations.append("Good time for intercourse - consider every other day")
        elif latest_entry.lh_test_result == "peak":
            recommendations.append("Peak LH detected - ovulation likely in 24-48 hours")
    
    return PartnerUpdateResponse(
        patient_name=patient.name,
        cycle_day=latest_entry.cycle_day,
        fertility_status=latest_entry.fertility_status,
        fertility_probability=fertility_probability,
        observations=observations,
        recommendations=recommendations,
        generated_at=datetime.utcnow()
    )


@router.get("/analyze/stats")
def get_cycle_statistics(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get cycle statistics"""
    analysis_service = CycleAnalysisService(db)
    
    # Get all entries
    entry_service = FertilityEntryService(db)
    entries, _ = entry_service.get_entries(patient_id)
    
    if not entries:
        return {"message": "No data available for analysis"}
    
    # Group by cycle
    cycles = analysis_service._group_entries_by_cycle(entries)
    
    # Analyze multiple cycles
    stats = analysis_service._analyze_multiple_cycles(cycles)
    
    # Get fertility profile
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient_id)
    
    # Add profile info
    if profile:
        stats["profile"] = {
            "trying_to_conceive": profile.trying_to_conceive,
            "cycle_length": profile.cycle_length,
            "last_period_date": profile.last_period_date
        }
    
    return stats


@router.get("/analyze/bbt-chart")
def get_bbt_chart_data(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Get BBT chart data"""
    entry_service = FertilityEntryService(db)
    entries, _ = entry_service.get_entries(patient_id)
    
    if not entries:
        return {"message": "No BBT data available"}
    
    # Filter entries with BBT data
    bbt_entries = [
        {
            "date": entry.submission_date,
            "temperature": entry.bbt_temperature,
            "cycle_day": entry.cycle_day,
            "fertility_status": entry.fertility_status
        }
        for entry in entries
        if entry.bbt_temperature is not None
    ]
    
    return {
        "bbt_data": bbt_entries,
        "total_readings": len(bbt_entries),
        "date_range": {
            "start": min([e["date"] for e in bbt_entries]) if bbt_entries else None,
            "end": max([e["date"] for e in bbt_entries]) if bbt_entries else None
        }
    }


# Export Routes
@router.get("/export/cycle-summary/text")
def export_cycle_summary_text(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Export cycle summary as text"""
    # Get patient info
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Get latest entry
    entry_service = FertilityEntryService(db)
    entries, _ = entry_service.get_entries(patient_id)
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fertility entries found"
        )
    
    latest_entry = entries[0]
    
    # Get fertility profile
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient_id)
    
    # Calculate fertility probability
    from services import FertilityCycleCalculator
    calculator = FertilityCycleCalculator()
    
    fertility_window = {"start": 0, "end": 0}
    fertility_probability = 0
    
    if profile and profile.last_period_date and profile.cycle_length:
        fertility_window = calculator.calculate_fertility_window(profile.cycle_length)
        
        # Count fertile signs
        fertile_signs = 0
        if latest_entry.cervical_fluid_type == "egg_white":
            fertile_signs += 2
        if latest_entry.lh_test_result in ["peak", "high"]:
            fertile_signs += 2
        if latest_entry.libido_level in ["high", "very_high"]:
            fertile_signs += 1
        
        fertility_probability = calculator.calculate_fertility_probability(
            latest_entry.cycle_day,
            fertility_window,
            fertile_signs
        )
    
    # Prepare observations
    observations = {
        "cervical_fluid": latest_entry.cervical_fluid_type,
        "lh_test": latest_entry.lh_test_result,
        "libido": latest_entry.libido_level,
        "mood": latest_entry.mood,
        "energy": latest_entry.energy_level,
        "cycle_day": latest_entry.cycle_day,
        "fertility_window": f"Days {fertility_window.get('start', 0)}-{fertility_window.get('end', 0)}"
    }
    
    # Generate recommendations
    recommendations = []
    if latest_entry.fertility_status == "fertile":
        recommendations.append("Optimal time for intercourse - consider today or tomorrow")
    elif latest_entry.fertility_status == "possibly_fertile":
        recommendations.append("Good time for intercourse - consider every other day")
    elif latest_entry.lh_test_result == "peak":
        recommendations.append("Peak LH detected - ovulation likely in 24-48 hours")
    
    # Create summary text
    summary_text = ExportService.create_cycle_summary_text(
        patient_name=patient.name,
        cycle_day=latest_entry.cycle_day,
        fertility_status=latest_entry.fertility_status,
        fertility_probability=fertility_probability,
        observations=observations,
        recommendations=recommendations if recommendations else None
    )
    
    return {"summary_text": summary_text}


@router.get("/export/emergency-card")
def export_emergency_card(
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Export emergency card"""
    # Get patient info
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Calculate age
    age = None
    if patient.birth_date:
        try:
            birth_date = datetime.strptime(patient.birth_date, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
        except:
            pass
    
    patient_info = {
        "name": patient.name,
        "age": age,
        "email": patient.email
    }
    
    # Get fertility profile
    profile_service = FertilityProfileService(db)
    profile = profile_service.get_profile(patient_id)
    fertility_profile = profile.dict() if profile else {}
    
    # Get latest entry
    entry_service = FertilityEntryService(db)
    entries, _ = entry_service.get_entries(patient_id)
    latest_entry = entries[0].dict() if entries else {}
    
    # Create emergency card text
    card_text = ExportService.create_emergency_card_text(
        patient_info=patient_info,
        fertility_profile=fertility_profile,
        latest_entry=latest_entry
    )
    
    return {"emergency_card_text": card_text}


# Validation Route
@router.post("/validate/entry", response_model=ValidationResult)
def validate_fertility_entry(
    entry_data: FertilityEntryCreate,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Validate fertility entry data"""
    errors = []
    warnings = []
    
    # Check for required fields (if any)
    if not entry_data.submission_date:
        errors.append({"field": "submission_date", "message": "Submission date is required"})
    
    # Validate BBT temperature range
    if entry_data.bbt_temperature is not None:
        if entry_data.bbt_temperature < 35.0 or entry_data.bbt_temperature > 40.0:
            warnings.append("BBT temperature seems abnormal (35-40°C normal range)")
    
    # Check for peak LH without intercourse
    if entry_data.lh_test_result == "peak" and not entry_data.intercourse_today:
        warnings.append("Peak LH detected - consider timing intercourse in next 24-48 hours")
    
    # Check for egg white cervical fluid
    if entry_data.cervical_fluid_type == "egg_white":
        warnings.append("Egg white cervical fluid detected - highly fertile sign")
    
    # Check for high stress
    if entry_data.stress_level in ["high", "very_high"]:
        warnings.append("High stress levels may affect cycle regularity and fertility")
    
    # Check for insufficient sleep
    if entry_data.sleep_hours is not None and entry_data.sleep_hours < 6:
        warnings.append("Insufficient sleep may affect hormone balance and fertility")
    
    # Check for existing entry on same date
    entry_service = FertilityEntryService(db)
    existing_entry = entry_service.get_entry_by_date(patient_id, entry_data.submission_date)
    if existing_entry:
        warnings.append(f"Entry already exists for date {entry_data.submission_date}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


# Health Check Route
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Try to query database
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )




# REMOVED THE RESPONCE ENTRY, DONT FORGET TO PUT IT BACKS

@router.post("/entries", response_model=FertilityEntryResponse)
def create_or_update_fertility_entry(
    entry_data: FertilityEntryCreate,
    patient_id: int = Depends(get_current_patient_id),
    db: Session = Depends(get_db)
):
    """Create or update fertility entry with insights"""
    
    print(f"🔍 [FINAL-ENDPOINT] Processing entry for patient {patient_id}, date {entry_data.submission_date}")
    
    entry_service = FertilityEntryService(db)
    profile_service = FertilityProfileService(db)
    
    # Check if entry exists
    existing_entry = entry_service.get_entry_by_date(patient_id, entry_data.submission_date)
    
    fertility_profile = profile_service.get_profile(patient_id)
    
    if existing_entry:
        # UPDATE
        print(f"🔄 [FINAL] Updating entry {existing_entry.id}")
        
        # Remove patient_id from entry_data if present
        entry_dict = entry_data.dict()
        entry_dict.pop('patient_id', None)
        
        from app.fertility.schemas import FertilityEntryUpdate
        update_data = FertilityEntryUpdate(**entry_dict)
        
        entry = entry_service.update_entry(existing_entry.id, patient_id, update_data)
        action = "updated"
    else:
        # CREATE
        print(f"🆕 [FINAL] Creating new entry")
        entry = entry_service.create_entry(patient_id, entry_data, fertility_profile)
        action = "created"
    
    # ====== GENERATE INSIGHTS ======
    insights = {
        "cycle_summary": {
            "cycle_day": entry.cycle_day or 0,
            "cycle_phase": entry.cycle_phase.value if entry.cycle_phase else "unknown",
            "ovulation_prediction": f"Day {entry.predicted_ovulation_day}" if entry.predicted_ovulation_day else "Unknown",
            "fertility_window": f"Days {entry.fertility_window_start}-{entry.fertility_window_end}" if entry.fertility_window_start else "Unknown",
            "next_period_prediction": None
        },
        "fertility_assessment": {
            "status": entry.fertility_status.value if entry.fertility_status else "infertile",
            "probability": 50,
            "key_indicators": []
        },
        "observations": ["Entry saved successfully"],
        "recommendations": ["Continue tracking daily"],
        "next_steps": ["Check again tomorrow"]
    }
    
    # Add ovulation alert if LH test is PEAK
    if entry.lh_test_result == LHTestResult.PEAK:
        insights["ovulation_alert"] = {
            "message": "🚨 PEAK LH DETECTED!",
            "detail": "Ovulation likely in 24-48 hours",
            "urgency": "high",
            "action": "Optimal time for intercourse"
        }
    
    if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
        insights["fertility_alert"] = {
            "message": "🥚 Egg White Cervical Fluid",
            "detail": "Highly fertile sign - peak fertility window",
            "urgency": "medium"
        }
    
    # Get patient name
    patient_service = PatientService(db)
    patient = patient_service.get_patient(patient_id)
    
    # Create response - CONVERT ALL DATETIME TO STRING
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "entry": {
                "id": entry.id,
                "patient_id": entry.patient_id,
                "patient_name": patient.name if patient else "Unknown",
                "cycle_day": entry.cycle_day or 0,
                "predicted_ovulation_day": entry.predicted_ovulation_day or 0,
                "fertility_window_start": entry.fertility_window_start or 0,
                "fertility_window_end": entry.fertility_window_end or 0,
                "fertility_status": entry.fertility_status.value if entry.fertility_status else "infertile",
                "cycle_phase": entry.cycle_phase.value if entry.cycle_phase else None,
                "bbt_temperature": entry.bbt_temperature,
                "lh_test_result": entry.lh_test_result.value if entry.lh_test_result else None,
                "submission_date": entry.submission_date,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,  # FIXED
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,  # FIXED
                # Add other required fields with proper defaults
                "bbt_time": entry.bbt_time,
                "bbt_notes": entry.bbt_notes,
                "cervical_fluid_type": entry.cervical_fluid_type.value if entry.cervical_fluid_type else None,
                "cervical_fluid_amount": entry.cervical_fluid_amount.value if entry.cervical_fluid_amount else None,
                "cervical_fluid_color": entry.cervical_fluid_color,
                "cervical_position": entry.cervical_position.value if entry.cervical_position else None,
                "cervical_firmness": entry.cervical_firmness.value if entry.cervical_firmness else None,
                "cervical_opening": entry.cervical_opening.value if entry.cervical_opening else None,
                "lh_test_time": entry.lh_test_time,
                "lh_test_brand": entry.lh_test_brand,
                "menstrual_flow": entry.menstrual_flow.value if entry.menstrual_flow else None,
                "menstrual_color": entry.menstrual_color,
                "menstrual_cramps": entry.menstrual_cramps.value if entry.menstrual_cramps else None,
                "libido_level": entry.libido_level.value if entry.libido_level else None,
                "breast_tenderness": entry.breast_tenderness.value if entry.breast_tenderness else None,
                "ovulation_pain": entry.ovulation_pain or False,
                "ovulation_pain_side": entry.ovulation_pain_side,
                "bloating": entry.bloating.value if entry.bloating else None,
                "mood": entry.mood.value if entry.mood else None,
                "energy_level": entry.energy_level.value if entry.energy_level else None,
                "intercourse_today": entry.intercourse_today or False,
                "intercourse_time": entry.intercourse_time,
                "intercourse_position": entry.intercourse_position.value if entry.intercourse_position else None,
                "contraception_used": entry.contraception_used.value if entry.contraception_used else None,
                "weight": entry.weight,
                "resting_heart_rate": entry.resting_heart_rate,
                "sleep_hours": entry.sleep_hours,
                "stress_level": entry.stress_level.value if entry.stress_level else None,
                "medications": entry.medications,
                "additional_notes": entry.additional_notes,
            },
            "insights": insights,
            "success": True,
            "message": f"Fertility entry {action} with analysis",
            "action": action,
            "entry_id": entry.id
        }
    )
















































# ====== HELPER FUNCTIONS ======
def calculate_fertility_probability(entry):
    """Calculate fertility probability 0-100%"""
    probability = 0
    
    # Base from cycle position
    if entry.fertility_window_start <= entry.cycle_day <= entry.fertility_window_end:
        window_length = entry.fertility_window_end - entry.fertility_window_start
        position = entry.cycle_day - entry.fertility_window_start
        probability = (position / window_length) * 80 if window_length > 0 else 50
    
    # Boost from symptoms
    if entry.lh_test_result == LHTestResult.PEAK:
        probability = min(95, probability + 30)
    elif entry.lh_test_result == LHTestResult.HIGH:
        probability = min(90, probability + 20)
    
    if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
        probability = min(95, probability + 25)
    elif entry.cervical_fluid_type == CervicalFluidType.WATERY:
        probability = min(85, probability + 15)
    
    if entry.libido_level in [LibidoLevel.HIGH, LibidoLevel.VERY_HIGH]:
        probability = min(90, probability + 10)
    
    return round(probability)


def extract_key_indicators(entry):
    """Extract key fertility indicators"""
    indicators = []
    
    if entry.lh_test_result == LHTestResult.PEAK:
        indicators.append("✅ Peak LH - Ovulation imminent")
    elif entry.lh_test_result == LHTestResult.HIGH:
        indicators.append("📈 High LH - Approaching ovulation")
    
    if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
        indicators.append("🥚 Egg white cervical fluid - Peak fertility")
    elif entry.cervical_fluid_type == CervicalFluidType.WATERY:
        indicators.append("💧 Watery cervical fluid - Fertile")
    
    if entry.cervical_position == CervicalPosition.HIGH and entry.cervical_firmness == CervicalFirmness.SOFT:
        indicators.append("📈 High, soft cervix - Fertile sign")
    
    if entry.libido_level in [LibidoLevel.HIGH, LibidoLevel.VERY_HIGH]:
        indicators.append("❤️ High libido - Fertility correlate")
    
    return indicators


def generate_observations(entry):
    """Generate human-readable observations"""
    observations = []
    
    # BBT observations
    if entry.bbt_temperature:
        observations.append(f"🌡️ BBT: {entry.bbt_temperature}°C at {entry.bbt_time or 'morning'}")
    
    # Cervical fluid observations
    if entry.cervical_fluid_type and entry.cervical_fluid_type != 'dry':
        fluid_desc = entry.cervical_fluid_type.replace('_', ' ').title()
        amount_desc = entry.cervical_fluid_amount.replace('_', ' ').title() if entry.cervical_fluid_amount else ""
        observations.append(f"💧 Cervical fluid: {fluid_desc} ({amount_desc})")
    
    # LH test observations
    if entry.lh_test_result and entry.lh_test_result != 'negative':
        lh_desc = entry.lh_test_result.replace('_', ' ').title()
        observations.append(f"🧪 LH test: {lh_desc}")
    
    # Symptom observations
    if entry.ovulation_pain:
        side = entry.ovulation_pain_side.replace('_', ' ').title() if entry.ovulation_pain_side else "one side"
        observations.append(f"⚡ Ovulation pain: {side}")
    
    if entry.breast_tenderness and entry.breast_tenderness != 'none':
        tenderness = entry.breast_tenderness.replace('_', ' ').title()
        observations.append(f"👙 Breast tenderness: {tenderness}")
    
    return observations


def generate_recommendations(entry, profile):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Based on fertility status
    if entry.fertility_status == FertilityStatus.FERTILE:
        recommendations.append("🎯 **Optimal timing**: Intercourse today or tomorrow")
        recommendations.append("⏰ **Test timing**: LH test tomorrow to confirm ovulation")
    
    elif entry.fertility_status == FertilityStatus.POSSIBLY_FERTILE:
        recommendations.append("📅 **Timing**: Intercourse every other day")
        recommendations.append("🔍 **Monitoring**: Check cervical fluid 2-3 times daily")
    
    # Specific test-based recommendations
    if entry.lh_test_result == LHTestResult.PEAK:
        recommendations.append("🚨 **Urgent**: Highest chance of conception in next 24 hours")
        recommendations.append("💑 **Action**: Plan intercourse within 12-36 hours")
    
    elif entry.lh_test_result == LHTestResult.HIGH:
        recommendations.append("📊 **Testing**: LH test twice daily until peak detected")
    
    # Cervical fluid based
    if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
        recommendations.append("🥚 **Observation**: Egg white fluid typically lasts 1-3 days")
    
    # Cycle phase recommendations
    if entry.cycle_day >= 8 and entry.cycle_day <= 14:
        recommendations.append("📈 **Window opening**: Start daily LH testing")
    
    elif entry.cycle_day > 16 and entry.lh_test_result == LHTestResult.PEAK:
        recommendations.append("📉 **Post-ovulation**: Continue BBT to confirm temp rise")
        recommendations.append("⏳ **Waiting**: Pregnancy test in 10-14 days if period late")
    
    # Trying to conceive specific
    if profile and profile.trying_to_conceive:
        recommendations.append("💑 **TTC**: Maintain intercourse every other day in fertile window")
        recommendations.append("🧘 **Wellness**: Reduce stress, maintain healthy sleep")
    
    return recommendations


def generate_next_steps(entry):
    """Generate next steps for user"""
    next_steps = []
    
    # Immediate next steps
    next_steps.append("✅ **Today**: Record any changes in symptoms")
    
    # Tomorrow's steps
    if entry.cycle_day >= 8 and entry.cycle_day <= 16:
        next_steps.append("📅 **Tomorrow**: Take morning BBT, check cervical fluid")
        if entry.lh_test_result != LHTestResult.PEAK:
            next_steps.append("🧪 **Tomorrow**: LH test with second morning urine")
    
    # Cycle-based next steps
    if entry.cycle_day < 7:
        next_steps.append("📊 **This week**: Track period flow changes")
    elif entry.cycle_day < 14:
        next_steps.append("🔍 **This week**: Watch for fertile cervical fluid")
    elif entry.cycle_day < 21:
        next_steps.append("🌡️ **This week**: Monitor BBT for post-ovulation rise")
    
    return next_steps


def entry_to_dict(entry):
    """Convert SQLAlchemy entry to dictionary"""
    return {
        "id": entry.id,
        "cycle_day": entry.cycle_day,
        "fertility_status": entry.fertility_status.value,
        "cervical_fluid_type": entry.cervical_fluid_type.value if entry.cervical_fluid_type else None,
        "lh_test_result": entry.lh_test_result.value if entry.lh_test_result else None,
        "bbt_temperature": entry.bbt_temperature,
        "submission_date": entry.submission_date,
        # Add other fields as needed
    }




# Main router inclusion
def include_fertility_routes(app):
    """Include all fertility routes in the FastAPI app"""
    app.include_router(router, prefix="/api/fertility", tags=["Fertility"])