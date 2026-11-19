# CareTrace: A Voice-Enabled AI Assistant for Personal Health Timeline Generation

CareTrace is a voice-enabled AI assistant designed to help users organize their personal health experiences into a chronological health history and, eventually, a structured summary for medical appointments.

Users can narrate their health experiences in **Hindi or Gujarati**. The system converts speech into text, translates it into English, and stores the information for future retrieval.

The project aims to make it easier for individuals to maintain and communicate their health history systematically.

---

## 1. Project Overview

People may find it difficult to remember and communicate the sequence of their symptoms, when they started, how they changed, and what other relevant circumstances occurred.

CareTrace addresses this problem through voice-based input and AI-assisted organization of personal health information.

The current prototype supports:

- Voice recording and audio file uploads.
- Hindi and Gujarati speech transcription.
- Translation of transcripts into English.
- Persistent storage of original and translated transcripts.
- Retrieval and display of previously stored health records.
- Automatic extraction of health issues (symptom, when it started, duration, severity, pattern) from the English text, shown in its own tab.

The longer-term objective is to generate chronological health timelines and structured appointment summaries.

## 2. Problem Statement

People often struggle to maintain a consistent record of their health experiences. Information may be spread across conversations, notes, or personal recollections.

Manually organizing this information can be inconvenient, particularly when someone needs to explain their health history during a medical appointment.

CareTrace aims to provide a simple voice-based interface that helps users record, organize, and retrieve their reported health experiences.

## 3. Project Objectives

- Enable users to narrate their health experiences in Hindi or Gujarati.
- Convert recorded speech into text.
- Translate the original transcript into English.
- Store health experiences with timestamps and patient identifiers.
- Retrieve previously stored health records.
- Extract relevant health events, symptoms, time expressions, and contextual information.
- Organize extracted events into a chronological timeline.
- Generate structured, editable summaries for medical appointments.
- Preserve uncertainty and avoid inventing missing information.
- Evaluate the accuracy and usability of the generated timeline and summary.

## 4. Current Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit (3 tabs: Record, Translated Records, Health Issues) |
| Backend | FastAPI |
| Speech Recognition (default) | AI4Bharat **IndicConformer 600M** (Hindi/Gujarati), via Hugging Face `transformers` |
| Speech Recognition (fallback) | Faster-Whisper `large-v3-turbo` |
| Translation + issue extraction | Local Ollama (`qwen2.5:3b`, default) **or** Hugging Face Inference Providers (`Qwen/Qwen3-32B`, optional, paid) |
| Database | SQLite |
| Data Validation | Pydantic |
| HTTP Communication | Requests |
| Testing | Pytest |

### Architecture

- **Streamlit:** user interaction, language selection, recording, and the three tabs.
- **FastAPI:** API requests, audio processing, transcription, translation, extraction, database.
- **IndicConformer / Faster-Whisper:** speech to text. If IndicConformer cannot load, the backend falls back to Whisper and prints a `[WARNING]`.
- **Language model (Hugging Face or Ollama):** translates to English and extracts health issues. One shared client (`backend/services/llm.py`) is used for both.
- **SQLite:** stores records, extracted issues and extraction status.

At backend start-up both models are loaded **before** the server accepts requests, so the first recording is as fast as later ones.

## 5. Current Development Workflow

1. **Patient Identification:** temporary patient ID (`001`).
2. **Language Selection:** Hindi or Gujarati.
3. **Voice Input:** record or upload audio (wav, mp3, m4a).
4. **Speech-to-Text:** IndicConformer (or Whisper) creates the original transcript.
5. **English Translation:** the language model translates the transcript.
6. **Storage:** both transcripts are saved to SQLite. The request returns immediately.
7. **Issue Extraction (background):** issues are extracted from the English text and stored with the exact supporting phrase. If the phrase is not found in the transcript the issue is flagged "please review". If extraction fails the record is still safe; use **Analyse pending records** in the Health Issues tab to retry.
8. **UI:** *Translated Records* tab shows original + English text; *Health Issues* tab shows issue cards (live "Analysing..." while running).

### Planned Workflow

1. Chronological timeline generation.
2. Structured appointment summary generation.
3. Editable transcript and timeline review.
4. Exporting summaries for medical appointments.
5. Patient authentication and secure access control.

## 6. Project Structure

```text
CareTrace/
├── backend/
│   ├── main.py                  # app, start-up (DB tables, model preload)
│   ├── database.py              # SQLite connection + table creation
│   ├── api/
│   │   ├── routes.py            # /health, /transcribe
│   │   ├── records_routes.py    # /records
│   │   └── issues_routes.py     # /issues
│   ├── schemas/                 # Pydantic models
│   └── services/
│       ├── transcription.py     # IndicConformer + Whisper
│       ├── translation.py
│       ├── extraction.py        # prompt + schema for issue extraction
│       ├── issues.py            # store/read extracted issues
│       ├── llm.py               # Hugging Face / Ollama client
│       ├── status.py            # model status shown in the sidebar
│       └── health_records.py
├── frontend/
│   ├── app.py                   # Streamlit UI
│   └── app_client.py            # HTTP calls to the backend
├── config/settings.py           # all settings (read from environment variables)
├── .streamlit/config.toml       # dark theme
├── test/                        # pytest
├── data/caretrace.db            # created automatically, not committed
├── requirements.txt
└── README.md
```

## 7. Installation and Setup

Instructions for a new Windows computer.

### Prerequisites

- Python 3.10+ and Git.
- A Hugging Face account (free) - needed to download the speech model.
- Optional: [Ollama](https://ollama.com/download) if you want fully local translation/extraction.
- Plenty of RAM/disk: the speech and Whisper models are large downloads on first run.

### Step 1: Clone and enter the project

```powershell
git clone https://github.com/meet272002/CareTrace.git
cd CareTrace
git checkout flashy-ui-whisper-turbo    # until the pull request is merged into main
```

### Step 2: Virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Speech model access (IndicConformer, one time)

The model is gated on Hugging Face.

1. Open https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual, log in and accept the terms.
2. Run `hf auth login` and paste a token (create one at https://huggingface.co/settings/tokens).
3. The first backend start downloads the model; later starts load it from disk.

Without access the backend prints `[WARNING] IndicConformer failed...` and falls back to Whisper (weaker on Gujarati).

### Step 5: Choose the language model (translation + extraction)

| Option | When to use | Setup |
|---|---|---|
| **Ollama** (local, **default**) | Free and fully private, but slow on CPU | `ollama pull qwen2.5:3b` and keep Ollama running |
| **Hugging Face** (optional) | Fast, better quality, no local model | `$env:LLM_BACKEND="huggingface"` plus a token with Inference Providers credits (see warning below) |

**Hugging Face warning:** Inference Providers is a paid service. Free accounts get only about $0.10 of monthly credits, which runs out after a few calls; then every request fails with `HTTP 402`. Buy pre-paid credits or subscribe to PRO (about $9/month), or use Ollama. A new token on the same account does not help; credits belong to the account.

When `LLM_BACKEND=huggingface`, the backend uses the token from the `HF_TOKEN` environment variable, otherwise the one saved by `hf auth login`. If `HF_TOKEN` is set it wins over the saved login. Downloading the speech model from the Hub is free and unrelated to these paid credits.

**Privacy:** with Hugging Face the transcribed *text* (not the audio) is sent to a third-party service. Use Ollama if that is not acceptable.

### Step 6: Settings (environment variables)

`.env` files are **not** read by the code. Set variables in the PowerShell window where you start the backend, e.g. `$env:LLM_BACKEND="ollama"`. They last only for that window.

| Variable | Default | Meaning |
|---|---|---|
| `LLM_BACKEND` | `ollama` | `ollama` (local) or `huggingface` (hosted, paid credits) |
| `HF_TOKEN` | saved `hf auth login` token | Hugging Face token (never commit it) |
| `HF_MODEL` | `Qwen/Qwen3-32B` | Hosted chat model; can pin a provider, e.g. `openai/gpt-oss-120b:groq` |
| `HF_TIMEOUT` | `120` | Seconds to wait for Hugging Face |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Local model (try `qwen2.5:7b` for quality) |
| `OLLAMA_TIMEOUT` | `300` | Seconds to wait for a translation |
| `OLLAMA_EXTRACT_TIMEOUT` | `900` | Seconds to wait for issue extraction (runs in the background) |
| `OLLAMA_NUM_CTX` | `3072` | Context size; smaller is faster on CPU |
| `ASR_BACKEND` | `indic_conformer` | Set `whisper` to force Whisper |
| `INDIC_DECODER` | `ctc` | `rnnt` is the alternate decoder |
| `WHISPER_MODEL` | `large-v3-turbo` | e.g. `small` for a faster, lighter Whisper |
| `WHISPER_DEVICE` / `WHISPER_COMPUTE_TYPE` | `cpu` / `int8` | Use `cuda` / `float16` on a GPU |
| `PRELOAD_BLOCKING` | `1` | `0` = start the API immediately and load models in the background |

### Step 7: Start the backend

From the project root, with the environment active:

```powershell
python -m uvicorn backend.main:app
```

Wait for `Models loaded. CareTrace backend is ready.` (the first start can take several minutes). Avoid `--reload` while testing audio: every file save restarts the server and reloads the models.

API docs: http://127.0.0.1:8000/docs

### Step 8: Start the frontend

In a second terminal (activate the environment first):

```powershell
streamlit run frontend/app.py
```

Open http://localhost:8501. The sidebar shows backend and model status.

## 8. API Endpoints

The FastAPI backend currently exposes the following endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome message |
| GET | `/api/v1/health` | Check backend availability |
| POST | `/api/v1/transcribe` | Transcribe, translate, and save an audio recording |
| POST | `/api/v1/records` | Save a health record directly |
| GET | `/api/v1/records/{patient_id}` | Retrieve a patient's health records |
| GET | `/api/v1/issues/{patient_id}` | Issues (symptom, onset, duration, severity, pattern, evidence) extracted from the translated records |
| POST | `/api/v1/issues/extract/{record_id}` | (Re-)run extraction for one record |
| POST | `/api/v1/issues/{patient_id}/extract-pending` | Extract for all records not yet analysed |

### Audio Transcription API

Endpoint:

```text
POST /api/v1/transcribe
```

Parameters:

- `language`: `hi` or `gu`
- `audio`: Uploaded audio file.

The endpoint processes the audio, generates an original transcript, translates it into English, and saves both transcripts.

### Health Record Retrieval API

Endpoint:

```text
GET /api/v1/records/001
```

Retrieves all records associated with the temporary patient ID `001`, ordered by creation time.

## 9. Database Design

SQLite file: `data/caretrace.db` (created automatically on backend start).

### `health_records`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Record id |
| `patient_id` | TEXT | Patient id (temporary `001`) |
| `original_transcript` | TEXT | Hindi/Gujarati transcript |
| `english_transcript` | TEXT | English translation |
| `created_at` | TEXT | When the record was saved |

### `health_issues`

One row per symptom/issue: `record_id`, `patient_id`, `name`, `status` (present / absent / unclear), `onset`, `duration`, `severity`, `pattern`, `evidence` (exact supporting phrase), `evidence_verified` (0/1).

### `record_extractions`

One row per record: `status` (`success` / `failed`), `error`, `additional_context`, `missing_information`, `extracted_at`.

"When" a problem started is stored as the patient said it ("since yesterday", "for two days"), together with the record's save time. Phrases are not converted to calendar dates, to avoid guessing.

The patient ID is hardcoded for the prototype:

```python
PATIENT_ID = "001"
```

## 10. Running the Project - Quick Reference

Two terminals, both in the project root with the environment activated.

**Terminal 1 - Backend** (wait for "CareTrace backend is ready")

```powershell
.\.venv\Scripts\Activate.ps1
# optional, hosted model: $env:LLM_BACKEND="huggingface"; $env:HF_TOKEN="hf_..."
python -m uvicorn backend.main:app
```

**Terminal 2 - Frontend**

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

If you use Ollama, make sure it is running and `qwen2.5:3b` is pulled.

Run the tests (mocked, no models needed): `python -m pytest test -q`

## 11. Troubleshooting

**Backend connection error / "Backend offline"** - the backend is still loading models (wait for the "ready" line) or not running. Check http://127.0.0.1:8000/api/v1/health.

**`ImportError: cannot import name 'get_patient_issues' from 'app_client'`** - your files are from different versions. Pull the whole branch (`git pull`) and restart both the backend and Streamlit.

**`git pull` says local changes would be overwritten** - `git stash`, `git pull`, `git stash pop`.

**Extraction failed: `HTTP 402` / "credits used up"** - the Hugging Face account has no Inference Providers credits (free accounts get only about $0.10 a month). Buy credits/PRO or switch back to Ollama (the default; remove `LLM_BACKEND=huggingface`). A new token on the same account will not help. After fixing, open the Health Issues tab and click **Analyse pending records**. Test a token directly:

```powershell
python -c "import requests; from config.settings import HF_TOKEN; r=requests.post('https://router.huggingface.co/v1/chat/completions', headers={'Authorization':'Bearer '+HF_TOKEN}, json={'model':'Qwen/Qwen3-32B','messages':[{'role':'user','content':'hi'}],'max_tokens':5}); print(HF_TOKEN[:7]+'...', r.status_code, r.text[:200])"
```

`200` means the token works. To use a different account: clear `HF_TOKEN` (`Remove-Item Env:HF_TOKEN`), run `hf auth login --force`, confirm with `hf auth whoami`, restart the backend.

**Extraction failed: `401` / `403` / `404` / `429`** - bad or missing token, token without Inference Providers permission, model not available (set another `HF_MODEL`), or rate limiting. The Health Issues tab shows the reason.

**Extraction failed: "Ollama ... timed out"** - the local model is slow on CPU. Extraction already uses a short prompt, a small output and a 15-minute timeout; raise `OLLAMA_EXTRACT_TIMEOUT` further, check `ollama ps` that the model is loaded (and on GPU if you have one), or use a faster machine/Hugging Face (with credits).

**`huggingface-cli` is deprecated** - use `hf auth login`.

**`[WARNING] IndicConformer failed`** - you have not accepted the model terms or logged in (Step 4), or there is not enough memory. The backend falls back to Whisper meanwhile.

**Transcript or translation is poor, especially Gujarati** - Whisper is weak on Gujarati; make sure IndicConformer loaded (sidebar: "Speech model: ready: IndicConformer"). For translation, a larger model helps.

**The first recording takes very long** - models were still loading. Start the backend and wait for "Models loaded" before recording.

**Python module import errors** - run commands from the project root with `python -m uvicorn backend.main:app`, with the virtual environment active.

**Records are not appearing** - check that the backend started and `data/caretrace.db` exists.

## 12. Evaluation Plan

The prototype will be evaluated using fictional health scenarios and, where appropriate, consented test data.

Key evaluation criteria include:

- **Transcription Accuracy:** How accurately Hindi and Gujarati speech is converted into text.
- **Translation Quality:** Whether the English translation preserves the meaning of the original narration.
- **Extraction Accuracy:** Whether relevant symptoms, events, and contextual details are identified correctly.
- **Chronological Accuracy:** Whether events are placed in the correct order.
- **Uncertainty Preservation:** Whether unknown dates and ambiguous details remain explicitly uncertain.
- **Unsupported Inference:** Whether the system avoids adding information that the user did not provide.
- **Usability:** Whether users can understand and use the generated timeline and summary.

## 13. Safety and Privacy Considerations

CareTrace is intended to organize user-reported health information. It does not provide medical diagnoses or treatment recommendations.

The system should:

- Preserve original transcripts as a source of truth.
- Avoid presenting generated information as a medical diagnosis.
- Preserve uncertainty instead of guessing missing information.
- Allow users to review and correct generated information as those features are implemented.
- Protect recordings and health information from unauthorized access.
- Avoid committing API keys, recordings, database files, or sensitive health information to version control.
- Use fictional sample scenarios during early development.
- Be aware that with the Hugging Face option the transcribed text is sent to a third-party service (audio stays local). Use Ollama for fully local processing.
- Never commit tokens (`HF_TOKEN`) to Git.

**Current prototype limitation:** Authentication and patient-level access control have not yet been implemented. The patient ID `001` is temporary, and the current database API must not be used to store real patient information in an exposed deployment.

## 14. Current Development Status

| Feature | Status |
|---|---|
| Initial project structure | Completed |
| Streamlit frontend | Implemented |
| FastAPI backend | Implemented |
| Hindi speech transcription | Implemented |
| Gujarati speech transcription | Implemented |
| English translation (Hugging Face or Ollama) | Implemented |
| SQLite database setup | Implemented |
| Health record storage | Implemented |
| Patient ID association | Implemented using temporary ID `001` |
| Existing health history retrieval | Implemented |
| Automatic UI refresh after saving | Implemented in current integration |
| Patient registration and login | Not implemented |
| Structured health issue extraction + Health Issues tab | Implemented (background task, evidence check) |
| Flashy UI with 3 tabs | Implemented |
| IndicConformer speech model with Whisper fallback | Implemented |
| Chronological timeline generation | Planned |
| Appointment summary generation | Planned |
| User editing and validation | Planned |
| Secure patient access control | Planned |

*Implementation status should be updated as features are integrated and tested.*

## 15. Future Enhancements

Potential future improvements include:

- Patient registration and authentication.
- Secure patient-specific health record access.
- Structured extraction of symptoms, events, and time expressions.
- Improved handling of relative dates and uncertain timelines.
- Chronological health timeline visualization.
- Editable appointment summaries.
- PDF export for medical appointments.
- Additional Indian language support.
- Better privacy, data retention, and deletion controls.

---

**Project Name:** CareTrace  
**Project Focus:** Voice-enabled personal health timeline generation  
**Initial Languages:** Hindi and Gujarati  
**Frontend:** Streamlit  
**Backend:** FastAPI  
**Database:** SQLite  
**Primary Goal:** Help users organize and communicate their reported health history more clearly.
