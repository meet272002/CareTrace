from fastapi import APIRouter, HTTPException
from backend.schemas.health_records import HealthRecordCreate
from backend.services.health_records import (
    save_health_record,
    get_patient_health_records
)

router = APIRouter()


@router.post("/records")
def create_record(record: HealthRecordCreate):

    try:
        saved_record = save_health_record(
            patient_id=record.patient_id,
            original_transcript=record.original_transcript,
            english_transcript=record.english_transcript
        )

        return {
            "status": "success",
            "message": "Health record saved successfully.",
            "record": saved_record
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to save health record: {str(error)}"
        )


@router.get("/records/{patient_id}")
def get_records(patient_id: str):

    try:
        records = get_patient_health_records(patient_id)

        return {
            "status": "success",
            "patient_id": patient_id,
            "total_records": len(records),
            "records": records
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve health records: {str(error)}"
        )
