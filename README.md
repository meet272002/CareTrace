# CareTrace: A Voice-Enabled AI Assistant for Personal Health Timeline Generation

## 1. Overview

CareTrace is a voice-enabled AI assistant designed to help users organize their personal health experiences into a chronological timeline and a structured summary for medical appointments.

Users will be able to narrate their health experiences in **Hindi or Gujarati**. The system will convert speech into text, extract relevant health events, organize them chronologically, and generate an editable summary that users can review before sharing with a healthcare professional.

CareTrace aims to make it easier for users to communicate their health history clearly and systematically.

## 2. Problem Statement

People may find it difficult to remember and communicate the sequence of their symptoms, when they started, how they changed, and what other relevant circumstances occurred.

Manually maintaining health records can be inconvenient, particularly when information is spread across multiple conversations, notes, or personal recollections.

CareTrace aims to address this problem through voice-based input and AI-assisted organization of personal health information.

## 3. Project Objectives

- Enable users to narrate their health experiences in Hindi or Gujarati.
- Convert recorded speech into editable text.
- Extract relevant health events, symptoms, time expressions, and contextual information.
- Organize extracted events into a chronological timeline.
- Generate a structured, editable summary for medical appointments.
- Preserve uncertainty and avoid inventing missing dates, details, or causal relationships.
- Evaluate the accuracy and usability of the generated timeline and summary.

## 4. Planned Workflow

1. **Language Selection:** The user selects Hindi or Gujarati.
2. **Voice Input:** The user records a narration of their health experiences.
3. **Audio Processing:** The system checks and prepares the audio for transcription.
4. **Speech-to-Text:** The recording is converted into text in the selected language.
5. **Transcript Review:** The user reviews and corrects the transcript.
6. **Health Information Extraction:** AI identifies symptoms, time expressions, changes, relevant context, and uncertainty.
7. **Information Validation:** The extracted information is checked for missing or unreliable details.
8. **Timeline Generation:** The system organizes health events chronologically while preserving unknown dates.
9. **Appointment Summary:** The system generates a structured summary of the user's reported experiences.
10. **User Review:** The user reviews, edits, and confirms the generated information before exporting or sharing it.

## 5. Initial Language Support

The initial prototype will focus on:

- Hindi
- Gujarati

Speech recognition quality and the accuracy of extracted health information will be evaluated for both languages.

## 6. Technology Stack

The following technologies are planned for the initial prototype. Specific speech-recognition and language-model choices will be finalized during implementation.

- **Programming Language:** Python
- **User Interface:** Streamlit
- **Speech Recognition:** A Hindi- and Gujarati-compatible speech-to-text model or service
- **AI/NLP Processing:** A language model for structured health-event extraction and summary generation
- **Data Validation:** Pydantic
- **Testing:** Pytest
- **Configuration:** Python environment variables and `python-dotenv`

## 7. Project Structure

```text
CareTrace/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   └── settings.py
│
├── src/
│   ├── __init__.py
│   ├── audio/
│   │   ├── __init__.py
│   │   └── recorder.py
│   ├── transcription/
│   │   ├── __init__.py
│   │   └── speech_to_text.py
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   └── schemas.py
│   ├── timeline/
│   │   ├── __init__.py
│   │   └── generator.py
│   └── summary/
│       ├── __init__.py
│       └── generator.py
│
├── tests/
│   ├── test_transcription.py
│   ├── test_extraction.py
│   └── test_timeline.py
│
├── data/
│   └── sample_inputs/
│
└── docs/
    └── workflow.md
```

## 8. Evaluation Plan

The prototype will be evaluated using fictional health scenarios and, where appropriate, consented test data.

Key evaluation criteria include:

- **Transcription Accuracy:** How accurately recorded Hindi and Gujarati speech is converted into text.
- **Extraction Accuracy:** Whether relevant symptoms, events, and contextual details are identified correctly.
- **Chronological Accuracy:** Whether events are placed in the correct order based on the available information.
- **Uncertainty Preservation:** Whether unknown dates and ambiguous details remain explicitly uncertain.
- **Unsupported Inference:** Whether the system avoids adding information that the user did not provide.
- **Usability:** Whether users can review, correct, and understand the generated timeline and summary.

## 9. Safety and Privacy Considerations

CareTrace is intended to organize user-reported health information, not to diagnose medical conditions or recommend treatments.

The system should:

- Avoid presenting generated information as a medical diagnosis.
- Preserve uncertainty instead of guessing missing information.
- Allow users to review and correct transcripts and extracted events.
- Protect recordings and health information from unauthorized access.
- Avoid committing API keys, recordings, or sensitive health information to version control.
- Use fictional sample scenarios during early development.

Data storage, retention, and deletion practices will be defined before testing with real personal health information.

## 10. Current Development Status

**Current stage:** Initial project setup.

The project directory structure and initial files have been created. The next development stages are:

1. Build the initial Streamlit interface.
2. Implement voice recording and audio handling.
3. Select and integrate Hindi/Gujarati speech recognition.
4. Implement structured health-event extraction.
5. Develop chronological timeline generation.
6. Generate editable appointment summaries.
7. Add tests and evaluate the prototype.

Features listed in the workflow are planned and should not be considered implemented until they have been developed and tested.

## 11. Future Enhancements

Potential future improvements include:

- Support for additional Indian languages.
- Improved handling of relative dates and uncertain timelines.
- Editable event-level confidence and clarification prompts.
- Exporting summaries into printable formats.
- Enhanced privacy controls and secure data handling.

---

**Project Name:** CareTrace  
**Project Focus:** Voice-enabled personal health timeline generation  
**Initial Languages:** Hindi and Gujarati  
**Primary Goal:** Help users organize and communicate their reported health history more clearly.
