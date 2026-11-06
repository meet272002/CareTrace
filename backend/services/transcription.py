
from functools import lru_cache
from faster_whisper import WhisperModel


# ==========================================
# MODEL CONFIGURATION
# ==========================================

MODEL_SIZE = "small"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "gu": "Gujarati",
}


# ==========================================
# LOAD WHISPER MODEL
# ==========================================

@lru_cache(maxsize=1)
def load_whisper_model():
    """
    Load the Whisper model once and reuse it
    for subsequent transcription requests.
    """

    print(f"Loading Whisper model: {MODEL_SIZE}")

    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )

    print("Whisper model loaded successfully!")

    return model


# ==========================================
# TRANSCRIPTION FUNCTION
# ==========================================

def transcribe_audio_file(
    audio_path: str,
    language: str,
) -> str:
    """
    Transcribe an audio file using local Whisper.

    Args:
        audio_path: Path to the audio file.
        language: 'hi' for Hindi or 'gu' for Gujarati.

    Returns:
        Transcribed text.
    """

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            "Unsupported language. Use 'hi' for Hindi "
            "or 'gu' for Gujarati."
        )

    # Load cached Whisper model
    model = load_whisper_model()

    print(
        f"Starting {SUPPORTED_LANGUAGES[language]} transcription..."
    )

    # Perform transcription
    segments, info = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        beam_size=5,
        vad_filter=True,
    )

    # Collect transcription segments
    transcript_parts = [
        segment.text.strip()
        for segment in segments
    ]

    transcript = " ".join(transcript_parts).strip()

    print(f"Detected language: {info.language}")
    print("Transcription completed!")

    return transcript
