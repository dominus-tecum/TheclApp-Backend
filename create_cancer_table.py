import sqlite3

conn = sqlite3.connect('hospiapp.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS cancer_entries')

cursor.execute('''
    CREATE TABLE cancer_entries (
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
        pain_level INTEGER,
        pain_location TEXT,
        side_effects INTEGER,
        condition_type TEXT DEFAULT 'cancer',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        urgency_status TEXT DEFAULT 'low'
    )
''')

conn.commit()
conn.close()
print('✅ cancer_entries table created with flat structure')