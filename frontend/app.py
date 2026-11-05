import streamlit as st
from app_client import check_backend, transcribe_audio

st.set_page_config(
    page_title="CareTrace: Voice Enabled Personal Health Timeline Generation",
    page_icon="🩺",
    layout="centered",
)

st.title("🩺 CareTrace: Voice Enabled Personal Health Timeline Generation")

st.subheader("A personal health timeline generation tool.")

st.write("""
CareTrace is a web application that allows users to generate a personal 
health timeline by transcribing audio recordings in Hindi and Gujarati.
The application uses a FastAPI backend to handle audio file uploads and transcriptions, 
and a Streamlit frontend to provide a user-friendly interface for interacting with the backend services.
""")

st.info(
    "CareTrace is a health-information organization tool."
    "It does not provide medical diagnosis or treatment advice."
)

with st.sidebar:
    st.header("Backend Health Check")

    if st.button("Check Backend Health"):
        backend_status = check_backend()
        if backend_status.get("status") == "healthy":
            st.success("Backend is healthy and running.")
        else:
            st.error(f"Backend is unavailable. Error: {backend_status.get('message')}")

    st.divider()

    st.caption("CareTrace Prototype v1.0.0 | Developed by Meet Gandhi and team | 2026")

st.header("1. Select the language.")
language_options = {
    "Hindi": "hi",
    "Gujarati": "gu"
}

selected_language = st.selectbox(
    "Choose the language for transcription:",
    options=list(language_options.keys()),
)

language_code = language_options[selected_language]

st.header("2. Record Your Health Experience.")
st.write("Please record your health experience in the selected language.")

audio_file = st.audio_input("Record your audio here:")
uploaded_audio = st.file_uploader("Or upload an audio file (WAV, MP3, etc.):", type=["wav", "mp3", "m4a"])

selected_audio = audio_file if audio_file is not None else uploaded_audio

if selected_audio is not None:
    st.audio(selected_audio)
    st.success("Audio is ready for transcription")

st.header("3. Transcribe Audio.")

if st.button(
    "Transcribe Audio",
    type="primary",
    disabled = selected_audio is None,
):
    with st.spinner(f"Sending audio for transcription for the selected language {selected_language}..."):
        result = transcribe_audio(audio_file = selected_audio, language = language_code)

    if result.get("status") == "error":
        st.error("Unable to process the audio. Please try again later.")
        st.write(result.get("message","unknown error occured"))
    elif result.get("status") == "not_implemented":
        st.warning("Transcription functionality is currently under development.")
        st.write(result.get("message","unknown error occured"))
    else:
        transcript = result.get("transcript", "")

        if transcript:
            st.session_state["transcript"] = transcript
            st.success("Transcription completed successfully.")
        else:
            st.warning("Transcription returned an empty result. Please try again.")

if "transcript" in st.session_state:
    st.header("4. Transcription Result.")
    edited_transcript = st.text_area(
        "You can edit the transcript below if needed:",
        value=st.session_state["transcript"],
        height=250
    )

    st.session_state["transcript"] = edited_transcript

    if st.button("Save Transcript"):
        st.success("Transcript saved successfully.")
