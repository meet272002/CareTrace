from fastapi import APIRouter, HTTPException

from backend.services.issues import (
    extract_and_store,
    get_patient_issues,
    get_record,
    get_unextracted_records,
)

router = APIRouter()


@router.get("/issues/{patient_id}")
def list_issues(patient_id: str):
    """Issues extracted from a patient's translated records."""
    try:
        return {"status": "success", "patient_id": patient_id, **get_patient_issues(patient_id)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve issues: {error}")


@router.post("/issues/extract/{record_id}")
def extract_one(record_id: int):
    """(Re-)run extraction for a single record."""
    record = get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    result = extract_and_store(record["id"], record["patient_id"], record["english_transcript"])
    return {"record_id": record_id, **result}


@router.post("/issues/{patient_id}/extract-pending")
def extract_pending(patient_id: str):
    """Run extraction for every record that has no successful extraction yet."""
    results = [
        {"record_id": r["id"], **extract_and_store(r["id"], r["patient_id"], r["english_transcript"])}
        for r in get_unextracted_records(patient_id)
    ]
    return {
        "status": "success",
        "processed": len(results),
        "succeeded": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
    }
