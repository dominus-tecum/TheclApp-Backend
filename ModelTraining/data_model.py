class PatientMentalHealthRecord:
    def __init__(
        self, patient_id, age, gender, diagnosis, symptom_severity,
        mood_score, sleep_quality, physical_activity, medication, therapy_type,
        treatment_start_date, treatment_duration_weeks, stress_level,
        outcome, treatment_progress, ai_detected_emotional_state, adherence_percent
    ):
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.diagnosis = diagnosis
        self.symptom_severity = symptom_severity
        self.mood_score = mood_score
        self.sleep_quality = sleep_quality
        self.physical_activity = physical_activity
        self.medication = medication
        self.therapy_type = therapy_type
        self.treatment_start_date = treatment_start_date
        self.treatment_duration_weeks = treatment_duration_weeks
        self.stress_level = stress_level
        self.outcome = outcome
        self.treatment_progress = treatment_progress
        self.ai_detected_emotional_state = ai_detected_emotional_state
        self.adherence_percent = adherence_percent