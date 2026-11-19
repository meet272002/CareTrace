from typing import List

from pydantic import BaseModel, Field

from backend.schemas.health import HealthExtractionResponse, Symptom
from backend.services.llm import chat
from config.settings import OLLAMA_EXTRACT_TIMEOUT

# Short prompt: on CPU every prompt and output token costs time.
SYSTEM_PROMPT = """Extract health issues from an English patient statement as JSON.

Rules:
- Use only what the patient says. Never diagnose or invent anything.
- One entry per distinct symptom, with a short normalized name (e.g. "headache").
- status: "present", or "absent" when negated ("I do not have a fever"), else "unclear".
- onset = when it started ("since yesterday"); duration = how long ("two days");
  pattern = how it changes (e.g. "less in the morning, worse in the evening");
  severity only if stated. Leave other fields out. No calendar dates.
- evidence = the exact words from the statement that support the entry.
- missing_information = at most 3 short useful details not stated (or empty).
"""


class _LiteExtraction(BaseModel):
    """Smaller output than HealthExtractionResponse: fewer tokens to generate."""

    symptoms: List[Symptom] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


def extract_health_information(
    transcript: str,
    language: str,
) -> HealthExtractionResponse:

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    if language not in ["hi", "gu", "en"]:
        raise ValueError("Language must be 'hi' or 'gu' or 'en'.")

    content = chat(
        SYSTEM_PROMPT,
        f"Statement:\n{transcript.strip()}",
        schema=_LiteExtraction.model_json_schema(),
        max_tokens=700,
        timeout=OLLAMA_EXTRACT_TIMEOUT,
    )

    try:
        lite = _LiteExtraction.model_validate_json(content)
    except ValueError as error:
        raise RuntimeError(f"Invalid extraction response from the model: {error}") from error

    return HealthExtractionResponse(
        language=language,
        symptoms=lite.symptoms,
        missing_information=lite.missing_information,
    )
