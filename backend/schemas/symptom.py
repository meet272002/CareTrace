
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class IdentifiedSymptom(BaseModel):

    name: str

    body_location: Optional[str] = None

    evidence: str

    evidence_status: Literal[
        "verified",
        "needs_review"
    ] = "needs_review"


class SymptomIdentificationResponse(BaseModel):

    symptoms: List[IdentifiedSymptom] = Field(
        default_factory=list
    )
