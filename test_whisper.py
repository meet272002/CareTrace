
from backend.services.transcription import transcribe_audio_file


# Hindi test
audio_path = "data/sample_inputs/hindi_sample.wav"

transcript = transcribe_audio_file(
    audio_path=audio_path,
    language="hi",
)

print("\n========== TRANSCRIPTION RESULT ==========")
print(transcript)
print("==========================================")
