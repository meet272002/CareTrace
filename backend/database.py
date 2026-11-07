
import sqlite3
from pathlib import Path

# Locate the CareTrace project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Define database directory
DATABASE_DIR = BASE_DIR / "data"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Define database path
DATABASE_PATH = DATABASE_DIR / "caretrace.db"


def get_db_connection():
    """
    Create and return a connection to the CareTrace database.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_health_records_table():
    """
    Create the health_records table if it does not exist.
    """

    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS health_records (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                patient_id TEXT NOT NULL,

                original_transcript TEXT NOT NULL,

                english_transcript TEXT NOT NULL,

                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')
                )
            )
        """)

        connection.commit()

        print("Health records table created successfully!")

    finally:
        connection.close()
