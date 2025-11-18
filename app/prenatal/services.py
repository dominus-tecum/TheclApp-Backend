# app/prenatal/services.py
from sqlalchemy.orm import Session
from datetime import date
from .models import PrenatalEntry
from .schemas import PrenatalCreate

class PrenatalService:
    
    @staticmethod
    def create_prenatal_entry(db: Session, entry: PrenatalCreate):
        # Check if entry already exists
        existing_entry = PrenatalService.check_existing_entry(db, entry.patient_id, entry.submission_date)
        
        if existing_entry:
            # Update existing entry with flat fields
            existing_entry.maternal_temperature = entry.maternal_temperature
            existing_entry.blood_pressure_systolic = entry.blood_pressure_systolic
            existing_entry.blood_pressure_diastolic = entry.blood_pressure_diastolic
            existing_entry.maternal_heart_rate = entry.maternal_heart_rate
            existing_entry.respiratory_rate = entry.respiratory_rate
            existing_entry.oxygen_saturation = entry.oxygen_saturation
            existing_entry.weight = entry.weight
            existing_entry.edema = entry.edema
            existing_entry.edema_location = ','.join(entry.edema_location) if entry.edema_location else ''
            existing_entry.headache = entry.headache
            existing_entry.visual_disturbances = entry.visual_disturbances
            existing_entry.epigastric_pain = entry.epigastric_pain
            existing_entry.nausea_level = entry.nausea_level
            existing_entry.vomiting_episodes = entry.vomiting_episodes
            existing_entry.fetal_movement = entry.fetal_movement
            existing_entry.movement_count = entry.movement_count
            existing_entry.movement_duration = entry.movement_duration
            existing_entry.contractions = entry.contractions
            existing_entry.contraction_frequency = entry.contraction_frequency
            existing_entry.contraction_duration = entry.contraction_duration
            existing_entry.contraction_intensity = entry.contraction_intensity
            existing_entry.vaginal_bleeding = entry.vaginal_bleeding
            existing_entry.bleeding_color = entry.bleeding_color
            existing_entry.fluid_leak = entry.fluid_leak
            existing_entry.fluid_color = entry.fluid_color
            existing_entry.fluid_amount = entry.fluid_amount
            existing_entry.urinary_frequency = entry.urinary_frequency
            existing_entry.dysuria = entry.dysuria
            existing_entry.urinary_incontinence = entry.urinary_incontinence
            existing_entry.appetite = entry.appetite
            existing_entry.heartburn = entry.heartburn
            existing_entry.constipation = entry.constipation
            existing_entry.medications_taken = entry.medications_taken
            existing_entry.missed_medications = entry.missed_medications
            existing_entry.gestational_age = entry.gestational_age
            existing_entry.high_risk = entry.high_risk
            existing_entry.additional_notes = entry.additional_notes
            existing_entry.status = entry.status
            
            db.commit()
            db.refresh(existing_entry)
            return existing_entry
        else:
            # Create new entry with flat fields
            db_entry = PrenatalEntry(
                patient_id=entry.patient_id,
                patient_name=entry.patient_name,
                submission_date=entry.submission_date,
                condition_type=entry.condition_type,
                status=entry.status,
                # All the flat fields
                maternal_temperature=entry.maternal_temperature,
                blood_pressure_systolic=entry.blood_pressure_systolic,
                blood_pressure_diastolic=entry.blood_pressure_diastolic,
                maternal_heart_rate=entry.maternal_heart_rate,
                respiratory_rate=entry.respiratory_rate,
                oxygen_saturation=entry.oxygen_saturation,
                weight=entry.weight,
                edema=entry.edema,
                edema_location=','.join(entry.edema_location) if entry.edema_location else '',
                headache=entry.headache,
                visual_disturbances=entry.visual_disturbances,
                epigastric_pain=entry.epigastric_pain,
                nausea_level=entry.nausea_level,
                vomiting_episodes=entry.vomiting_episodes,
                fetal_movement=entry.fetal_movement,
                movement_count=entry.movement_count,
                movement_duration=entry.movement_duration,
                contractions=entry.contractions,
                contraction_frequency=entry.contraction_frequency,
                contraction_duration=entry.contraction_duration,
                contraction_intensity=entry.contraction_intensity,
                vaginal_bleeding=entry.vaginal_bleeding,
                bleeding_color=entry.bleeding_color,
                fluid_leak=entry.fluid_leak,
                fluid_color=entry.fluid_color,
                fluid_amount=entry.fluid_amount,
                urinary_frequency=entry.urinary_frequency,
                dysuria=entry.dysuria,
                urinary_incontinence=entry.urinary_incontinence,
                appetite=entry.appetite,
                heartburn=entry.heartburn,
                constipation=entry.constipation,
                medications_taken=entry.medications_taken,
                missed_medications=entry.missed_medications,
                gestational_age=entry.gestational_age,
                high_risk=entry.high_risk,
                additional_notes=entry.additional_notes
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            return db_entry
    
    @staticmethod
    def check_existing_entry(db: Session, patient_id: str, date: date):
        return db.query(PrenatalEntry).filter(
            PrenatalEntry.patient_id == patient_id,
            PrenatalEntry.submission_date == date
        ).first()
    
    @staticmethod
    def get_all_prenatal_entries(db: Session):
        return db.query(PrenatalEntry).all()