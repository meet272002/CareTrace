
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


def create_health_issues_tables():
    """
    Create tables that store information extracted from translated records.

    record_extractions: one row per record (status of the extraction run)
    health_issues:      one row per symptom/issue found in a record
    """

    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS record_extractions (
                record_id INTEGER PRIMARY KEY,
                patient_id TEXT NOT NULL,
                status TEXT NOT NULL,               -- 'success' or 'failed'
                error TEXT,
                additional_context TEXT NOT NULL DEFAULT '[]',   -- JSON list
                missing_information TEXT NOT NULL DEFAULT '[]',  -- JSON list
                extracted_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')
                ),
                FOREIGN KEY (record_id) REFERENCES health_records(id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS health_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                patient_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,               -- present / absent / unclear
                onset TEXT,
                duration TEXT,
                severity TEXT,
                pattern TEXT,
                evidence TEXT NOT NULL,
                evidence_verified INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (record_id) REFERENCES health_records(id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_patient "
            "ON health_issues(patient_id)"
        )

        connection.commit()

    finally:
        connection.close()
