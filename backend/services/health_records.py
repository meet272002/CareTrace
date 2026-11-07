
from backend.database import get_db_connection


def save_health_record(
    patient_id: str,
    original_transcript: str,
    english_transcript: str
):
    """
    Save a patient's health experience in the database.
    """

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO health_records (
                patient_id,
                original_transcript,
                english_transcript
            )
            VALUES (?, ?, ?)
            """,
            (
                patient_id,
                original_transcript,
                english_transcript
            )
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "patient_id": patient_id,
            "original_transcript": original_transcript,
            "english_transcript": english_transcript
        }

    finally:
        connection.close()


def get_patient_health_records(patient_id: str):
    """
    Retrieve all health records belonging to a patient.
    """

    connection = get_db_connection()

    try:
        records = connection.execute(
            """
            SELECT *
            FROM health_records
            WHERE patient_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (patient_id,)
        ).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()
