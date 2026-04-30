from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from typing_extensions import Literal


# Base Schemas
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# Enums for Pydantic
class CervicalFluidType(str, Enum):
    DRY = "dry"
    STICKY = "sticky"
    CREAMY = "creamy"
    WATERY = "watery"
    EGG_WHITE = "egg_white"
    BLOODY = "bloody"


class CervicalFluidAmount(str, Enum):
    NONE = "none"
    SCANT = "scant"
    MODERATE = "moderate"
    ABUNDANT = "abundant"


class CervicalPosition(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CervicalFirmness(str, Enum):
    FIRM = "firm"
    MEDIUM = "medium"
    SOFT = "soft"


class CervicalOpening(str, Enum):
    CLOSED = "closed"
    PARTIALLY_OPEN = "partially_open"
    OPEN = "open"


class LHTestResult(str, Enum):
    NEGATIVE = "negative"
    LOW = "low"
    HIGH = "high"
    PEAK = "peak"


class MenstrualFlow(str, Enum):
    SPOTTING = "spotting"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    VERY_HEAVY = "very_heavy"


class MoodLevel(str, Enum):
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "very_sad"
    ANXIOUS = "anxious"


class EnergyLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


class StressLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class LibidoLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SymptomSeverity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class FertilityStatus(str, Enum):
    FERTILE = "fertile"
    POSSIBLY_FERTILE = "possibly_fertile"
    INFERTILE = "infertile"
    POST_OVULATION = "post_ovulation"


class IntercoursePosition(str, Enum):
    MISSIONARY = "missionary"
    DOGGY = "doggy"
    COWGIRL = "cowgirl"
    SPOONING = "spooning"
    OTHER = "other"


class ContraceptionType(str, Enum):
    NONE = "none"
    CONDOM = "condom"
    PULL_OUT = "pull_out"
    OTHER = "other"


class CyclePhase(str, Enum):
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATION = "ovulation"
    LUTEAL = "luteal"


# Request Schemas
class MedicationsSchema(BaseModel):
    prenatal: bool = Field(default=False)
    folic_acid: bool = Field(default=False)
    progesterone: bool = Field(default=False)
    clomid: bool = Field(default=False)
    letrozole: bool = Field(default=False)
    metformin: bool = Field(default=False)
    other: Optional[str] = Field(default=None)


class FertilityEntryCreate(BaseSchema):
    # Core Tracking Data
    bbt_temperature: Optional[float] = Field(None, ge=35.0, le=45.0)
    bbt_time: Optional[str] = None
    bbt_notes: Optional[str] = None
    
    # Cervical Observations
    cervical_fluid_type: Optional[CervicalFluidType] = None
    cervical_fluid_amount: Optional[CervicalFluidAmount] = None
    cervical_fluid_color: Optional[str] = None
    
    # Cervical Position
    cervical_position: Optional[CervicalPosition] = None
    cervical_firmness: Optional[CervicalFirmness] = None
    cervical_opening: Optional[CervicalOpening] = None
    
    # LH Testing
    lh_test_result: Optional[LHTestResult] = None
    lh_test_time: Optional[str] = None
    lh_test_brand: Optional[str] = None
    
    # Menstrual Tracking
    menstrual_flow: Optional[MenstrualFlow] = None
    menstrual_color: Optional[str] = None
    menstrual_cramps: Optional[SymptomSeverity] = None
    
    # Symptoms
    libido_level: Optional[LibidoLevel] = None
    breast_tenderness: Optional[SymptomSeverity] = None
    ovulation_pain: bool = False
    ovulation_pain_side: Optional[str] = None
    bloating: Optional[SymptomSeverity] = None
    mood: Optional[MoodLevel] = None
    energy_level: Optional[EnergyLevel] = None
    
    # Intercourse
    intercourse_today: bool = False
    intercourse_time: Optional[str] = None
    intercourse_position: Optional[IntercoursePosition] = None
    contraception_used: Optional[ContraceptionType] = None
    
    # Health Metrics
    weight: Optional[float] = Field(None, ge=30, le=200)
    resting_heart_rate: Optional[int] = Field(None, ge=40, le=120)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    stress_level: Optional[StressLevel] = None
    
    # Medications
    medications: Optional[MedicationsSchema] = Field(default_factory=MedicationsSchema)
    
    # Additional Notes
    additional_notes: Optional[str] = None
    
    # Metadata
    submission_date: str  # YYYY-MM-DD format
    
    @validator('submission_date')
    def validate_submission_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('submission_date must be in YYYY-MM-DD format')


class FertilityEntryUpdate(BaseSchema):
    # All fields from create but optional
    bbt_temperature: Optional[float] = Field(None, ge=35.0, le=45.0)
    bbt_time: Optional[str] = None
    bbt_notes: Optional[str] = None
    cervical_fluid_type: Optional[CervicalFluidType] = None
    cervical_fluid_amount: Optional[CervicalFluidAmount] = None
    cervical_fluid_color: Optional[str] = None
    cervical_position: Optional[CervicalPosition] = None
    cervical_firmness: Optional[CervicalFirmness] = None
    cervical_opening: Optional[CervicalOpening] = None
    lh_test_result: Optional[LHTestResult] = None
    lh_test_time: Optional[str] = None
    lh_test_brand: Optional[str] = None
    menstrual_flow: Optional[MenstrualFlow] = None
    menstrual_color: Optional[str] = None
    menstrual_cramps: Optional[SymptomSeverity] = None
    libido_level: Optional[LibidoLevel] = None
    breast_tenderness: Optional[SymptomSeverity] = None
    ovulation_pain: Optional[bool] = None
    ovulation_pain_side: Optional[str] = None
    bloating: Optional[SymptomSeverity] = None
    mood: Optional[MoodLevel] = None
    energy_level: Optional[EnergyLevel] = None
    intercourse_today: Optional[bool] = None
    intercourse_time: Optional[str] = None
    intercourse_position: Optional[IntercoursePosition] = None
    contraception_used: Optional[ContraceptionType] = None
    weight: Optional[float] = Field(None, ge=30, le=200)
    resting_heart_rate: Optional[int] = Field(None, ge=40, le=120)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    stress_level: Optional[StressLevel] = None
    medications: Optional[MedicationsSchema] = None
    additional_notes: Optional[str] = None


class FertilityProfileCreate(BaseSchema):
    # Cycle Information
    cycle_length: int = Field(28, ge=21, le=45)
    period_length: int = Field(5, ge=1, le=14)
    last_period_date: Optional[str] = None  # YYYY-MM-DD format
    # ============ ADD THIS LINE ============
    period_dates: Optional[List[str]] = Field(default_factory=list)  # List of dates
    # =======================================
    typical_cycle_pattern: str = Field("regular", pattern="^(regular|irregular|unknown)$")
    
    
    # Fertility Goals
    trying_to_conceive: bool = False
    fertility_issues: List[str] = Field(default_factory=list)
    
    # Medical History
    known_conditions: List[str] = Field(default_factory=list)
    medications_history: List[str] = Field(default_factory=list)
    
    # Pregnancy History
    previous_pregnancies: int = Field(0, ge=0)
    previous_births: int = Field(0, ge=0)
    previous_miscarriages: int = Field(0, ge=0)
    
    # Partner Information
    partner_age: Optional[int] = Field(None, ge=18, le=70)
    partner_fertility_issues: List[str] = Field(default_factory=list)
    
    # Risk Factors
    high_risk: bool = False
    
    @validator('last_period_date')
    def validate_last_period_date(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('last_period_date must be in YYYY-MM-DD format')

            # ============ ADD THIS VALIDATOR ============
    @validator('period_dates')
    def validate_period_dates(cls, v):
        if v is None:
            return []
        for date_str in v:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f'Invalid date format in period_dates: {date_str}. Use YYYY-MM-DD')
        return v
    # ============================================






class FertilityProfileUpdate(BaseSchema):
    cycle_length: Optional[int] = Field(None, ge=21, le=45)
    period_length: Optional[int] = Field(None, ge=1, le=14)
    last_period_date: Optional[str] = None
    # ============ ADD THIS LINE ============
    period_dates: Optional[List[str]] = None  # Can be null for updates
    # =======================================
    typical_cycle_pattern: Optional[str] = Field(None, pattern="^(regular|irregular|unknown)$")
    trying_to_conceive: Optional[bool] = None
    fertility_issues: Optional[List[str]] = None
    known_conditions: Optional[List[str]] = None
    medications_history: Optional[List[str]] = None
    previous_pregnancies: Optional[int] = Field(None, ge=0)
    previous_births: Optional[int] = Field(None, ge=0)
    previous_miscarriages: Optional[int] = Field(None, ge=0)
    partner_age: Optional[int] = Field(None, ge=18, le=70)
    partner_fertility_issues: Optional[List[str]] = None
    high_risk: Optional[bool] = None


class PatientCreate(BaseSchema):
    user_id: str
    name: str
    email: str
    birth_date: Optional[str] = None
    phone_number: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class CycleAnalysisCreate(BaseSchema):
    cycle_number: int
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None


# Response Schemas
class FertilityEntryResponse(BaseSchema):
    id: int
    patient_id: int
    patient_name: str
    
    # Cycle Information
    cycle_day: int
    predicted_ovulation_day: int
    fertility_window_start: int
    fertility_window_end: int
    fertility_status: FertilityStatus
    cycle_phase: Optional[CyclePhase]
    
    # Tracking Data
    bbt_temperature: Optional[float]
    bbt_time: Optional[str]
    bbt_notes: Optional[str]
    cervical_fluid_type: Optional[CervicalFluidType]
    cervical_fluid_amount: Optional[CervicalFluidAmount]
    cervical_fluid_color: Optional[str]
    cervical_position: Optional[CervicalPosition]
    cervical_firmness: Optional[CervicalFirmness]
    cervical_opening: Optional[CervicalOpening]
    lh_test_result: Optional[LHTestResult]
    lh_test_time: Optional[str]
    lh_test_brand: Optional[str]
    menstrual_flow: Optional[MenstrualFlow]
    menstrual_color: Optional[str]
    menstrual_cramps: Optional[SymptomSeverity]
    libido_level: Optional[LibidoLevel]
    breast_tenderness: Optional[SymptomSeverity]
    ovulation_pain: bool
    ovulation_pain_side: Optional[str]
    bloating: Optional[SymptomSeverity]
    mood: Optional[MoodLevel]
    energy_level: Optional[EnergyLevel]
    intercourse_today: bool
    intercourse_time: Optional[str]
    intercourse_position: Optional[IntercoursePosition]
    contraception_used: Optional[ContraceptionType]
    weight: Optional[float]
    resting_heart_rate: Optional[int]
    sleep_hours: Optional[float]
    stress_level: Optional[StressLevel]
    medications: Optional[Dict[str, Any]]
    additional_notes: Optional[str]
    
    # Metadata
    submission_date: str
    submitted_at: datetime
    updated_at: Optional[datetime]


class FertilityProfileResponse(BaseSchema):
    id: int
    patient_id: int
    
    # Cycle Information
    cycle_length: int
    period_length: int
    last_period_date: Optional[str]
    # ============ ADD THIS LINE ============
    period_dates: Optional[List[str]]  # This is now required in response
    # =======================================
    typical_cycle_pattern: str
    
    # Fertility Goals
    trying_to_conceive: bool
    fertility_issues: List[str]
    
    # Medical History
    known_conditions: List[str]
    medications_history: List[str]
    
    # Pregnancy History
    previous_pregnancies: int
    previous_births: int
    previous_miscarriages: int
    
    # Partner Information
    partner_age: Optional[int]
    partner_fertility_issues: List[str]
    
    # Risk Factors
    high_risk: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]


class PatientResponse(BaseSchema):
    id: int
    user_id: str
    name: str
    email: str
    birth_date: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    fertility_profile: Optional[FertilityProfileResponse]


class CycleAnalysisResponse(BaseSchema):
    id: int
    patient_id: int
    cycle_number: int
    start_date: str
    end_date: Optional[str]
    
    # Analysis Results
    cycle_length: Optional[int]
    ovulation_day: Optional[int]
    luteal_phase_length: Optional[int]
    bbt_shift_detected: bool
    ovulation_confirmed: bool
    
    # Statistics
    average_bbt_pre_ovulation: Optional[float]
    average_bbt_post_ovulation: Optional[float]
    bbt_shift_amount: Optional[float]
    
    # Symptoms Analysis
    symptoms_summary: Dict[str, Any]
    
    # Fertility Insights
    fertile_window: Dict[str, Any]
    peak_fertility_day: Optional[int]
    
    # Timestamps
    analyzed_at: datetime
    updated_at: Optional[datetime]


class FertilityInsightResponse(BaseSchema):
    id: int
    patient_id: int
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]
    confidence_score: Optional[float]
    is_actionable: bool
    is_archived: bool
    generated_at: datetime
    expires_at: Optional[datetime]


# Pagination and Filter Schemas
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class FertilityEntryFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cycle_day_min: Optional[int] = Field(None, ge=1, le=45)
    cycle_day_max: Optional[int] = Field(None, ge=1, le=45)
    fertility_status: Optional[FertilityStatus] = None
    cycle_phase: Optional[CyclePhase] = None
    lh_test_result: Optional[LHTestResult] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Analysis and Report Schemas
class CycleSummaryRequest(BaseModel):
    cycle_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CycleSummaryResponse(BaseSchema):
    patient_id: int
    patient_name: str
    cycle_number: int
    start_date: str
    end_date: Optional[str]
    cycle_length: Optional[int]
    average_cycle_length: Optional[float]
    ovulation_day: Optional[int]
    luteal_phase_length: Optional[int]
    fertile_window: Dict[str, Any]
    bbt_pattern: Dict[str, Any]
    symptom_patterns: Dict[str, Any]
    fertility_score: float
    recommendations: List[str]
    next_period_prediction: Optional[str]
    next_fertile_window: Optional[Dict[str, Any]]


class DoctorVisitSummaryRequest(BaseModel):
    timeframe: str = Field("cycle", pattern="^(cycle|month|three_months)$")
    include_symptoms: bool = True
    include_bbt: bool = True
    include_medications: bool = True


class DoctorVisitSummaryResponse(BaseSchema):
    patient_id: int
    patient_name: str
    generated_date: str
    timeframe: str
    cycles_analyzed: int
    
    # Patient Information
    patient_info: Dict[str, Any]
    fertility_profile: Dict[str, Any]
    
    # Cycle Analysis
    cycle_statistics: Dict[str, Any]
    ovulation_patterns: Dict[str, Any]
    cycle_regularity: Dict[str, Any]
    
    # Symptoms Analysis
    symptoms_summary: Dict[str, Any]
    
    # BBT Analysis
    bbt_analysis: Optional[Dict[str, Any]]
    
    # Medications Summary
    medications_summary: Optional[Dict[str, Any]]
    
    # Concerns and Recommendations
    potential_concerns: List[str]
    doctor_questions: List[str]
    recommendations: List[str]


class PartnerUpdateRequest(BaseModel):
    include_details: bool = True
    include_recommendations: bool = True


class PartnerUpdateResponse(BaseSchema):
    patient_name: str
    cycle_day: int
    fertility_status: FertilityStatus
    fertility_probability: float
    observations: Dict[str, Any]
    recommendations: Optional[List[str]]
    generated_at: datetime


# Validation Response Schema
class ValidationError(BaseModel):
    field: str
    message: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]