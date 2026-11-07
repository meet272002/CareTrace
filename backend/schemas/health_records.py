
from pydantic import BaseModel, Field


class HealthRecordCreate(BaseModel):
    patient_id: str = Field(min_length=1)
    original_transcript: str = Field(min_length=1)
    english_transcript: str = Field(min_length=1)
