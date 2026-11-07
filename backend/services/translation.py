
import requests

from config.settings import (
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
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json()

        translated_text = (
            result["message"]["content"].strip()
        )

        if not translated_text:
            raise ValueError("Translation returned an empty response.")

        return translated_text

    except requests.ConnectionError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether Ollama is running."
        ) from error

    except requests.Timeout as error:
        raise RuntimeError(
            "Ollama translation timed out."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"Ollama API request failed: {error}"
        ) from error

    except (KeyError, ValueError) as error:
        raise RuntimeError(
            f"Invalid translation response: {error}"
        ) from error
