import json
import re
from typing import Dict, List

from backend.database import get_db_connection
from backend.schemas.health import HealthExtractionResponse
from backend.services.extraction import extract_health_information



def _contains(transcript: str, evidence: str) -> bool:
    """True if the evidence phrase really appears in the transcript."""
    words = lambda t: re.sub(r"[^\w\s]", " ", (t or "").lower()).split()
    needle, haystack = words(evidence), words(transcript)
    if not needle:
        return False
    n = len(needle)
    return any(haystack[i:i + n] == needle for i in range(len(haystack) - n + 1))


def save_extraction(
    record_id: int,
    patient_id: str,
    english_transcript: str,
    extraction: HealthExtractionResponse,
) -> int:
    """Replace any earlier extraction of this record with a new one."""
    connection = get_db_connection()
    try:
        connection.execute("DELETE FROM health_issues WHERE record_id = ?", (record_id,))
        connection.execute("DELETE FROM record_extractions WHERE record_id = ?", (record_id,))

        for symptom in extraction.symptoms:
            connection.execute(
                """
                INSERT INTO health_issues (
                    record_id, patient_id, name, status, onset, duration,
                    severity, pattern, evidence, evidence_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id, patient_id, symptom.name.strip(), symptom.status,
                    symptom.onset, symptom.duration, symptom.severity,
                    symptom.pattern, symptom.evidence,
                    int(_contains(english_transcript, symptom.evidence)),
                ),
            )

        connection.execute(
            """
            INSERT INTO record_extractions (
                record_id, patient_id, status, additional_context, missing_information
            ) VALUES (?, ?, 'success', ?, ?)
            """,
            (
                record_id, patient_id,
                json.dumps(extraction.additional_context),
                json.dumps(extraction.missing_information),
            ),
        )
        connection.commit()
        return len(extraction.symptoms)
    finally:
        connection.close()


def save_extraction_failure(record_id: int, patient_id: str, error: str) -> None:
    connection = get_db_connection()
    try:
        connection.execute("DELETE FROM record_extractions WHERE record_id = ?", (record_id,))
        connection.execute(
            "INSERT INTO record_extractions (record_id, patient_id, status, error) "
            "VALUES (?, ?, 'failed', ?)",
            (record_id, patient_id, error[:500]),
        )
        connection.commit()
    finally:
        connection.close()


def extract_and_store(record_id: int, patient_id: str, english_transcript: str) -> Dict:
    """
    Run extraction on one translated record and store the result.
    Never raises: a failure is stored so the record itself is never lost.
    """
    try:
        extraction = extract_health_information(english_transcript, "en")
        count = save_extraction(record_id, patient_id, english_transcript, extraction)
        return {"status": "success", "issue_count": count}
    except Exception as error:  # noqa: BLE001
        save_extraction_failure(record_id, patient_id, str(error))
        return {"status": "failed", "issue_count": 0, "error": str(error)}


def get_record(record_id: int):
    connection = get_db_connection()
    try:
        row = connection.execute(
            "SELECT * FROM health_records WHERE id = ?", (record_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def get_unextracted_records(patient_id: str) -> List[dict]:
    """Records that have no successful extraction yet (new, old, or failed)."""
    connection = get_db_connection()
    try:
        rows = connection.execute(
            """
            SELECT r.* FROM health_records r
            LEFT JOIN record_extractions e ON e.record_id = r.id
            WHERE r.patient_id = ? AND (e.record_id IS NULL OR e.status != 'success')
            ORDER BY r.id
            """,
            (patient_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_patient_issues(patient_id: str) -> Dict:
    """All issues for a patient, newest report first, with when they were reported."""
    connection = get_db_connection()
    try:
        issues = connection.execute(
            """
            SELECT i.*, r.created_at AS reported_at
            FROM health_issues i
            JOIN health_records r ON r.id = i.record_id
            WHERE i.patient_id = ?
            ORDER BY r.created_at DESC, i.id
            """,
            (patient_id,),
        ).fetchall()

        extractions = connection.execute(
            "SELECT * FROM record_extractions WHERE patient_id = ?", (patient_id,)
        ).fetchall()
    finally:
        connection.close()

    context = {}
    for row in extractions:
        context[row["record_id"]] = {
            "status": row["status"],
            "error": row["error"],
            "additional_context": json.loads(row["additional_context"] or "[]"),
            "missing_information": json.loads(row["missing_information"] or "[]"),
        }

    return {
        "issues": [dict(i, evidence_verified=bool(i["evidence_verified"])) for i in issues],
        "extractions": context,
        "pending_records": len(get_unextracted_records(patient_id)),
    }
