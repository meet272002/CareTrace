import os
import tempfile
import time
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from typing import Literal
import traceback

from backend.services.transcription import transcribe_audio_file
from backend.services.translation import translate_to_english
from backend.services.health_records import save_health_record
from backend.services.status import MODEL_STATUS
from backend.services.issues import extract_and_store, mark_processing

PATIENT_ID = "001"

router = APIRouter()

"""
Created by Meet Gandhi on 24/10/2026 to check whether the backend is available or not.  
"""
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareTrace API",
        "models": MODEL_STATUS,
    }

"""
Created by Meet Gandhi on 24/10/2026 for transcribing audio files in Gujarati and Hindi language. 
"""

# Plain `def` (not `async def`): FastAPI runs it in a worker thread, so the slow
# speech/translation work does not freeze the whole server (health checks,
# progress polling) while it runs.
@router.post("/transcribe")
def transcribe_audio(
    background_tasks: BackgroundTasks,
    language: Literal["hi", "gu"],
    audio: UploadFile = File(...)
):
    """
    Transcribe audio, translate it into English,
    and save both transcripts for the patient.
    """

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio filename is missing."
        )

    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    temporary_path = None

    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temporary_file:

            temporary_path = temporary_file.name
            content = audio.file.read()
            temporary_file.write(content)

        # Step 1: Transcribe audio
        started = time.perf_counter()
        print(f"[transcribe] speech recognition started (model: {MODEL_STATUS['speech']})")
        original_transcript = transcribe_audio_file(
            audio_path=temporary_path,
            language=language
        )
        print(f"[transcribe] speech recognition done in {time.perf_counter() - started:.1f}s")

        if not original_transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech was detected in the audio."
            )

        # Step 2: Translate transcript into English
        started = time.perf_counter()
        print("[transcribe] translation started")
        english_transcript = translate_to_english(
            transcript=original_transcript,
            language=language
        )
        print(f"[transcribe] translation done in {time.perf_counter() - started:.1f}s")

        # Step 3: Save both transcripts
        saved_record = save_health_record(
            patient_id=PATIENT_ID,
            original_transcript=original_transcript,
            english_transcript=english_transcript
        )

        # Step 4: Extract issues in the background so the user is not kept
        # waiting (the record is already saved either way).
        mark_processing(saved_record["id"], PATIENT_ID)
        background_tasks.add_task(
            extract_and_store,
            saved_record["id"],
            PATIENT_ID,
            english_transcript,
        )
        extraction_result = {"status": "processing"}

        return {
            "status": "success",
            "extraction": extraction_result,
            "patient_id": PATIENT_ID,
            "filename": audio.filename,
            "original_transcript": original_transcript,
            "english_transcript": english_transcript,
            "record": saved_record,
            "message": "Health record saved successfully."
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print("\n========== TRANSCRIPTION ERROR ==========")
        traceback.print_exc()
        print("==========================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Unable to process health record: {str(error)}"
        )

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)

