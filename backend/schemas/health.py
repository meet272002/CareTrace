from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    service: str

class Symptom(BaseModel):
    name: str = Field(
        description="Name of the symptom reported by the user"
    )

    onset: Optional[str] = Field(
        default=None,
        description="When the symptom started, as reported by the user"
    )

    duration: Optional[str] = None

    severity: Optional[str] = None

    pattern: Optional[str] = Field(
        default=None,
        description="How the symptom changes over time"
    )

    status: Literal[
        "present",
        "absent",
        "unclear"
    ] = "unclear"

    evidence: str = Field(
        description="Original transcript phrase supporting this information"
    )

class HealthExtractionResponse(BaseModel):
    language: str

    symptoms: List[Symptom] = Field(
        default_factory=list
    )

    additional_context: List[str] = Field(
        default_factory=list
    )

    missing_information: List[str] = Field(
        default_factory=list
    )