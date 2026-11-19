import os

# ---------------- Translation (Ollama) ----------------
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")  # try "qwen2.5:7b" for better Gujarati->English
OLLAMA_TIMEOUT = 300

# ---------------- Speech recognition (faster-whisper) ----------------
# Latest Whisper: "large-v3-turbo" (needs faster-whisper >= 1.1.0).
# Override without code changes, e.g. in .env or the shell:
#   WHISPER_MODEL=large-v3          (slower, a bit more accurate)
#   WHISPER_MODEL=small             (old default, fastest on CPU)
#   WHISPER_MODEL=C:/models/my-finetuned-gujarati-ct2   (local CTranslate2 folder)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3-turbo")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")          # "cpu" or "cuda"
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")  # "float16" on GPU

# ---------------- ASR backend ----------------
# "indic_conformer": AI4Bharat IndicConformer 600M (best for Hindi/Gujarati, MIT licence)
# "whisper":         faster-whisper (settings above)
ASR_BACKEND = os.getenv("ASR_BACKEND", "indic_conformer")
INDIC_CONFORMER_MODEL = os.getenv(
    "INDIC_CONFORMER_MODEL", "ai4bharat/indic-conformer-600m-multilingual"
)
INDIC_DECODER = os.getenv("INDIC_DECODER", "ctc")  # "ctc" (faster) or "rnnt" (often more accurate)
