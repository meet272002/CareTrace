import os
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import Literal

from backend.services.transcription import transcribe_audio_file
from backend.services.translation import translate_to_english
from backend.services.health_records import save_health_record

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
    }

"""
Created by Meet Gandhi on 24/10/2026 for transcribing audio files in Gujarati and Hindi language. 
"""

@router.post("/transcribe")
async def transcribe_audio(
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
            content = await audio.read()
            temporary_file.write(content)

        # Step 1: Transcribe audio
        original_transcript = transcribe_audio_file(
            audio_path=temporary_path,
            language=language
        )

        if not original_transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech was detected in the audio."
            )

        # Step 2: Translate transcript into English
        english_transcript = translate_to_english(
            transcript=original_transcript,
            language=language
        )

        # Step 3: Save both transcripts
        saved_record = save_health_record(
            patient_id=PATIENT_ID,
            original_transcript=original_transcript,
            english_transcript=english_transcript
        )

        return {
            "status": "success",
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
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process health record: {str(error)}"
        )

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)

