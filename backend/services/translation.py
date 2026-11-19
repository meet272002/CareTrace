
import requests

from backend.services.llm import chat, describe_backend
from config.settings import (
    LLM_BACKEND,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)


SUPPORTED_LANGUAGES = {
    "gu": "Gujarati",
    "hi": "Hindi",
}


SYSTEM_PROMPT = """
You are a professional Gujarati and Hindi to English
translator specializing in faithful translation of
patient-reported health statements.

Your ONLY task is translation.
Do not summarize, interpret, diagnose, or rewrite.

STRICT TRANSLATION RULES:

1. Preserve every symptom exactly as described.
2. Never replace a symptom with an unrelated word.
3. Preserve body locations.
4. Preserve negation.
5. Preserve duration and onset expressions.
6. Preserve the relationship between symptoms and time.
7. Do not transfer a duration from one symptom to another.
8. Do not add or remove medical information.
9. If the source is ambiguous, translate it literally.
10. Never guess what the patient intended to say.

IMPORTANT GUJARATI VOCABULARY:

- દુખાવો = pain
- માથું દુખે છે = headache / head pain
- પેટમાં દુખે છે = stomach pain
- ઉધરસ = cough
- તાવ = fever
- નથી = do not have / does not exist
- કાલથી = since yesterday
- બે દિવસથી = for two days
- સવારે = in the morning
- સાંજે = in the evening
- ઓછો = less / reduced
- વધી ગયો = increased

EXAMPLES:

Gujarati:
"સવારે દુખાવો ઓછો હતો, સાંજે વધી ગયો."

English:
"The pain was less in the morning and increased
in the evening."

Gujarati:
"મને બે દિવસથી ઉધરસ છે અને તાવ પણ છે."

English:
"I have had a cough for two days, and I also have
a fever."

Gujarati:
"મને તાવ નથી."

English:
"I do not have a fever."

Return ONLY the English translation.
"""

def translate_to_english(
    transcript: str,
    language: str,
) -> str:

    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            "Language must be 'gu' or 'hi'."
        )

    language_name = SUPPORTED_LANGUAGES[language]

    user_prompt = f"""
Translate the following {language_name} patient statement
into English.

Original statement:
{transcript}

Return only the English translation.
"""

    translated_text = chat(SYSTEM_PROMPT, user_prompt, max_tokens=600)

    if not translated_text:
        raise RuntimeError("Translation returned an empty response.")

    return translated_text


def preload_translation_model() -> None:
    """Warm the translator. Hosted models need no loading; Ollama is asked to
    load its model into memory and keep it there."""
    from backend.services.status import MODEL_STATUS

    if LLM_BACKEND == "huggingface":
        MODEL_STATUS["translator"] = f"ready: {describe_backend()}"
        return

    MODEL_STATUS["translator"] = f"loading {OLLAMA_MODEL}"
    try:
        requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "keep_alive": "30m"},
            timeout=OLLAMA_TIMEOUT,
        )
        MODEL_STATUS["translator"] = f"ready: {OLLAMA_MODEL}"
    except requests.RequestException as error:
        MODEL_STATUS["translator"] = "Ollama not reachable"
        print(f"[WARNING] Ollama preload skipped: {error}")
