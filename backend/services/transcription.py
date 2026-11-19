
from functools import lru_cache
from faster_whisper import WhisperModel

from config.settings import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    ASR_BACKEND,
    INDIC_CONFORMER_MODEL,
    INDIC_DECODER,
)


# ==========================================
# MODEL CONFIGURATION (see config/settings.py)
# ==========================================

MODEL_SIZE = WHISPER_MODEL          # default: "large-v3-turbo"
DEVICE = WHISPER_DEVICE
COMPUTE_TYPE = WHISPER_COMPUTE_TYPE

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

def _transcribe_whisper(
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


# ==========================================
# INDICCONFORMER (AI4Bharat) BACKEND
# ==========================================

@lru_cache(maxsize=1)
def load_indic_conformer():
    """
    Load IndicConformer once. The model on Hugging Face is gated:
    accept its terms on the model page and run `huggingface-cli login` once.
    """
    from transformers import AutoModel

    print(f"Loading IndicConformer: {INDIC_CONFORMER_MODEL}")
    model = AutoModel.from_pretrained(
        INDIC_CONFORMER_MODEL, trust_remote_code=True
    )
    print("IndicConformer loaded successfully!")
    return model


def _transcribe_indic_conformer(audio_path: str, language: str) -> str:
    import torch
    from faster_whisper.audio import decode_audio

    # decode_audio handles wav/mp3/m4a and returns 16 kHz mono float32
    samples = decode_audio(audio_path, sampling_rate=16000)
    wav = torch.from_numpy(samples).unsqueeze(0)  # [1, samples]

    model = load_indic_conformer()
    with torch.no_grad():
        text = model(wav, language, INDIC_DECODER)

    if isinstance(text, (list, tuple)):
        text = text[0]
    return str(text).strip()


# ==========================================
# PUBLIC ENTRY POINT
# ==========================================

def transcribe_audio_file(
    audio_path: str,
    language: str,
) -> str:
    """
    Transcribe an audio file (Hindi 'hi' or Gujarati 'gu').
    Uses IndicConformer by default and falls back to Whisper
    if it cannot be loaded. Set ASR_BACKEND=whisper to force Whisper.
    """

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            "Unsupported language. Use 'hi' for Hindi "
            "or 'gu' for Gujarati."
        )

    if ASR_BACKEND == "indic_conformer":
        try:
            return _transcribe_indic_conformer(audio_path, language)
        except Exception as error:  # noqa: BLE001
            print(
                f"[WARNING] IndicConformer failed ({error!r}); "
                "falling back to Whisper."
            )

    return _transcribe_whisper(audio_path, language)
