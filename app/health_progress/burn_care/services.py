from sqlalchemy.orm import Session
from datetime import date
from .models import BurnCareEntry
from .schemas import BurnCareCreate

class BurnCareService:
    
    @staticmethod
    def create_burn_care_entry(db: Session, entry: BurnCareCreate):
        # Check if entry already exists
        existing_entry = BurnCareService.check_existing_entry(db, entry.patient_id, entry.submission_date)
        
        # Convert date to string for JSON storage
        submission_date_str = entry.submission_date.isoformat() if hasattr(entry.submission_date, 'isoformat') else str(entry.submission_date)
        
        if existing_entry:
            # Update existing entry
            existing_entry.common_data = {
                "temperature": entry.temperature,
                "pain_level": entry.pain_level,
                "status": entry.status,
                "day_post_op": entry.dayPost_op,
                "submission_date": submission_date_str
            }
            
            existing_entry.condition_data = {
                "itching": entry.itching,
                "wound_appearance": entry.wound_appearance,
                "drainage": entry.drainage,
                "rom_exercises": entry.rom_exercises,
                "joint_tightness": entry.joint_tightness,
                "mobility": entry.mobility,
                "compression_garment": entry.compression_garment,
                "scar_appearance": entry.scar_appearance,
                "protein_intake": entry.protein_intake,
                "fluid_intake": entry.fluid_intake,
                "additional_notes": entry.additional_notes
            }
            
            existing_entry.condition_type = entry.condition_type
            
            db.commit()
            db.refresh(existing_entry)
            return existing_entry
        else:
            # Create new entry
            db_entry = BurnCareEntry(
                patient_id=entry.patient_id,
                patient_name=entry.patient_name,
                surgery_type=entry.surgery_type,
                condition_type=entry.condition_type,
                submission_date=entry.submission_date,
                photo_urls=entry.photo_urls if hasattr(entry, 'photo_urls') else [],
                common_data={
                    "temperature": entry.temperature,
                    "pain_level": entry.pain_level,
                    "status": entry.status,
                    "day_post_op": entry.dayPost_op,
                    "submission_date": submission_date_str
                },
                condition_data={
                    "itching": entry.itching,
                    "wound_appearance": entry.wound_appearance,
                    "drainage": entry.drainage,
                    "rom_exercises": entry.rom_exercises,
                    "joint_tightness": entry.joint_tightness,
                    "mobility": entry.mobility,
                    "compression_garment": entry.compression_garment,
                    "scar_appearance": entry.scar_appearance,
                    "protein_intake": entry.protein_intake,
                    "fluid_intake": entry.fluid_intake,
                    "additional_notes": entry.additional_notes
                }
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            return db_entry

    @staticmethod
    def check_existing_entry(db: Session, patient_id: str, dt: date):
        return db.query(BurnCareEntry).filter(
            BurnCareEntry.patient_id == patient_id,
            BurnCareEntry.submission_date == dt
        ).first()

    @staticmethod
    def get_all_burn_care_entries(db: Session, skip: int = 0, limit: int = 100):
        return db.query(BurnCareEntry).offset(skip).limit(limit).all()