import sqlite3

conn = sqlite3.connect('hospiapp.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS prenatal_entries')

cursor.execute('''
    CREATE TABLE prenatal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        patient_name TEXT NOT NULL,
        submission_date TEXT NOT NULL,
        
        -- Maternal Vital Signs
        maternal_temperature TEXT,
        blood_pressure_systolic TEXT,
        blood_pressure_diastolic TEXT,
        maternal_heart_rate TEXT,
        respiratory_rate TEXT,
        oxygen_saturation TEXT,
        
        -- Maternal Symptoms
        weight TEXT,
        edema TEXT,
        edema_location TEXT,
        headache TEXT,
        visual_disturbances INTEGER,
        epigastric_pain INTEGER,
        nausea_level TEXT,
        vomiting_episodes INTEGER,
        
        -- Fetal Movement
        fetal_movement TEXT,
        movement_count INTEGER,
        movement_duration TEXT,
        
        -- Contractions
        contractions INTEGER,
        contraction_frequency TEXT,
        contraction_duration TEXT,
        contraction_intensity TEXT,
        
        -- Vaginal Symptoms
        vaginal_bleeding TEXT,
        bleeding_color TEXT,
        fluid_leak INTEGER,
        fluid_color TEXT,
        fluid_amount TEXT,
        
        -- Urinary Symptoms
        urinary_frequency TEXT,
        dysuria TEXT,
        urinary_incontinence INTEGER,
        
        -- Gastrointestinal
        appetite TEXT,
        heartburn TEXT,
        constipation TEXT,
        
        -- Medication Compliance
        medications_taken INTEGER,
        missed_medications TEXT,
        
        -- Additional Fields
        gestational_age TEXT,
        high_risk INTEGER,
        additional_notes TEXT,
        status TEXT,
        condition_type TEXT DEFAULT 'prenatal',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        urgency_status TEXT DEFAULT 'low'
    )
''')

conn.commit()
conn.close()
print('✅ prenatal_entries table created successfully!')