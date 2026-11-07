
import streamlit as st

# Use the filename that actually exists in your frontend folder.
from app_client import (
    check_backend,
    transcribe_audio,
    get_patient_records
)


st.set_page_config(
    page_title="CareTrace: Voice Enabled Personal Health Timeline Generation",
    page_icon="🩺",
    layout="centered",
)

PATIENT_ID = "001"

# Fetch existing patient records whenever the app loads
records_response = get_patient_records(PATIENT_ID)

if records_response.get("status") == "success":
    st.session_state["health_records"] = records_response.get(
        "records", []
    )
else:
    st.session_state["health_records"] = []

st.title("🩺 CareTrace: Voice Enabled Personal Health Timeline Generation")
st.subheader("A personal health timeline generation tool.")

st.write("""
CareTrace is a web application that helps users organize their
health experiences by transcribing audio recordings in Hindi
and Gujarati and extracting relevant health information.
""")

st.info(
    "CareTrace is a health-information organization tool. "
    "It does not provide medical diagnosis or treatment advice."
)

# --------------------------------------------------
# Sidebar: Backend health check
# --------------------------------------------------

with st.sidebar:
    st.header("Backend Health Check")

    if st.button("Check Backend Health"):
        backend_status = check_backend()

        if backend_status.get("status") == "healthy":
            st.success("Backend is healthy and running.")
        else:
            st.error(
                f"Backend is unavailable: "
                f"{backend_status.get('message', 'Unknown error')}"
            )

    st.divider()
    st.caption(
        "CareTrace Prototype v1.0.0 | "
        "Developed by Meet Gandhi and team | 2026"
    )


# Display saved health history
st.header("1. Your Health History")

if st.session_state.get("record_saved"):
    st.success("Your new health record has been saved successfully!")
    st.session_state["record_saved"] = False

health_records = st.session_state.get("health_records", [])

if health_records:

    st.write(f"Total health records: {len(health_records)}")

    for record in health_records:

        timestamp = record.get("created_at", "Date unavailable")

        with st.expander(f"Health Record #{record['id']} | {timestamp}"):

            st.markdown("**Original Transcript**")
            st.write(record["original_transcript"])

            st.markdown("**English Translation**")
            st.write(record["english_transcript"])

else:
    st.info("No health records found. Your health experiences will appear here.")

st.divider()

# Audio recording section
st.header("2. Record Your Health Experience")

language_options = {
    "Hindi": "hi",
    "Gujarati": "gu"
}

selected_language = st.selectbox(
    "Choose your language:",
    options=list(language_options.keys())
)

language_code = language_options[selected_language]

st.write("Record your health experience in the selected language.")

audio_file = st.audio_input("Record your audio:")

uploaded_audio = st.file_uploader(
    "Or upload an audio file:",
    type=["wav", "mp3", "m4a"]
)

selected_audio = (
    audio_file if audio_file is not None else uploaded_audio
)

if selected_audio is not None:
    st.audio(selected_audio)

# Transcription and automatic database storage
st.header("3. Save Your Health Experience")

if st.button(
    "Process and Save",
    type="primary",
    disabled=selected_audio is None
):

    with st.spinner(
        "Transcribing, translating and saving your health experience..."
    ):

        result = transcribe_audio(
            audio_file=selected_audio,
            language=language_code
        )

    if result.get("status") == "error":

        st.error("Unable to process your audio.")
        st.write(result.get("message", "Unknown error"))

    elif result.get("status") == "success":

        # Fetch updated records after successful database insertion
        updated_records = get_patient_records("001")

        if updated_records.get("status") == "success":

            st.session_state["health_records"] = (
                updated_records.get("records", [])
            )

            st.session_state["record_saved"] = True

            # Refresh the page to display the newly saved record
            st.rerun()

        else:
            st.warning(
                "Your record was processed, but the updated "
                "health history could not be retrieved."
            )
            st.write(updated_records.get("message", "Unknown error"))

    else:
        st.error(
            result.get("message", "Unexpected response from backend.")
        )
