"""One place that talks to the language model (Hugging Face or Ollama).

Used for both translation and health-issue extraction.
"""
import json
import re
from typing import Optional

import requests

from config.settings import (
    HF_BASE_URL,
    HF_MODEL,
    HF_TIMEOUT,
    HF_TOKEN,
    LLM_BACKEND,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)


def _clean(text: str) -> str:
    """Drop <think> blocks (reasoning models) and surrounding whitespace."""
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()


def _strip_fences(text: str) -> str:
    text = _clean(text)
    match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    return (match.group(1) if match else text).strip()


def describe_backend() -> str:
    return f"Hugging Face ({HF_MODEL})" if LLM_BACKEND == "huggingface" else f"Ollama ({OLLAMA_MODEL})"


# ---------------------------------------------------------------- Hugging Face
def _hf_post(payload: dict) -> str:
    response = requests.post(
        f"{HF_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json=payload,
        timeout=HF_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _chat_hf(system: str, user: str, schema: Optional[dict], max_tokens: int) -> str:
    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is not set. Create a Hugging Face access token and set "
            "it as the HF_TOKEN environment variable."
        )

    base = {
        "model": HF_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }

    if schema is None:
        return _clean(_hf_post(base))

    # Structured output: try strict JSON-schema first. Not every provider
    # supports it, so fall back to asking for JSON in the prompt.
    try:
        return _strip_fences(_hf_post({
            **base,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "result", "schema": schema},
            },
        }))
    except requests.HTTPError as error:
        status = error.response.status_code if error.response is not None else 0
        if status in (401, 402, 403, 404, 429) or status >= 500:
            raise
    fallback = {
        **base,
        "messages": [
            {"role": "system", "content": system + "\n\nReturn ONLY valid JSON matching this JSON schema, with no extra text:\n" + json.dumps(schema)},
            {"role": "user", "content": user},
        ],
    }
    return _strip_fences(_hf_post(fallback))


# ---------------------------------------------------------------------- Ollama
def _chat_ollama(system: str, user: str, schema: Optional[dict], max_tokens: int) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "keep_alive": "30m",
        "options": {"temperature": 0, "num_predict": max_tokens},
    }
    if schema is not None:
        payload["format"] = schema
    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT)
    response.raise_for_status()
    return _clean(response.json()["message"]["content"])


# ----------------------------------------------------------------- Public API
def chat(system: str, user: str, *, schema: Optional[dict] = None, max_tokens: int = 900) -> str:
    """Send one system+user prompt to the configured model; return its text.

    Raises RuntimeError with a readable message on any failure.
    """
    try:
        if LLM_BACKEND == "huggingface":
            return _chat_hf(system, user, schema, max_tokens)
        return _chat_ollama(system, user, schema, max_tokens)

    except requests.ConnectionError as error:
        target = "Hugging Face" if LLM_BACKEND == "huggingface" else "Ollama. Make sure Ollama is running"
        raise RuntimeError(f"Cannot connect to {target}.") from error
    except requests.Timeout as error:
        raise RuntimeError(f"{describe_backend()} timed out.") from error
    except requests.HTTPError as error:
        status = error.response.status_code if error.response is not None else "?"
        hints = {
            401: "Invalid or missing HF_TOKEN.",
            402: "Hugging Face credits/quota used up.",
            403: "Token lacks permission for Inference Providers.",
            404: f"Model '{HF_MODEL}' not found or not served by any provider.",
            429: "Rate limited by Hugging Face; try again shortly.",
        }
        raise RuntimeError(f"{describe_backend()} returned HTTP {status}. {hints.get(status, '')}".strip()) from error
    except (KeyError, IndexError, ValueError) as error:
        raise RuntimeError(f"Unexpected response from {describe_backend()}: {error}") from error
    except requests.RequestException as error:
        raise RuntimeError(f"{describe_backend()} request failed: {error}") from error
