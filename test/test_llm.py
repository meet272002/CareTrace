import json

import pytest
import requests

import backend.services.llm as llm
from backend.schemas.health import HealthExtractionResponse
from backend.services import extraction, translation


class Resp:
    def __init__(self, status=200, content="", ):
        self.status_code = status
        self._content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


@pytest.fixture(autouse=True)
def hf(monkeypatch):
    monkeypatch.setattr(llm, "LLM_BACKEND", "huggingface")
    monkeypatch.setattr(llm, "HF_TOKEN", "hf_test")


def test_translation_strips_think_and_sends_token(monkeypatch):
    seen = {}

    def post(url, headers=None, json=None, timeout=None):
        seen.update(url=url, auth=headers["Authorization"], body=json)
        return Resp(content="<think>hmm</think>I have a fever.")

    monkeypatch.setattr(llm.requests, "post", post)
    assert translation.translate_to_english("મને તાવ છે", "gu") == "I have a fever."
    assert seen["url"].endswith("/chat/completions") and seen["auth"] == "Bearer hf_test"


GOOD = json.dumps({"language": "en", "symptoms": [
    {"name": "fever", "status": "present", "evidence": "I have a fever"}]})


def test_extraction_falls_back_when_json_schema_rejected(monkeypatch):
    calls = []

    def post(url, headers=None, json=None, timeout=None):
        calls.append("response_format" in json)
        return Resp(422) if "response_format" in json else Resp(content="```json\n" + GOOD + "\n```")

    monkeypatch.setattr(llm.requests, "post", post)
    result = extraction.extract_health_information("I have a fever", "en")
    assert isinstance(result, HealthExtractionResponse) and result.symptoms[0].name == "fever"
    assert calls == [True, False]


def test_missing_token_and_http_errors_are_readable(monkeypatch):
    monkeypatch.setattr(llm, "HF_TOKEN", "")
    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        translation.translate_to_english("x", "gu")

    monkeypatch.setattr(llm, "HF_TOKEN", "hf_test")
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: Resp(402))
    with pytest.raises(RuntimeError, match="credits"):
        translation.translate_to_english("x", "gu")
