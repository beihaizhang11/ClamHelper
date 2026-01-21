import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'instance', 'bar.db')
# Check if it's in root or instance
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.getcwd(), 'bar.db')

def migrate():
    print(f"Connecting to database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(consumption)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'event_id' not in columns:
            print("Adding event_id column to consumption table...")
            cursor.execute("ALTER TABLE consumption ADD COLUMN event_id INTEGER REFERENCES event(id)")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column event_id already exists.")
            
    except sqlite3.OperationalError as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
