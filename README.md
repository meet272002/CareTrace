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
| Frontend | Streamlit |
| Backend | FastAPI |
| Speech Recognition | Faster-Whisper |
| Whisper Model | `small` |
| Translation | Ollama |
| Translation Model | `qwen2.5:3b` |
| Database | SQLite |
| Data Validation | Pydantic |
| HTTP Communication | Requests |
| Testing | Pytest |
| Configuration | Python configuration files |

### Architecture

CareTrace follows a frontend-backend architecture.

- **Streamlit:** Handles user interaction, language selection, audio recording, and displaying health records.
- **FastAPI:** Handles API requests, audio processing, transcription, translation, and database operations.
- **Faster-Whisper:** Converts Hindi and Gujarati speech into text.
- **Ollama:** Translates the original transcript into English using a locally running language model.
- **SQLite:** Stores patient health records persistently.

The frontend communicates with the backend through HTTP APIs. Database access and AI processing are handled by the backend.

## 5. Current Development Workflow

The implemented prototype currently follows this workflow:

1. **Patient Identification:** The prototype uses a temporary patient ID (`001`).
2. **Language Selection:** The user selects Hindi or Gujarati.
3. **Voice Input:** The user records their health experience or uploads an audio file.
4. **Audio Processing:** The backend receives and temporarily saves the uploaded audio.
5. **Speech-to-Text:** Faster-Whisper generates the original transcript.
6. **English Translation:** Ollama translates the transcript into English.
7. **Database Storage:** Both original and English transcripts are stored in SQLite with the patient ID and timestamp.
8. **Health History Retrieval:** The backend retrieves existing records associated with the patient ID.
9. **UI Update:** Streamlit displays existing records and refreshes the health history after a new record is saved.

### Planned Workflow

The following features are planned for subsequent development:

1. Health information extraction.
2. Identification of symptoms, events, time expressions, and relevant context.
3. Validation of extracted information.
4. Chronological timeline generation.
5. Structured appointment summary generation.
6. Editable transcript and timeline review.
7. Exporting summaries for medical appointments.
8. Patient authentication and secure access control.

## 6. Project Structure

The current project follows this directory structure:

```text
CareTrace/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── record_routes.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── health_records.py
│   │
│   └── services/
│       ├── transcription.py
│       ├── translation.py
│       ├── health_records.py
│       └── extraction.py
│
├── frontend/
│   ├── app.py
│   └── app_client.py
│
├── config/
│   └── settings.py
│
├── data/
│   └── caretrace.db
│
├── tests/
│
├── docs/
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

**Note:** The `data/caretrace.db` file is generated automatically when the backend initializes the database. It does not need to be committed to GitHub.

The structure above reflects the intended current organization. Keep filenames consistent with the actual files in your local repository.

## 7. Installation and Setup

Follow these instructions to run CareTrace on a new Windows computer.

### Prerequisites

Install the following software:

- Python 3.10 or a compatible version supported by the project's dependencies.
- Git.
- Visual Studio Code (recommended).
- Ollama.

Useful installation links:

- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Ollama](https://ollama.com/download)

### Step 1: Clone the Repository

Open PowerShell or the VS Code terminal.

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate to the project directory:

```powershell
cd CareTrace
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual repository URL.

### Step 2: Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

### Step 4: Install and Configure Ollama

Install Ollama from:

https://ollama.com/download

After installation, open a terminal and download the translation model:

```powershell
ollama pull qwen2.5:3b
```

Check whether the model is available:

```powershell
ollama list
```

Ensure the Ollama service is running.

The default local Ollama API address used by CareTrace is:

```text
http://localhost:11434
```

### Step 5: Configure Environment Variables

If the project uses `.env.example`, create your local `.env` file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with any configuration required by the project.

Do not commit `.env` to GitHub.

### Step 6: Start the FastAPI Backend

From the CareTrace project root, activate the virtual environment if necessary.

Run:

```powershell
python -m uvicorn backend.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The backend initializes the SQLite database and creates the required table when the application starts.

### Step 7: Start the Streamlit Frontend

Open another terminal in VS Code.

Navigate to the CareTrace project directory and activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
streamlit run frontend/app.py
```

The frontend should open at:

```text
http://localhost:8501
```

CareTrace is now ready to use.

## 8. API Endpoints

The FastAPI backend currently exposes the following endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome message |
| GET | `/api/v1/health` | Check backend availability |
| POST | `/api/v1/transcribe` | Transcribe, translate, and save an audio recording |
| POST | `/api/v1/records` | Save a health record directly |
| GET | `/api/v1/records/{patient_id}` | Retrieve a patient's health records |

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

The current prototype uses SQLite for persistent storage.

Database location:

```text
data/caretrace.db
```

### Table: `health_records`

| Column | Data Type | Description |
|---|---|---|
| `id` | INTEGER | Unique record identifier |
| `patient_id` | TEXT | Patient identifier |
| `original_transcript` | TEXT | Original Hindi/Gujarati transcript |
| `english_transcript` | TEXT | English translation |
| `created_at` | TEXT | Record creation timestamp |

The database table is created automatically during backend startup.

For the current prototype, the patient ID is hardcoded as:

```python
PATIENT_ID = "001"
```

This will be replaced with patient-specific authentication and access control in a future version.

## 10. Running the Project — Quick Reference

After completing the initial installation, two terminals are required.

**Terminal 1 — Backend**

```powershell
cd CareTrace

.\.venv\Scripts\Activate.ps1

python -m uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend**

```powershell
cd CareTrace

.\.venv\Scripts\Activate.ps1

streamlit run frontend/app.py
```

Make sure Ollama is running with the `qwen2.5:3b` model available.

## 11. Troubleshooting

### Issue 1: Backend connection error

Ensure that FastAPI is running:

```text
http://127.0.0.1:8000/health
```

Check that the frontend API base URL matches:

```python
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
```

### Issue 2: Ollama connection error

Check whether Ollama is running and the model is available:

```powershell
ollama list
```

If the model is missing:

```powershell
ollama pull qwen2.5:3b
```

### Issue 3: Whisper model loading takes time

The first transcription may take longer because the Whisper model needs to be downloaded and initialized.

The current configuration uses:

- Model: `small`
- Device: CPU
- Compute type: `int8`

### Issue 4: Python module import errors

Ensure commands are executed from the CareTrace project root.

Use:

```powershell
python -m uvicorn backend.main:app --reload
```

rather than executing the backend file directly.

Also verify that the virtual environment is activated and all dependencies are installed.

### Issue 5: Database records are not appearing

Ensure the backend started successfully and the database initialization completed.

Check that the database file exists:

```text
data/caretrace.db
```

Also verify that the patient ID used for saving and retrieving records is the same.

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

**Current prototype limitation:** Authentication and patient-level access control have not yet been implemented. The patient ID `001` is temporary, and the current database API must not be used to store real patient information in an exposed deployment.

## 14. Current Development Status

| Feature | Status |
|---|---|
| Initial project structure | Completed |
| Streamlit frontend | Implemented |
| FastAPI backend | Implemented |
| Hindi speech transcription | Implemented |
| Gujarati speech transcription | Implemented |
| English translation using Ollama | Implemented |
| SQLite database setup | Implemented |
| Health record storage | Implemented |
| Patient ID association | Implemented using temporary ID `001` |
| Existing health history retrieval | Implemented |
| Automatic UI refresh after saving | Implemented in current integration |
| Patient registration and login | Not implemented |
| Structured health information extraction | Experimental / pending integration |
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