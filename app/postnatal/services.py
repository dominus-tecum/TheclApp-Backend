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
            # Update existing entry with flat fields
            existing_entry.infant_name = entry.infant_name
            existing_entry.condition_type = entry.condition_type
            existing_entry.status = entry.status
            existing_entry.days_postpartum = entry.days_postpartum
            
            # Maternal Recovery
            existing_entry.lochia_flow = entry.lochia_flow
            existing_entry.lochia_color = entry.lochia_color
            existing_entry.perineal_pain = entry.perineal_pain
            existing_entry.uterine_pain = entry.uterine_pain
            existing_entry.breast_engorgement = entry.breast_engorgement
            existing_entry.nipple_pain = entry.nipple_pain
            existing_entry.c_section_pain = entry.c_section_pain
            existing_entry.incision_redness = entry.incision_redness
            existing_entry.incision_discharge = entry.incision_discharge
            
            # Vital Signs
            existing_entry.maternal_temperature = entry.maternal_temperature
            existing_entry.blood_pressure_systolic = entry.blood_pressure_systolic
            existing_entry.blood_pressure_diastolic = entry.blood_pressure_diastolic
            existing_entry.maternal_heart_rate = entry.maternal_heart_rate
            
            # Mental Health
            existing_entry.mood_laugh = entry.mood_laugh
            existing_entry.mood_anxious = entry.mood_anxious
            existing_entry.mood_blame = entry.mood_blame
            existing_entry.mood_panic = entry.mood_panic
            existing_entry.mood_sleep = entry.mood_sleep
            existing_entry.mood_sad = entry.mood_sad
            existing_entry.mood_crying = entry.mood_crying
            existing_entry.mood_harm = entry.mood_harm
            
            # Infant Care
            existing_entry.feeding_method = entry.feeding_method
            existing_entry.feeding_frequency = entry.feeding_frequency
            existing_entry.feeding_duration = entry.feeding_duration
            existing_entry.latching_quality = entry.latching_quality
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
            
            # General
            existing_entry.maternal_energy = entry.maternal_energy
            existing_entry.support_system = entry.support_system
            existing_entry.additional_notes = entry.additional_notes
            
            db.commit()
            db.refresh(existing_entry)
            return existing_entry
        else:
            # Create new entry with flat fields
            db_entry = PostnatalEntry(
                patient_id=entry.patient_id,
                patient_name=entry.patient_name,
                infant_name=entry.infant_name,
                submission_date=entry.submission_date,
                condition_type=entry.condition_type,
                status=entry.status,
                days_postpartum=entry.days_postpartum,
                
                # Maternal Recovery
                lochia_flow=entry.lochia_flow,
                lochia_color=entry.lochia_color,
                perineal_pain=entry.perineal_pain,
                uterine_pain=entry.uterine_pain,
                breast_engorgement=entry.breast_engorgement,
                nipple_pain=entry.nipple_pain,
                c_section_pain=entry.c_section_pain,
                incision_redness=entry.incision_redness,
                incision_discharge=entry.incision_discharge,
                
                # Vital Signs
                maternal_temperature=entry.maternal_temperature,
                blood_pressure_systolic=entry.blood_pressure_systolic,
                blood_pressure_diastolic=entry.blood_pressure_diastolic,
                maternal_heart_rate=entry.maternal_heart_rate,
                
                # Mental Health
                mood_laugh=entry.mood_laugh,
                mood_anxious=entry.mood_anxious,
                mood_blame=entry.mood_blame,
                mood_panic=entry.mood_panic,
                mood_sleep=entry.mood_sleep,
                mood_sad=entry.mood_sad,
                mood_crying=entry.mood_crying,
                mood_harm=entry.mood_harm,
                
                # Infant Care
                feeding_method=entry.feeding_method,
                feeding_frequency=entry.feeding_frequency,
                feeding_duration=entry.feeding_duration,
                latching_quality=entry.latching_quality,
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
                
                # General
                maternal_energy=entry.maternal_energy,
                support_system=entry.support_system,
                additional_notes=entry.additional_notes,
                submitted_at=datetime.now()
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            return db_entry
    
    @staticmethod
    def check_existing_entry(db: Session, patient_id: str, date: date):
        return db.query(PostnatalEntry).filter(
            PostnatalEntry.patient_id == patient_id,
            PostnatalEntry.submission_date == date
        ).first()
    
    @staticmethod
    def get_all_postnatal_entries(db: Session):
        return db.query(PostnatalEntry).all()
    
    @staticmethod
    def get_patient_entries(db: Session, patient_id: str):
        return db.query(PostnatalEntry).filter(
            PostnatalEntry.patient_id == patient_id
        ).all()