import os
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import Literal

from backend.services.transcription import transcribe_audio_file

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
    Receive an audio file, transcribe it using
    the local Whisper model, and return the transcript.
    """

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio filename is missing."
        )

    # Preserve the uploaded file extension
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

        # Run Whisper transcription
        transcript = transcribe_audio_file(
            audio_path=temporary_path,
            language=language
        )

        return {
            "status": "success",
            "language": language,
            "filename": audio.filename,
            "transcript": transcript
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(error)}"
        )

    finally:
        # Remove temporary audio file
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
