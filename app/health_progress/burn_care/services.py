from sqlalchemy.orm import Session
from datetime import date
from .models import BurnCareEntry
from .schemas import BurnCareCreate

class BurnCareService:
    
    @staticmethod
    def create_burn_care_entry(db: Session, entry: BurnCareCreate):
        # Check if entry already exists
        existing_entry = BurnCareService.check_existing_entry(db, entry.patient_id, entry.submission_date)
        
        if existing_entry:
            # Update existing entry
            existing_entry.common_data = {
                "temperature": entry.temperature,
                "pain_level": entry.pain_level,
                "status": entry.status,
                "day_post_op": entry.dayPost_op  # ✅ ADD: Store dayPost_op
            }
            
            existing_entry.condition_data = {
                # ❌ REMOVE: "pain_level": entry.pain_level, (duplicate)
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
                # ✅ ADD: Store submitted_at if your model has it
                # submitted_at=entry.submitted_at,  # Uncomment if field exists
                common_data={
                    "temperature": entry.temperature,
                    "pain_level": entry.pain_level,
                    "status": entry.status,
                    "day_post_op": entry.dayPost_op  # ✅ ADD: Store dayPost_op
                },
                condition_data={
                    # ❌ REMOVE: "pain_level": entry.pain_level, (duplicate)
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
    def check_existing_entry(db: Session, patient_id: str, date: date):
        return db.query(BurnCareEntry).filter(
            BurnCareEntry.patient_id == patient_id,
            BurnCareEntry.submission_date == date
        ).first()
    
    @staticmethod
    def get_all_burn_care_entries(db: Session):
        return db.query(BurnCareEntry).all()