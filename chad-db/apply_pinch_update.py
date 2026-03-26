
import sqlite3
import sys
from pathlib import Path

MIGRATION_SQL = Path(__file__).with_name("chad_pinch_migration.sql").read_text(encoding="utf-8")

def main():
    if len(sys.argv) != 2:
        print("Usage: python apply_pinch_update.py <database_file>")
        sys.exit(1)

    db_file = Path(sys.argv[1])
    if not db_file.exists():
        print(f"Database file not found: {db_file}")
        sys.exit(1)

    conn = sqlite3.connect(db_file)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(MIGRATION_SQL)
        conn.commit()
        print(f"Updated database: {db_file}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
