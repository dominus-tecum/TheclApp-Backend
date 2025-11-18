import sqlite3

conn = sqlite3.connect('hospiapp.db')
cursor = conn.cursor()

try:
    # Add condition_type column to general_entries table
    cursor.execute('ALTER TABLE general_entries ADD COLUMN condition_type TEXT DEFAULT "general_health"')
    conn.commit()
    print('✅ condition_type column added to general_entries table')
    
except Exception as e:
    print(f'❌ Error adding column: {e}')
    
finally:
    conn.close()