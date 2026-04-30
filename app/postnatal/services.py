from sqlalchemy.orm import Session
from datetime import date, datetime
from .models import PostnatalEntry, PostnatalProfile
from .schemas import PostnatalCreate, PostnatalProfileCreate

class PostnatalService:
    
    @staticmethod
    def create_or_update_profile(db: Session, patient_id: str, profile_data: PostnatalProfileCreate):
        # Check if profile already exists
        existing_profile = db.query(PostnatalProfile).filter(
            PostnatalProfile.patient_id == patient_id
        ).first()
        
        if existing_profile:
            # Update existing profile with flat fields
            existing_profile.delivery_date = profile_data.delivery_date
            existing_profile.delivery_type = profile_data.delivery_type
            existing_profile.infant_name = profile_data.infant_name
            existing_profile.infant_birth_weight = profile_data.infant_birth_weight
            existing_profile.infant_birth_date = profile_data.infant_birth_date
            
            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # Create new profile with flat fields
            db_profile = PostnatalProfile(
                patient_id=patient_id,
                patient_name=profile_data.patient_name,
                delivery_date=profile_data.delivery_date,
                delivery_type=profile_data.delivery_type,
                infant_name=profile_data.infant_name,
                infant_birth_weight=profile_data.infant_birth_weight,
                infant_birth_date=profile_data.infant_birth_date,
                created_at=datetime.now()
            )
            
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)
            return db_profile
    
    @staticmethod
    def get_profile(db: Session, patient_id: str):
        return db.query(PostnatalProfile).filter(
            PostnatalProfile.patient_id == patient_id
        ).first()
    
    @staticmethod
    def create_postnatal_entry(db: Session, entry: PostnatalCreate):
        # Check if entry already exists
        existing_entry = PostnatalService.check_existing_entry(db, entry.patient_id, entry.submission_date)
        
        if existing_entry:
            # Update existing entry
            existing_entry.infant_name = entry.infant_name
            existing_entry.condition_type = entry.condition_type
            existing_entry.status = entry.status
            existing_entry.days_postpartum = entry.days_postpartum
            
            # Vital Signs
            existing_entry.maternal_temperature = entry.maternal_temperature
            existing_entry.blood_pressure_systolic = entry.blood_pressure_systolic
            existing_entry.blood_pressure_diastolic = entry.blood_pressure_diastolic
            existing_entry.maternal_heart_rate = entry.maternal_heart_rate
            existing_entry.sleep_hours = entry.sleep_hours
            
            # Pain Assessment
            existing_entry.pain_level = entry.pain_level
            existing_entry.pain_location = str(entry.pain_location) if entry.pain_location else None
            existing_entry.perineal_pain = entry.perineal_pain
            existing_entry.uterine_pain = entry.uterine_pain
            existing_entry.nipple_pain = entry.nipple_pain
            existing_entry.c_section_pain = entry.c_section_pain
            
            # Uterine Recovery & Lochia
            existing_entry.lochia_flow = entry.lochia_flow
            existing_entry.lochia_color = entry.lochia_color
            existing_entry.lochia_odor = entry.lochia_odor
            existing_entry.healing_progress = entry.healing_progress
            existing_entry.perineal_tear = entry.perineal_tear
            
            # Incision
            existing_entry.incision_redness = entry.incision_redness
            existing_entry.incision_discharge = entry.incision_discharge
            
            # Breastfeeding
            existing_entry.breastfeeding_status = entry.breastfeeding_status
            existing_entry.breast_engorgement = entry.breast_engorgement
            existing_entry.nipple_condition = entry.nipple_condition
            existing_entry.milk_supply = entry.milk_supply
            existing_entry.feeding_method = entry.feeding_method
            existing_entry.feeding_frequency = entry.feeding_frequency
            existing_entry.feeding_duration = entry.feeding_duration
            existing_entry.latching_quality = entry.latching_quality
            
            # Emotional Wellbeing
            existing_entry.baby_blues_symptoms = entry.baby_blues_symptoms
            existing_entry.maternal_energy = entry.maternal_energy
            
            # Gastrointestinal & Urinary
            existing_entry.appetite = entry.appetite
            existing_entry.bowel_movement = entry.bowel_movement
            existing_entry.urinary_frequency = entry.urinary_frequency
            existing_entry.incontinence = entry.incontinence
            
            # Baby Information
            existing_entry.baby_feeding_frequency = entry.baby_feeding_frequency
            existing_entry.baby_urination_frequency = entry.baby_urination_frequency
            existing_entry.baby_bowel_movement_frequency = entry.baby_bowel_movement_frequency
            existing_entry.baby_weight_gain = entry.baby_weight_gain
            existing_entry.wet_diapers = entry.wet_diapers
            existing_entry.soiled_diapers = entry.soiled_diapers
            existing_entry.stool_color = entry.stool_color
            existing_entry.stool_consistency = entry.stool_consistency
            existing_entry.infant_temperature = entry.infant_temperature
            existing_entry.infant_heart_rate = entry.infant_heart_rate
            existing_entry.jaundice_level = entry.jaundice_level
            existing_entry.umbilical_cord = entry.umbilical_cord
            existing_entry.skin_condition = entry.skin_condition
            existing_entry.infant_alertness = entry.infant_alertness
            existing_entry.sleep_pattern = entry.sleep_pattern
            existing_entry.crying_level = entry.crying_level
            
            # Medications
            existing_entry.medication_adherence = entry.medication_adherence
            existing_entry.missed_medications = entry.missed_medications
            
            # Notes
            existing_entry.additional_notes = entry.additional_notes
            existing_entry.additional_concerns = entry.additional_concerns
            existing_entry.submitted_at = datetime.now()
            
            db.commit()
            db.refresh(existing_entry)
            return existing_entry
        
        else:
            # Create new entry with ALL fields
            db_entry = PostnatalEntry(
                patient_id=entry.patient_id,
                patient_name=entry.patient_name,
                infant_name=entry.infant_name,
                submission_date=entry.submission_date,
                condition_type=entry.condition_type,
                status=entry.status,
                days_postpartum=entry.days_postpartum,
                
                # Vital Signs
                maternal_temperature=entry.maternal_temperature,
                blood_pressure_systolic=entry.blood_pressure_systolic,
                blood_pressure_diastolic=entry.blood_pressure_diastolic,
                maternal_heart_rate=entry.maternal_heart_rate,
                sleep_hours=entry.sleep_hours,
                
                # Pain Assessment
                pain_level=entry.pain_level,
                pain_location=str(entry.pain_location) if entry.pain_location else None,
                perineal_pain=entry.perineal_pain,
                uterine_pain=entry.uterine_pain,
                nipple_pain=entry.nipple_pain,
                c_section_pain=entry.c_section_pain,
                
                # Uterine Recovery & Lochia
                lochia_flow=entry.lochia_flow,
                lochia_color=entry.lochia_color,
                lochia_odor=entry.lochia_odor,
                healing_progress=entry.healing_progress,
                perineal_tear=entry.perineal_tear,
                
                # Incision
                incision_redness=entry.incision_redness,
                incision_discharge=entry.incision_discharge,
                
                # Breastfeeding
                breastfeeding_status=entry.breastfeeding_status,
                breast_engorgement=entry.breast_engorgement,
                nipple_condition=entry.nipple_condition,
                milk_supply=entry.milk_supply,
                feeding_method=entry.feeding_method,
                feeding_frequency=entry.feeding_frequency,
                feeding_duration=entry.feeding_duration,
                latching_quality=entry.latching_quality,
                
                # Emotional Wellbeing
                baby_blues_symptoms=entry.baby_blues_symptoms,
                maternal_energy=entry.maternal_energy,
                
                # Gastrointestinal & Urinary
                appetite=entry.appetite,
                bowel_movement=entry.bowel_movement,
                urinary_frequency=entry.urinary_frequency,
                incontinence=entry.incontinence,
                
                # Baby Information
                baby_feeding_frequency=entry.baby_feeding_frequency,
                baby_urination_frequency=entry.baby_urination_frequency,
                baby_bowel_movement_frequency=entry.baby_bowel_movement_frequency,
                baby_weight_gain=entry.baby_weight_gain,
                wet_diapers=entry.wet_diapers,
                soiled_diapers=entry.soiled_diapers,
                stool_color=entry.stool_color,
                stool_consistency=entry.stool_consistency,
                infant_temperature=entry.infant_temperature,
                infant_heart_rate=entry.infant_heart_rate,
                jaundice_level=entry.jaundice_level,
                umbilical_cord=entry.umbilical_cord,
                skin_condition=entry.skin_condition,
                infant_alertness=entry.infant_alertness,
                sleep_pattern=entry.sleep_pattern,
                crying_level=entry.crying_level,
                
                # Medications
                medication_adherence=entry.medication_adherence,
                missed_medications=entry.missed_medications,
                
                # Notes
                additional_notes=entry.additional_notes,
                additional_concerns=entry.additional_concerns,
                submitted_at=datetime.now()
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            return db_entry
    
    @staticmethod
    def check_existing_entry(db: Session, patient_id: str, submission_date: date):
        return db.query(PostnatalEntry).filter(
            PostnatalEntry.patient_id == patient_id,
            PostnatalEntry.submission_date == submission_date
        ).first()
    
    @staticmethod
    def get_all_postnatal_entries(db: Session):
        return db.query(PostnatalEntry).all()
    
    @staticmethod
    def get_patient_entries(db: Session, patient_id: str):
        return db.query(PostnatalEntry).filter(
            PostnatalEntry.patient_id == patient_id
        ).all()