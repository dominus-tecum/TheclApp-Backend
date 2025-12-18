from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import json
from fastapi import HTTPException, status
import math

from app.fertility.models import (
    FertilityEntry, FertilityProfile, Patient, CycleAnalysis, FertilityInsight,
    CervicalFluidType, LHTestResult, FertilityStatus, CyclePhase,
    SymptomSeverity, LibidoLevel, MoodLevel, EnergyLevel, StressLevel
)
from app.fertility.schemas import (

    FertilityEntryCreate, FertilityEntryUpdate, FertilityProfileCreate,
    FertilityProfileUpdate, PatientCreate, CycleAnalysisCreate,
    FertilityEntryFilter, PaginationParams
)


class FertilityCycleCalculator:
    """Service for calculating fertility cycle information"""
    
    @staticmethod
    def calculate_cycle_day(last_period_date: str, current_date: date = None) -> int:
        """Calculate current cycle day based on last period date"""
        if not last_period_date:
            return 0
        
        if current_date is None:
            current_date = date.today()
        
        last_period = datetime.strptime(last_period_date, '%Y-%m-%d').date()
        diff_days = (current_date - last_period).days + 1
        return max(1, diff_days)
    
    @staticmethod
    def calculate_predicted_ovulation(cycle_length: int) -> int:
        """Calculate predicted ovulation day"""
        return max(1, cycle_length - 14)
    
    @staticmethod
    def calculate_fertility_window(cycle_length: int) -> Dict[str, int]:
        """Calculate fertility window"""
        ovulation_day = FertilityCycleCalculator.calculate_predicted_ovulation(cycle_length)
        return {
            "start": max(1, ovulation_day - 5),
            "end": min(cycle_length, ovulation_day + 1)
        }
    
    @staticmethod
    def get_cycle_phase(cycle_day: int, cycle_length: int) -> CyclePhase:
        """Determine current cycle phase"""
        if cycle_day <= 5:
            return CyclePhase.MENSTRUAL
        elif cycle_day <= 13:
            return CyclePhase.FOLLICULAR
        elif cycle_day <= 16:
            return CyclePhase.OVULATION
        else:
            return CyclePhase.LUTEAL
    
    @staticmethod
    def calculate_fertility_probability(
        cycle_day: int,
        fertility_window: Dict[str, int],
        fertile_signs_count: int
    ) -> float:
        """Calculate fertility probability based on cycle day and signs"""
        if cycle_day < fertility_window["start"] or cycle_day > fertility_window["end"]:
            base_probability = 0
        else:
            window_length = fertility_window["end"] - fertility_window["start"]
            position_in_window = cycle_day - fertility_window["start"]
            base_probability = (position_in_window / max(1, window_length)) * 90
        
        # Adjust based on fertile signs
        adjusted_probability = base_probability + (fertile_signs_count * 10)
        return min(95, max(0, adjusted_probability))


class FertilityEntryService:
    """Service for managing fertility entries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_entry(
        self,
        patient_id: int,
        entry_data: FertilityEntryCreate,
        fertility_profile: Optional[FertilityProfile] = None
    ) -> FertilityEntry:
        """Create a new fertility entry"""
        
        
        # Get patient info
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        



        # Calculate cycle information
        cycle_day = 0
        predicted_ovulation_day = 0
        fertility_window = {"start": 0, "end": 0}
        cycle_phase = None
        
        if fertility_profile and fertility_profile.last_period_date:
            calculator = FertilityCycleCalculator()
            submission_date = datetime.strptime(entry_data.submission_date, '%Y-%m-%d').date()
            cycle_day = calculator.calculate_cycle_day(
                fertility_profile.last_period_date,
                submission_date
            )
            predicted_ovulation_day = calculator.calculate_predicted_ovulation(
                fertility_profile.cycle_length
            )
            fertility_window = calculator.calculate_fertility_window(
                fertility_profile.cycle_length
            )
            cycle_phase = calculator.get_cycle_phase(cycle_day, fertility_profile.cycle_length)
        
        # Determine fertility status
        fertility_status = self._determine_fertility_status(entry_data, cycle_day)
        
        # Create entry
        db_entry = FertilityEntry(
            patient_id=patient_id,
            patient_name=patient.name,
            cycle_day=cycle_day,
            predicted_ovulation_day=predicted_ovulation_day,
            fertility_window_start=fertility_window.get("start", 0),
            fertility_window_end=fertility_window.get("end", 0),
            fertility_status=fertility_status,
            cycle_phase=cycle_phase,
            **entry_data.dict(exclude_none=True)
        )
        
        # Handle medications
        if entry_data.medications:
            db_entry.medications = entry_data.medications.dict()
        
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        
        # Generate insights if fertile signs detected
        self._generate_insights(db_entry, fertility_profile)
        
        return db_entry
    
    def update_entry(
        self,
        entry_id: int,
        patient_id: int,
        update_data: FertilityEntryUpdate
    ) -> FertilityEntry:
        """Update an existing fertility entry"""
        entry = self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.id == entry_id,
                FertilityEntry.patient_id == patient_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fertility entry not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_none=True)
        if 'medications' in update_dict:
            entry.medications = update_dict['medications']
            del update_dict['medications']
        
        for field, value in update_dict.items():
            setattr(entry, field, value)
        
        # Recalculate fertility status
        fertility_profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        if fertility_profile:
            calculator = FertilityCycleCalculator()
            if fertility_profile.last_period_date:
                submission_date = datetime.strptime(entry.submission_date, '%Y-%m-%d').date()
                entry.cycle_day = calculator.calculate_cycle_day(
                    fertility_profile.last_period_date,
                    submission_date
                )
                entry.predicted_ovulation_day = calculator.calculate_predicted_ovulation(
                    fertility_profile.cycle_length
                )
                fertility_window = calculator.calculate_fertility_window(
                    fertility_profile.cycle_length
                )
                entry.fertility_window_start = fertility_window["start"]
                entry.fertility_window_end = fertility_window["end"]
                entry.cycle_phase = calculator.get_cycle_phase(
                    entry.cycle_day,
                    fertility_profile.cycle_length
                )
        
        entry.fertility_status = self._determine_fertility_status_from_db(entry)
        
        entry.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def get_entry(self, entry_id: int, patient_id: int) -> FertilityEntry:
        """Get a specific fertility entry"""
        entry = self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.id == entry_id,
                FertilityEntry.patient_id == patient_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fertility entry not found"
            )
        
        return entry
    
    def get_entries(
        self,
        patient_id: int,
        filters: Optional[FertilityEntryFilter] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[FertilityEntry], int]:
        """Get fertility entries with filtering and pagination"""
        query = self.db.query(FertilityEntry).filter(
            FertilityEntry.patient_id == patient_id
        )
        
        # Apply filters
        if filters:
            if filters.start_date:
                query = query.filter(FertilityEntry.submission_date >= filters.start_date)
            if filters.end_date:
                query = query.filter(FertilityEntry.submission_date <= filters.end_date)
            if filters.cycle_day_min:
                query = query.filter(FertilityEntry.cycle_day >= filters.cycle_day_min)
            if filters.cycle_day_max:
                query = query.filter(FertilityEntry.cycle_day <= filters.cycle_day_max)
            if filters.fertility_status:
                query = query.filter(FertilityEntry.fertility_status == filters.fertility_status)
            if filters.cycle_phase:
                query = query.filter(FertilityEntry.cycle_phase == filters.cycle_phase)
            if filters.lh_test_result:
                query = query.filter(FertilityEntry.lh_test_result == filters.lh_test_result)
        
        # Count total
        total = query.count()
        
        # Apply pagination
        if pagination:
            offset = (pagination.page - 1) * pagination.page_size
            query = query.order_by(FertilityEntry.submission_date.desc())
            query = query.offset(offset).limit(pagination.page_size)
        else:
            query = query.order_by(FertilityEntry.submission_date.desc())
        
        entries = query.all()
        return entries, total
    
    def get_entry_by_date(self, patient_id: int, date_str: str) -> Optional[FertilityEntry]:
        """Get fertility entry by date"""
        return self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.patient_id == patient_id,
                FertilityEntry.submission_date == date_str
            )
        ).first()
    
    def delete_entry(self, entry_id: int, patient_id: int) -> bool:
        """Delete a fertility entry"""
        entry = self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.id == entry_id,
                FertilityEntry.patient_id == patient_id
            )
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fertility entry not found"
            )
        
        self.db.delete(entry)
        self.db.commit()
        return True
    
    def get_cycle_entries(self, patient_id: int, cycle_number: int) -> List[FertilityEntry]:
        """Get all entries for a specific cycle"""
        # This is a simplified implementation
        # In a real app, you'd need to determine cycle boundaries
        entries = self.db.query(FertilityEntry).filter(
            FertilityEntry.patient_id == patient_id
        ).order_by(FertilityEntry.submission_date).all()
        
        # Group by cycle (simplified)
        cycles = {}
        current_cycle = 1
        for entry in entries:
            if entry.cycle_day == 1:
                current_cycle += 1
            if current_cycle == cycle_number:
                cycles.setdefault(current_cycle, []).append(entry)
        
        return cycles.get(cycle_number, [])
    
    def _determine_fertility_status(
        self,
        entry_data: FertilityEntryCreate,
        cycle_day: int
    ) -> FertilityStatus:
        """Determine fertility status from entry data"""
        # Count fertile signs
        fertile_signs = 0
        
        # Check cervical fluid
        if entry_data.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
            fertile_signs += 2
        elif entry_data.cervical_fluid_type in [CervicalFluidType.WATERY, CervicalFluidType.CREAMY]:
            fertile_signs += 1
        
        # Check LH test
        if entry_data.lh_test_result == LHTestResult.PEAK:
            fertile_signs += 2
        elif entry_data.lh_test_result == LHTestResult.HIGH:
            fertile_signs += 1
        
        # Check other signs
        if entry_data.libido_level in [LibidoLevel.HIGH, LibidoLevel.VERY_HIGH]:
            fertile_signs += 1
        
        # Determine status based on signs
        if fertile_signs >= 3:
            return FertilityStatus.FERTILE
        elif fertile_signs >= 2:
            return FertilityStatus.POSSIBLY_FERTILE
        elif cycle_day > 16:  # Post-ovulation phase
            return FertilityStatus.POST_OVULATION
        else:
            return FertilityStatus.INFERTILE
    
    def _determine_fertility_status_from_db(self, entry: FertilityEntry) -> FertilityStatus:
        """Determine fertility status from database entry"""
        fertile_signs = 0
        
        # Check cervical fluid
        if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
            fertile_signs += 2
        elif entry.cervical_fluid_type in [CervicalFluidType.WATERY, CervicalFluidType.CREAMY]:
            fertile_signs += 1
        
        # Check LH test
        if entry.lh_test_result == LHTestResult.PEAK:
            fertile_signs += 2
        elif entry.lh_test_result == LHTestResult.HIGH:
            fertile_signs += 1
        
        # Check other signs
        if entry.libido_level in [LibidoLevel.HIGH, LibidoLevel.VERY_HIGH]:
            fertile_signs += 1
        
        # Determine status based on signs
        if fertile_signs >= 3:
            return FertilityStatus.FERTILE
        elif fertile_signs >= 2:
            return FertilityStatus.POSSIBLY_FERTILE
        elif entry.cycle_day > 16:  # Post-ovulation phase
            return FertilityStatus.POST_OVULATION
        else:
            return FertilityStatus.INFERTILE
    
    def _generate_insights(
        self,
        entry: FertilityEntry,
        fertility_profile: Optional[FertilityProfile] = None
    ):
        """Generate insights based on entry data"""
        insights = []
        
        # Insight for peak LH test
        if entry.lh_test_result == LHTestResult.PEAK:
            insights.append({
                "type": "ovulation",
                "title": "Peak LH Detected",
                "description": "Ovulation is likely to occur in the next 24-48 hours.",
                "data": {"lh_result": "peak", "test_time": entry.lh_test_time},
                "confidence_score": 0.9,
                "is_actionable": True
            })
        
        # Insight for egg white cervical fluid
        if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
            insights.append({
                "type": "fertility_sign",
                "title": "Highly Fertile Cervical Fluid",
                "description": "Egg white cervical fluid indicates peak fertility.",
                "data": {"fluid_type": "egg_white", "amount": entry.cervical_fluid_amount},
                "confidence_score": 0.85,
                "is_actionable": True
            })
        
        # Insight for high libido
        if entry.libido_level in [LibidoLevel.HIGH, LibidoLevel.VERY_HIGH]:
            insights.append({
                "type": "symptom_pattern",
                "title": "Increased Libido",
                "description": "High libido often coincides with fertile window.",
                "data": {"libido_level": entry.libido_level},
                "confidence_score": 0.7,
                "is_actionable": False
            })
        
        # Save insights
        for insight_data in insights:
            insight = FertilityInsight(
                patient_id=entry.patient_id,
                insight_type=insight_data["type"],
                title=insight_data["title"],
                description=insight_data["description"],
                data=insight_data["data"],
                confidence_score=insight_data.get("confidence_score"),
                is_actionable=insight_data.get("is_actionable", False)
            )
            self.db.add(insight)
        
        if insights:
            self.db.commit()


class FertilityProfileService:
    """Service for managing fertility profiles"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_profile(
        self,
        patient_id: int,
        profile_data: FertilityProfileCreate
    ) -> FertilityProfile:
        """Create a new fertility profile"""
        # Check if profile already exists
        existing_profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fertility profile already exists for this patient"
            )
        
        # Verify patient exists
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Create profile
        db_profile = FertilityProfile(
            patient_id=patient_id,
            **profile_data.dict()
        )
        
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        
        return db_profile
    
    def update_profile(
        self,
        patient_id: int,
        profile_data: FertilityProfileUpdate
    ) -> FertilityProfile:
        """Update fertility profile"""
        profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fertility profile not found"
            )
        
        # Update fields
        update_dict = profile_data.dict(exclude_none=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def get_profile(self, patient_id: int) -> Optional[FertilityProfile]:
        """Get fertility profile for patient"""
        return self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
    
    def delete_profile(self, patient_id: int) -> bool:
        """Delete fertility profile"""
        profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fertility profile not found"
            )
        
        self.db.delete(profile)
        self.db.commit()
        return True


class CycleAnalysisService:
    """Service for analyzing fertility cycles"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_cycle(
        self,
        patient_id: int,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a fertility cycle"""
        # Get entries for the period
        entries = self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.patient_id == patient_id,
                FertilityEntry.submission_date >= start_date
            )
        )
        
        if end_date:
            entries = entries.filter(FertilityEntry.submission_date <= end_date)
        
        entries = entries.order_by(FertilityEntry.submission_date).all()
        
        if not entries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No entries found for analysis period"
            )
        
        # Calculate cycle statistics
        cycle_length = self._calculate_cycle_length(entries)
        ovulation_day = self._detect_ovulation_day(entries)
        luteal_phase_length = self._calculate_luteal_phase_length(cycle_length, ovulation_day)
        
        # BBT analysis
        bbt_analysis = self._analyze_bbt_pattern(entries, ovulation_day)
        
        # Symptom analysis
        symptom_analysis = self._analyze_symptoms(entries)
        
        # Fertility window analysis
        fertile_window = self._calculate_fertile_window(entries, ovulation_day)
        
        return {
            "cycle_length": cycle_length,
            "ovulation_day": ovulation_day,
            "luteal_phase_length": luteal_phase_length,
            "bbt_analysis": bbt_analysis,
            "symptom_analysis": symptom_analysis,
            "fertile_window": fertile_window,
            "ovulation_confirmed": ovulation_day is not None,
            "entries_analyzed": len(entries)
        }
    
    def generate_cycle_summary(
        self,
        patient_id: int,
        cycle_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive cycle summary"""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get fertility profile
        profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        # Analyze cycle
        analysis_result = self.analyze_cycle(patient_id, start_date or "", end_date)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_result, profile)
        
        # Predict next period
        next_period = self._predict_next_period(profile, analysis_result)
        
        return {
            "patient_id": patient_id,
            "patient_name": patient.name,
            "cycle_analysis": analysis_result,
            "recommendations": recommendations,
            "next_period_prediction": next_period,
            "fertility_score": self._calculate_fertility_score(analysis_result, profile)
        }
    
    def generate_doctor_summary(
        self,
        patient_id: int,
        timeframe: str = "cycle"
    ) -> Dict[str, Any]:
        """Generate summary for doctor visit"""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get patient info
        profile = self.db.query(FertilityProfile).filter(
            FertilityProfile.patient_id == patient_id
        ).first()
        
        # Get entries based on timeframe
        end_date = datetime.now().strftime('%Y-%m-%d')
        if timeframe == "cycle":
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif timeframe == "month":
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:  # three_months
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        entries = self.db.query(FertilityEntry).filter(
            and_(
                FertilityEntry.patient_id == patient_id,
                FertilityEntry.submission_date >= start_date,
                FertilityEntry.submission_date <= end_date
            )
        ).all()
        
        # Analyze multiple cycles
        cycles = self._group_entries_by_cycle(entries)
        cycle_stats = self._analyze_multiple_cycles(cycles)
        
        # Generate doctor questions
        doctor_questions = self._generate_doctor_questions(cycle_stats, profile)
        
        # Identify concerns
        concerns = self._identify_potential_concerns(cycle_stats, profile)
        
        return {
            "patient_info": {
                "name": patient.name,
                "age": self._calculate_age(patient.birth_date) if patient.birth_date else None,
                "email": patient.email
            },
            "fertility_profile": profile.dict() if profile else {},
            "cycle_statistics": cycle_stats,
            "timeframe": timeframe,
            "entries_analyzed": len(entries),
            "cycles_analyzed": len(cycles),
            "doctor_questions": doctor_questions,
            "potential_concerns": concerns,
            "generated_date": datetime.now().strftime('%Y-%m-%d')
        }
    
    def _calculate_cycle_length(self, entries: List[FertilityEntry]) -> Optional[int]:
        """Calculate cycle length from entries"""
        if not entries:
            return None
        
        cycle_days = [entry.cycle_day for entry in entries]
        return max(cycle_days) if cycle_days else None
    
    def _detect_ovulation_day(self, entries: List[FertilityEntry]) -> Optional[int]:
        """Detect ovulation day from entries"""
        # Check for LH peak
        for entry in entries:
            if entry.lh_test_result == LHTestResult.PEAK:
                return entry.cycle_day
        
        # Check for cervical fluid peak
        for entry in entries:
            if entry.cervical_fluid_type == CervicalFluidType.EGG_WHITE:
                return entry.cycle_day
        
        return None
    
    def _calculate_luteal_phase_length(
        self,
        cycle_length: Optional[int],
        ovulation_day: Optional[int]
    ) -> Optional[int]:
        """Calculate luteal phase length"""
        if not cycle_length or not ovulation_day:
            return None
        
        return cycle_length - ovulation_day
    
    def _analyze_bbt_pattern(
        self,
        entries: List[FertilityEntry],
        ovulation_day: Optional[int]
    ) -> Dict[str, Any]:
        """Analyze BBT pattern"""
        bbt_entries = [e for e in entries if e.bbt_temperature is not None]
        
        if not bbt_entries:
            return {"bbt_data_available": False}
        
        # Separate pre and post ovulation temperatures
        pre_ovulation = []
        post_ovulation = []
        
        for entry in bbt_entries:
            if ovulation_day and entry.cycle_day < ovulation_day:
                pre_ovulation.append(entry.bbt_temperature)
            elif ovulation_day and entry.cycle_day >= ovulation_day:
                post_ovulation.append(entry.bbt_temperature)
        
        # Calculate statistics
        analysis = {
            "bbt_data_available": True,
            "total_readings": len(bbt_entries),
            "average_temperature": sum(entry.bbt_temperature for entry in bbt_entries) / len(bbt_entries)
        }
        
        if pre_ovulation:
            analysis["average_pre_ovulation"] = sum(pre_ovulation) / len(pre_ovulation)
        
        if post_ovulation:
            analysis["average_post_ovulation"] = sum(post_ovulation) / len(post_ovulation)
        
        # Check for BBT shift
        if pre_ovulation and post_ovulation:
            avg_pre = sum(pre_ovulation) / len(pre_ovulation)
            avg_post = sum(post_ovulation) / len(post_ovulation)
            analysis["bbt_shift"] = avg_post - avg_pre
            analysis["bbt_shift_detected"] = (avg_post - avg_pre) >= 0.3  # 0.3°C threshold
        
        return analysis
    
    def _analyze_symptoms(self, entries: List[FertilityEntry]) -> Dict[str, Any]:
        """Analyze symptom patterns"""
        symptoms = {
            "libido": [],
            "breast_tenderness": [],
            "ovulation_pain": 0,
            "bloating": [],
            "mood": [],
            "energy": []
        }
        
        for entry in entries:
            if entry.libido_level:
                symptoms["libido"].append(entry.libido_level)
            if entry.breast_tenderness:
                symptoms["breast_tenderness"].append(entry.breast_tenderness)
            if entry.ovulation_pain:
                symptoms["ovulation_pain"] += 1
            if entry.bloating:
                symptoms["bloating"].append(entry.bloating)
            if entry.mood:
                symptoms["mood"].append(entry.mood)
            if entry.energy_level:
                symptoms["energy"].append(entry.energy_level)
        
        # Calculate patterns
        analysis = {}
        for symptom, values in symptoms.items():
            if values:
                if symptom == "ovulation_pain":
                    analysis[symptom] = {
                        "count": values,
                        "percentage": (values / len(entries)) * 100
                    }
                else:
                    # Find most common value
                    from collections import Counter
                    most_common = Counter(values).most_common(1)
                    if most_common:
                        analysis[symptom] = {
                            "most_common": most_common[0][0],
                            "frequency": most_common[0][1] / len(values)
                        }
        
        return analysis
    
    def _calculate_fertile_window(
        self,
        entries: List[FertilityEntry],
        ovulation_day: Optional[int]
    ) -> Dict[str, Any]:
        """Calculate fertile window"""
        if not ovulation_day:
            return {"detected": False}
        
        return {
            "detected": True,
            "ovulation_day": ovulation_day,
            "fertile_window_start": max(1, ovulation_day - 5),
            "fertile_window_end": ovulation_day + 1,
            "peak_fertility_day": ovulation_day - 1
        }
    
    def _group_entries_by_cycle(self, entries: List[FertilityEntry]) -> Dict[int, List[FertilityEntry]]:
        """Group entries by cycle number"""
        cycles = {}
        current_cycle = 1
        
        for entry in sorted(entries, key=lambda x: x.submission_date):
            if entry.cycle_day == 1 and entry.cycle_day != 0:
                current_cycle += 1
            cycles.setdefault(current_cycle, []).append(entry)
        
        return cycles
    
    def _analyze_multiple_cycles(self, cycles: Dict[int, List[FertilityEntry]]) -> Dict[str, Any]:
        """Analyze multiple cycles"""
        if not cycles:
            return {"total_cycles": 0}
        
        cycle_lengths = []
        ovulation_days = []
        
        for cycle_entries in cycles.values():
            cycle_length = self._calculate_cycle_length(cycle_entries)
            ovulation_day = self._detect_ovulation_day(cycle_entries)
            
            if cycle_length:
                cycle_lengths.append(cycle_length)
            if ovulation_day:
                ovulation_days.append(ovulation_day)
        
        # Calculate statistics
        stats = {
            "total_cycles": len(cycles),
            "cycles_with_data": len([c for c in cycles.values() if c])
        }
        
        if cycle_lengths:
            stats["average_cycle_length"] = sum(cycle_lengths) / len(cycle_lengths)
            stats["cycle_length_range"] = {"min": min(cycle_lengths), "max": max(cycle_lengths)}
            # Check regularity
            avg = stats["average_cycle_length"]
            variance = sum((x - avg) ** 2 for x in cycle_lengths) / len(cycle_lengths)
            stats["regular_cycles"] = variance <= 9  # Standard deviation <= 3 days
        
        if ovulation_days:
            stats["ovulation_detected"] = True
            stats["average_ovulation_day"] = sum(ovulation_days) / len(ovulation_days)
            stats["ovulation_rate"] = len(ovulation_days) / len(cycles)
        else:
            stats["ovulation_detected"] = False
            stats["ovulation_rate"] = 0
        
        return stats
    
    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        profile: Optional[FertilityProfile] = None
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for ovulation detection
        if not analysis.get("ovulation_confirmed", False):
            recommendations.append("Consider tracking LH tests more frequently to detect ovulation.")
        
        # Check luteal phase length
        luteal_length = analysis.get("luteal_phase_length")
        if luteal_length and luteal_length < 10:
            recommendations.append("Short luteal phase detected. Consider discussing with your doctor.")
        
        # Check BBT pattern
        bbt_analysis = analysis.get("bbt_analysis", {})
        if bbt_analysis.get("bbt_data_available") and not bbt_analysis.get("bbt_shift_detected"):
            recommendations.append("No clear BBT shift detected. Ensure consistent morning temperature taking.")
        
        # General recommendations
        if profile and profile.trying_to_conceive:
            fertile_window = analysis.get("fertile_window", {})
            if fertile_window.get("detected"):
                recommendations.append(f"Time intercourse around days {fertile_window.get('fertile_window_start')}-{fertile_window.get('fertile_window_end')} for optimal chances.")
            else:
                recommendations.append("Consider tracking cervical fluid and LH tests to identify fertile window.")
        
        return recommendations
    
    def _predict_next_period(
        self,
        profile: Optional[FertilityProfile],
        analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Predict next period date"""
        if not profile or not profile.last_period_date:
            return None
        
        try:
            last_period = datetime.strptime(profile.last_period_date, '%Y-%m-%d')
            avg_cycle_length = analysis.get("cycle_analysis", {}).get("cycle_length") or profile.cycle_length
            
            next_period = last_period + timedelta(days=avg_cycle_length)
            return next_period.strftime('%Y-%m-%d')
        except:
            return None
    
    def _calculate_fertility_score(
        self,
        analysis: Dict[str, Any],
        profile: Optional[FertilityProfile] = None
    ) -> float:
        """Calculate fertility score (0-100)"""
        score = 50  # Base score
        
        # Add points for ovulation detection
        if analysis.get("ovulation_confirmed"):
            score += 20
        
        # Add points for regular cycles
        cycle_stats = analysis.get("cycle_analysis", {})
        if cycle_stats.get("cycle_length") and 21 <= cycle_stats["cycle_length"] <= 35:
            score += 15
        
        # Add points for adequate luteal phase
        luteal_length = cycle_stats.get("luteal_phase_length")
        if luteal_length and luteal_length >= 10:
            score += 15
        
        # Add points for BBT shift
        bbt_analysis = cycle_stats.get("bbt_analysis", {})
        if bbt_analysis.get("bbt_shift_detected"):
            score += 10
        
        return min(100, max(0, score))
    
    def _generate_doctor_questions(
        self,
        cycle_stats: Dict[str, Any],
        profile: Optional[FertilityProfile] = None
    ) -> List[str]:
        """Generate questions for doctor visit"""
        questions = []
        
        if not cycle_stats.get("ovulation_detected", False):
            questions.append("I'm not seeing clear ovulation signs. Should I be concerned?")
        
        if not cycle_stats.get("regular_cycles", True):
            questions.append("My cycles appear irregular. What could be causing this?")
        
        if profile and profile.trying_to_conceive and profile.previous_miscarriages > 0:
            questions.append(f"Given my history of {profile.previous_miscarriages} miscarriage(s), what additional testing do you recommend?")
        
        questions.append("Based on my tracking data, what's the best timing for intercourse?")
        questions.append("Are there any lifestyle changes you recommend to improve fertility?")
        
        return questions
    
    def _identify_potential_concerns(
        self,
        cycle_stats: Dict[str, Any],
        profile: Optional[FertilityProfile] = None
    ) -> List[str]:
        """Identify potential concerns from analysis"""
        concerns = []
        
        if not cycle_stats.get("ovulation_detected", False):
            concerns.append("Possible anovulatory cycles")
        
        if not cycle_stats.get("regular_cycles", True):
            concerns.append("Irregular cycle length")
        
        # Check luteal phase if we have individual cycle data
        if "cycles" in cycle_stats:
            for cycle_data in cycle_stats["cycles"]:
                luteal_length = cycle_data.get("luteal_phase_length")
                if luteal_length and luteal_length < 10:
                    concerns.append("Short luteal phase detected")
                    break
        
        if profile and profile.trying_to_conceive and profile.previous_miscarriages >= 2:
            concerns.append("Recurrent pregnancy loss history")
        
        return list(set(concerns))  # Remove duplicates
    
    def _calculate_age(self, birth_date_str: Optional[str]) -> Optional[int]:
        """Calculate age from birth date"""
        if not birth_date_str:
            return None
        
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            return age
        except:
            return None


class PatientService:
    """Service for managing patients"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient"""
        # Check if patient already exists
        existing_patient = self.db.query(Patient).filter(
            or_(
                Patient.user_id == patient_data["user_id"],
                Patient.email == patient_data["email"] 
                
            )
        ).first()
        
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this user ID or email already exists"
            )
        
        # Create patient
        db_patient = Patient(
    user_id=patient_data["user_id"],
    name=patient_data["name"],
    email=patient_data["email"],
    phone_number=patient_data.get("phone_number"),
    birth_date=patient_data.get("birth_date")
)
        
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        
        return db_patient
    
    def get_patient(self, patient_id: int) -> Patient:
        """Get patient by ID"""

        print("=" * 50)
        print("🚨 [SERVICE-GET-PATIENT] METHOD ENTERED!")
        print(f"🚨 [SERVICE-GET-PATIENT] patient_id = {patient_id}")
        print("=" * 50)

        print(f"🔍 [SERVICE-GET-PATIENT] START: Looking for patient_id: {patient_id}")

        print(f"🔍 [SERVICE-GET-PATIENT] Looking for patient_id: {patient_id}")
        print(f"🔍 [SERVICE-GET-PATIENT] Database session: {self.db}")
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()

        print(f"🔍 [SERVICE-GET-PATIENT] Query result: {patient}")
        print(f"🔍 [SERVICE-GET-PATIENT] Patient found: {patient is not None}")
        
        if not patient:

            print(f"❌ [SERVICE-GET-PATIENT] Patient {patient_id} NOT FOUND in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        print(f"✅ [SERVICE-GET-PATIENT] Found patient: id={patient.id}, user_id={patient.user_id}")
        return patient
    
    def get_patient_by_user_id(self, user_id: str) -> Optional[Patient]:
        """Get patient by user ID"""
        return self.db.query(Patient).filter(Patient.user_id == user_id).first()
    
    def update_patient(self, patient_id: int, update_data: dict) -> Patient:
        """Update patient information"""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(patient, field):
                setattr(patient, field, value)
        
        patient.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(patient)
        
        return patient
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete patient"""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        self.db.delete(patient)
        self.db.commit()
        return True


class ExportService:
    """Service for generating exports and reports"""
    
    @staticmethod
    def create_cycle_summary_text(
        patient_name: str,
        cycle_day: int,
        fertility_status: FertilityStatus,
        fertility_probability: float,
        observations: Dict[str, Any],
        recommendations: Optional[List[str]] = None
    ) -> str:
        """Create text summary of cycle status"""
        summary = f"Fertility Update for {patient_name}\n"
        summary += "=" * 40 + "\n\n"
        summary += f"Cycle Day: {cycle_day}\n"
        summary += f"Fertility Status: {fertility_status.value.replace('_', ' ').title()}\n"
        summary += f"Fertility Probability: {fertility_probability:.1f}%\n\n"
        
        summary += "Recent Observations:\n"
        for key, value in observations.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    summary += f"- {formatted_key}: {json.dumps(value, indent=2)}\n"
                else:
                    summary += f"- {formatted_key}: {value}\n"
        
        if recommendations:
            summary += "\nRecommendations:\n"
            for rec in recommendations:
                summary += f"- {rec}\n"
        
        summary += "\nGenerated by Fertility Tracker"
        return summary
    
    @staticmethod
    def create_emergency_card_text(
        patient_info: Dict[str, Any],
        fertility_profile: Dict[str, Any],
        latest_entry: Dict[str, Any]
    ) -> str:
        """Create emergency card text"""
        card = "⚠️ FERTILITY & PREGNANCY EMERGENCY CARD ⚠️\n\n"
        card += "Show this to emergency medical staff\n\n"
        
        card += "PATIENT INFORMATION:\n"
        card += f"• Name: {patient_info.get('name', 'N/A')}\n"
        card += f"• Age: {patient_info.get('age', 'N/A')}\n"
        
        if fertility_profile:
            card += f"• Trying to Conceive: {'Yes' if fertility_profile.get('trying_to_conceive') else 'No'}\n"
            card += f"• Previous Pregnancies: {fertility_profile.get('previous_pregnancies', 0)}\n"
            card += f"• Previous Births: {fertility_profile.get('previous_births', 0)}\n"
            card += f"• Previous Miscarriages: {fertility_profile.get('previous_miscarriages', 0)}\n"
        
        if latest_entry:
            card += f"\nLATEST FERTILITY STATUS ({latest_entry.get('submission_date', 'N/A')}):\n"
            card += f"• Cycle Day: {latest_entry.get('cycle_day', 'N/A')}\n"
            card += f"• Fertility Status: {latest_entry.get('fertility_status', 'N/A')}\n"
            if latest_entry.get('lh_test_result'):
                card += f"• LH Test: {latest_entry.get('lh_test_result')}\n"
        
        card += "\nEMERGENCY INSTRUCTIONS:\n"
        card += "• Call 911 or go to nearest hospital\n"
        card += "• Show this card to medical staff\n"
        card += "• Inform staff if you might be pregnant\n\n"
        
        card += "Generated by Fertility Tracker App"
        return card