import sqlite3

DB_NAME = "mental_health.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patient_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        age INTEGER,
        gender TEXT,
        diagnosis TEXT,
        symptom_severity INTEGER,
        mood_label TEXT,
        mood_score INTEGER,
        sleep_quality INTEGER,
        physical_activity TEXT,
        medication TEXT,
        therapy_type TEXT,
        treatment_start_date TEXT,
        treatment_duration_weeks INTEGER,
        stress_level INTEGER,
        outcome TEXT,
        treatment_progress INTEGER,
        ai_detected_emotional_state TEXT,
        adherence_percent INTEGER
    )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized and patient_records table created (if not exists) in {DB_NAME}.")

if __name__ == "__main__":
    init_db()