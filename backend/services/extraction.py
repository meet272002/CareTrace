
import requests

from backend.schemas.health import HealthExtractionResponse
from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)

SYSTEM_PROMPT = """
You are a careful health-information extraction system.

Your task is to extract structured information from
English patient-reported health statements.

IMPORTANT RULES:

1. Extract only information explicitly stated by the patient.
2. Never diagnose or recommend treatment.
3. Never invent symptoms, dates, durations, or severity.
4. Identify every distinct symptom separately.
5. Never combine different symptoms into a generic symptom.
6. Use concise normalized English symptom names.

SYMPTOM IDENTIFICATION:

- headache means headache.
- stomach pain means stomach pain.
- cough means cough.
- fever means fever.
- Do not replace one symptom with another.
- Do not merge multiple symptoms into a single entry.

NEGATION:

- "I do not have a fever" means fever is absent.
- "I have a fever" means fever is present.
- Distinguish absent symptoms from present symptoms.

TEMPORAL INFORMATION:

- "since yesterday" should be extracted as onset.
- "for two days" should be extracted as duration.
- Preserve the stated time expression.
- Do not invent calendar dates.
- Associate temporal information with the correct symptom.

SYMPTOM PATTERNS:

- "The pain was less in the morning and increased
  in the evening" describes one symptom.
- Record this change in the pattern field.
- Do not create duplicate symptoms for different times.
- Do not put explicitly stated patterns in missing_information.

SEVERITY:

- Extract severity only when explicitly mentioned.
- Do not infer severity from the symptom name.

EVIDENCE:

- Every symptom must include the exact English
  phrase from the input that supports its extraction.
- Never create evidence that does not exist in the input.

MISSING INFORMATION:

- Include only useful information that is genuinely missing.
- Do not ask about information already provided.

Return valid JSON matching the supplied schema.
"""

def extract_health_information(
    transcript: str,
    language: str,
) -> HealthExtractionResponse:

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    if language not in ["hi", "gu", "en"]:
        raise ValueError("Language must be 'hi' or 'gu' or 'en'.")

    user_prompt = f"""
        Extract health information from the following transcript.

        Transcript language: {language}

        Transcript:
        <transcript>
        {transcript}
        </transcript>

        Remember:
        - Do not assume missing information.
        - Preserve the original evidence.
        - Return only information supported by the transcript.
    """

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "format": HealthExtractionResponse.model_json_schema(),
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json()

        extracted_json = result["message"]["content"]

        validated_result = HealthExtractionResponse.model_validate_json(
            extracted_json
        )

        return validated_result

    except requests.ConnectionError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Make sure Ollama is running."
        ) from error

    except requests.Timeout as error:
        raise RuntimeError(
            "Ollama extraction timed out."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"Ollama API request failed: {error}"
        ) from error

    except (KeyError, ValueError) as error:
        raise RuntimeError(
            f"Invalid response from Ollama: {error}"
        ) from error
