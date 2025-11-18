import sqlite3

conn = sqlite3.connect('hospiapp.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS kidney_entries')

cursor.execute('''
    CREATE TABLE kidney_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        patient_name TEXT NOT NULL,
        submission_date TEXT NOT NULL,
        blood_pressure_systolic TEXT,
        blood_pressure_diastolic TEXT,
        energy_level INTEGER,
        sleep_hours REAL,
        sleep_quality INTEGER,
        medications TEXT,
        symptoms TEXT,
        notes TEXT,
        status TEXT,
        weight TEXT,
        swelling_level INTEGER,
        urine_output TEXT,
        fluid_intake TEXT,
        breathing_difficulty INTEGER,
        fatigue_level INTEGER,
        nausea_level INTEGER,
        itching_level INTEGER,
        condition_type TEXT DEFAULT 'kidney',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        urgency_status TEXT DEFAULT 'low'
    )
''')

conn.commit()
conn.close()
print('✅ kidney_entries table recreated with sleep_hours REAL')