import sqlite3
from pathlib import Path

DB_FILE = "wrist_device.db"
SCHEMA_FILE = "schema.sql"
SEED_FILE = "seed.sql"

def run_sql_file(cursor, filename):
    print(f"Running {filename}...")
    with open(filename, "r", encoding="utf-8") as f:
        sql = f.read()
    cursor.executescript(sql)
    print(f"Finished {filename}")

def main():
    print("Starting database setup...")

    db_exists = Path(DB_FILE).exists()
    print(f"Database already exists: {db_exists}")

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        run_sql_file(cursor, SCHEMA_FILE)
        run_sql_file(cursor, SEED_FILE)

        conn.commit()
        conn.close()

        if db_exists:
            print(f"Database updated: {DB_FILE}")
        else:
            print(f"Database created: {DB_FILE}")

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()