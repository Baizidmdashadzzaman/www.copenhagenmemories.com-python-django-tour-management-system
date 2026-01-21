import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    target_tables = ['accounts_tourpricing']
    for table_name in target_tables:
        print(f"\n--- Table: {table_name} ---")
        try:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"{col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error reading {table_name}: {e}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
