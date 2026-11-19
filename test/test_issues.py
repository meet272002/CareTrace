import pytest
from fastapi.testclient import TestClient

import backend.database as db
from backend.main import app
from backend.schemas.health import HealthExtractionResponse, Symptom
from backend.services import issues as issues_service
from backend.services.health_records import save_health_record

TEXT = "I have had a cough for two days and I do not have a fever."


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "t.db")
    db.create_health_records_table()
    db.create_health_issues_tables()
    return TestClient(app)


def fake_extract(transcript, language):
    return HealthExtractionResponse(
        language="en",
        symptoms=[
            Symptom(name="cough", duration="two days", status="present",
                    evidence="a cough for two days"),
            Symptom(name="fever", status="absent", evidence="do not have a fever"),
            Symptom(name="headache", status="present", evidence="made up phrase"),
        ],
        missing_information=["severity of cough"],
    )


def test_extract_and_list(client, monkeypatch):
    monkeypatch.setattr(issues_service, "extract_health_information", fake_extract)
    rec = save_health_record("001", "orig", TEXT)

    r = client.post(f"/api/v1/issues/extract/{rec['id']}")
    assert r.json()["status"] == "success" and r.json()["issue_count"] == 3

    data = client.get("/api/v1/issues/001").json()
    by_name = {i["name"]: i for i in data["issues"]}
    assert by_name["cough"]["duration"] == "two days"
    assert by_name["cough"]["evidence_verified"] is True
    assert by_name["fever"]["status"] == "absent"
    assert by_name["headache"]["evidence_verified"] is False  # invented evidence flagged
    assert by_name["cough"]["reported_at"]
    assert data["pending_records"] == 0


def test_failure_is_stored_and_retried(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("Cannot connect to Ollama.")

    monkeypatch.setattr(issues_service, "extract_health_information", boom)
    save_health_record("001", "orig", TEXT)

    assert client.get("/api/v1/issues/001").json()["pending_records"] == 1
    out = client.post("/api/v1/issues/001/extract-pending").json()
    assert out["failed"] == 1

    monkeypatch.setattr(issues_service, "extract_health_information", fake_extract)
    out = client.post("/api/v1/issues/001/extract-pending").json()
    assert out["succeeded"] == 1
    assert client.get("/api/v1/issues/001").json()["pending_records"] == 0


def test_reextract_replaces_old_issues(client, monkeypatch):
    monkeypatch.setattr(issues_service, "extract_health_information", fake_extract)
    rec = save_health_record("001", "orig", TEXT)
    client.post(f"/api/v1/issues/extract/{rec['id']}")
    client.post(f"/api/v1/issues/extract/{rec['id']}")
    assert len(client.get("/api/v1/issues/001").json()["issues"]) == 3


def test_unknown_record_404(client):
    assert client.post("/api/v1/issues/extract/999").status_code == 404


def test_processing_flag_and_background_not_pending(client, monkeypatch):
    from backend.services.issues import mark_processing, _in_progress
    rec = save_health_record("001", "orig", TEXT)
    mark_processing(rec["id"], "001")
    try:
        data = client.get("/api/v1/issues/001").json()
        assert data["processing"] == 1 and data["pending_records"] == 0
    finally:
        _in_progress.clear()
    assert client.get("/api/v1/issues/001").json()["pending_records"] == 1
