from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import Literal

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
async def transcribe_audio(audio: UploadFile = File(...), language: Literal["hi", "gu"] = "hi"):
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload an audio file.")

    return {
        "status": "currently not implemented",
        "language": language,
        "filename": audio.filename,
        "message": "Audio received successfully. Transcription functionality is under development."
    }