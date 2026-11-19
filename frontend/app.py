import html

import streamlit as st

from app_client import (
    check_backend,
    transcribe_audio,
    get_patient_records,
)


st.set_page_config(
    page_title="CareTrace | Voice Enabled Health Timeline",
    page_icon="🩺",
    layout="wide",
)

PATIENT_ID = "001"


# --------------------------------------------------
# Flashy styling
# --------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }

/* animated aurora background */
.stApp {
    background:
        radial-gradient(900px 500px at 8% -5%,  rgba(124, 92, 255, .35), transparent 60%),
        radial-gradient(800px 500px at 95% 5%,  rgba(0, 224, 255, .22),  transparent 60%),
        radial-gradient(900px 600px at 50% 110%, rgba(255, 64, 160, .20), transparent 60%),
        #0B0B1A;
    background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1150px; }

/* hero */
.hero {
    position: relative; overflow: hidden;
    padding: 2.4rem 2.2rem; border-radius: 26px;
    background: linear-gradient(135deg, rgba(124,92,255,.28), rgba(0,224,255,.12) 55%, rgba(255,64,160,.22));
    border: 1px solid rgba(255,255,255,.14);
    box-shadow: 0 20px 60px rgba(124,92,255,.25), inset 0 1px 0 rgba(255,255,255,.12);
    backdrop-filter: blur(14px);
    margin-bottom: 1.4rem;
}
.hero::after {
    content: ""; position: absolute; inset: -50%;
    background: conic-gradient(from 0deg, transparent, rgba(255,255,255,.07), transparent 30%);
    animation: spin 9s linear infinite; pointer-events: none;
}
@keyframes spin { to { transform: rotate(360deg); } }
.hero h1 {
    margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(90deg, #7C5CFF, #00E0FF, #FF40A0, #7C5CFF);
    background-size: 300% 100%;
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    animation: flow 6s linear infinite;
}
@keyframes flow { to { background-position: 300% 0; } }
.hero p  { margin: .6rem 0 0; color: #C9C9F0; font-size: 1.05rem; max-width: 760px; }
.badge {
    display: inline-block; margin: 1rem .5rem 0 0; padding: .3rem .85rem; border-radius: 999px;
    font-size: .78rem; font-weight: 600; color: #fff;
    background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.2);
}

/* pipeline */
.pipeline { display: flex; gap: .8rem; flex-wrap: wrap; margin: 0 0 1.6rem; }
.step {
    flex: 1 1 180px; padding: 1rem 1.1rem; border-radius: 18px;
    background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.1);
    transition: transform .25s, box-shadow .25s, border-color .25s;
}
.step:hover { transform: translateY(-5px); border-color: #00E0FF; box-shadow: 0 12px 30px rgba(0,224,255,.25); }
.step .ico { font-size: 1.7rem; }
.step .t { font-weight: 700; color: #fff; margin-top: .25rem; }
.step .d { font-size: .8rem; color: #A9A9D6; }

/* stat tiles */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .9rem; margin-bottom: 1.6rem; }
.stat {
    padding: 1.1rem 1.3rem; border-radius: 20px;
    background: linear-gradient(145deg, rgba(255,255,255,.09), rgba(255,255,255,.03));
    border: 1px solid rgba(255,255,255,.12);
}
.stat .n { font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1.1; }
.stat .l { font-size: .8rem; color: #A9A9D6; text-transform: uppercase; letter-spacing: .08em; }

/* section titles */
.sec { display: flex; align-items: center; gap: .6rem; margin: 2rem 0 1rem; font-size: 1.5rem; font-weight: 700; color: #fff; }
.sec .pill {
    width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; font-size: 1.1rem;
    background: linear-gradient(135deg, #7C5CFF, #FF40A0); box-shadow: 0 6px 18px rgba(124,92,255,.5);
}

/* timeline of records */
.timeline { position: relative; margin-left: 14px; padding-left: 26px; border-left: 2px dashed rgba(124,92,255,.5); }
.rec {
    position: relative; margin-bottom: 1.2rem; padding: 1.1rem 1.3rem; border-radius: 20px;
    background: rgba(255,255,255,.055); border: 1px solid rgba(255,255,255,.1);
    backdrop-filter: blur(10px); transition: transform .25s, box-shadow .25s;
    animation: rise .5s ease both;
}
.rec:hover { transform: translateX(6px); box-shadow: 0 14px 40px rgba(124,92,255,.28); }
.rec::before {
    content: ""; position: absolute; left: -37px; top: 22px; width: 18px; height: 18px; border-radius: 50%;
    background: linear-gradient(135deg, #00E0FF, #FF40A0);
    box-shadow: 0 0 0 4px #0B0B1A, 0 0 18px #00E0FF;
}
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.rec .head { display: flex; justify-content: space-between; align-items: center; margin-bottom: .7rem; }
.rec .id { font-weight: 700; color: #fff; }
.rec .ts { font-size: .78rem; color: #A9A9D6; padding: .15rem .6rem; border-radius: 999px; background: rgba(255,255,255,.08); }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 760px) { .cols { grid-template-columns: 1fr; } }
.col .lab { font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .3rem; }
.col.o .lab { color: #FF8AC8; } .col.e .lab { color: #66EFFF; }
.col .txt { color: #E6E6FF; line-height: 1.6; white-space: pre-wrap; }

/* empty state */
.empty {
    text-align: center; padding: 2.2rem 1rem; border-radius: 20px; color: #C9C9F0;
    border: 2px dashed rgba(255,255,255,.18); background: rgba(255,255,255,.03);
}

/* recording panel */
.pulse {
    width: 14px; height: 14px; border-radius: 50%; background: #FF3B6B; display: inline-block; margin-right: .5rem;
    box-shadow: 0 0 0 0 rgba(255,59,107,.7); animation: pulse 1.6s infinite;
}
@keyframes pulse { 70% { box-shadow: 0 0 0 14px rgba(255,59,107,0); } 100% { box-shadow: 0 0 0 0 rgba(255,59,107,0); } }

/* streamlit widgets */
div.stButton > button {
    border: 0; border-radius: 14px; padding: .75rem 1.6rem; font-weight: 700; color: #fff;
    background: linear-gradient(90deg, #7C5CFF, #FF40A0, #00E0FF); background-size: 200% 100%;
    box-shadow: 0 10px 28px rgba(124,92,255,.45); transition: transform .2s, background-position .5s, box-shadow .2s;
}
div.stButton > button:hover:not(:disabled) { transform: translateY(-3px) scale(1.02); background-position: 100% 0; box-shadow: 0 16px 38px rgba(255,64,160,.5); }
div.stButton > button:disabled { opacity: .35; box-shadow: none; }
div[data-testid="stSelectbox"] > div > div, div[data-testid="stFileUploader"] section, div[data-testid="stAudioInput"] {
    border-radius: 16px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.12);
}
section[data-testid="stSidebar"] { background: rgba(14,14,34,.85); border-right: 1px solid rgba(255,255,255,.08); }
.status { display: inline-flex; align-items: center; gap: .5rem; padding: .35rem .8rem; border-radius: 999px; font-size: .8rem; font-weight: 600; }
.status.ok  { background: rgba(0,255,170,.12); color: #5CFFC8; border: 1px solid rgba(0,255,170,.35); }
.status.bad { background: rgba(255,59,107,.12); color: #FF8FAA; border: 1px solid rgba(255,59,107,.35); }
.disclaimer {
    margin: 0 0 1.4rem; padding: .85rem 1.1rem; border-radius: 14px; font-size: .88rem; color: #FFE9A8;
    background: rgba(255,200,60,.08); border: 1px solid rgba(255,200,60,.3);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def esc(value) -> str:
    """Escape user/transcript text before putting it inside HTML."""
    return html.escape(str(value if value is not None else ""))


# --------------------------------------------------
# Data
# --------------------------------------------------

records_response = get_patient_records(PATIENT_ID)

if records_response.get("status") == "success":
    st.session_state["health_records"] = records_response.get("records", [])
else:
    st.session_state["health_records"] = []

health_records = st.session_state.get("health_records", [])


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.markdown("### 🩺 CareTrace")
    st.caption("Voice-enabled health timeline")

    backend_status = check_backend()
    if backend_status.get("status") == "healthy":
        st.markdown('<span class="status ok">● Backend online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status bad">● Backend offline</span>', unsafe_allow_html=True)
        st.caption(esc(backend_status.get("message", "Unknown error")))

    if st.button("↻ Re-check backend"):
        st.rerun()

    st.divider()
    st.markdown("**Patient:** `001` (prototype)")
    st.caption(
        "CareTrace Prototype v1.1.0 | "
        "Developed by Meet Gandhi and team | 2026"
    )


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.markdown(
    """
<div class="hero">
  <h1>CareTrace</h1>
  <p>Speak your health story in <b>Hindi</b> or <b>Gujarati</b>. CareTrace transcribes it,
     translates it to English and builds a personal health timeline you can bring to your doctor.</p>
  <span class="badge">🎙️ Voice first</span>
  <span class="badge">🌐 हिन्दी · ગુજરાતી</span>
  <span class="badge">🔒 Runs locally</span>
</div>
<div class="disclaimer">
  ⚠️ CareTrace is a health-information organization tool. It does not provide medical diagnosis or treatment advice.
</div>
<div class="pipeline">
  <div class="step"><div class="ico">🎙️</div><div class="t">1 · Record</div><div class="d">Speak or upload audio</div></div>
  <div class="step"><div class="ico">📝</div><div class="t">2 · Transcribe</div><div class="d">Whisper speech-to-text</div></div>
  <div class="step"><div class="ico">🌍</div><div class="t">3 · Translate</div><div class="d">Local LLM → English</div></div>
  <div class="step"><div class="ico">🗂️</div><div class="t">4 · Save</div><div class="d">Added to your timeline</div></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="stats">
  <div class="stat"><div class="n">{len(health_records)}</div><div class="l">Records saved</div></div>
  <div class="stat"><div class="n">2</div><div class="l">Languages</div></div>
  <div class="stat"><div class="n" style="font-size:1.35rem;padding:.45rem 0">{esc(health_records[-1].get('created_at', '—')) if health_records else '—'}</div><div class="l">Latest entry</div></div>
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 1. Health history timeline
# --------------------------------------------------

st.markdown('<div class="sec"><span class="pill">🕒</span>Your Health Timeline</div>', unsafe_allow_html=True)

if st.session_state.get("record_saved"):
    st.success("✨ Your new health record has been saved successfully!")
    st.balloons()
    st.session_state["record_saved"] = False

if health_records:
    cards = []
    for i, record in enumerate(health_records):
        cards.append(
            f"""
<div class="rec" style="animation-delay:{min(i, 8) * 0.06:.2f}s">
  <div class="head">
    <span class="id">Health Record #{esc(record.get('id'))}</span>
    <span class="ts">{esc(record.get('created_at', 'Date unavailable'))}</span>
  </div>
  <div class="cols">
    <div class="col o"><div class="lab">Original transcript</div><div class="txt">{esc(record.get('original_transcript'))}</div></div>
    <div class="col e"><div class="lab">English translation</div><div class="txt">{esc(record.get('english_transcript'))}</div></div>
  </div>
</div>"""
        )
    st.markdown(f'<div class="timeline">{"".join(cards)}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="empty">🌱 No health records yet.<br>'
        'Record your first health experience below and it will appear here.</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# 2. Record
# --------------------------------------------------

st.markdown('<div class="sec"><span class="pill">🎙️</span>Record Your Health Experience</div>', unsafe_allow_html=True)

language_options = {
    "Hindi (हिन्दी)": "hi",
    "Gujarati (ગુજરાતી)": "gu",
}

left, right = st.columns([1, 2])

with left:
    selected_language = st.selectbox(
        "Choose your language:",
        options=list(language_options.keys()),
    )
    language_code = language_options[selected_language]
    st.markdown(
        '<span class="pulse"></span><small>Ready to listen</small>',
        unsafe_allow_html=True,
    )

with right:
    audio_file = st.audio_input("Record your audio:")
    uploaded_audio = st.file_uploader(
        "Or upload an audio file:",
        type=["wav", "mp3", "m4a"],
    )

selected_audio = audio_file if audio_file is not None else uploaded_audio

if selected_audio is not None:
    st.audio(selected_audio)


# --------------------------------------------------
# 3. Process & save
# --------------------------------------------------

st.markdown('<div class="sec"><span class="pill">🚀</span>Save Your Health Experience</div>', unsafe_allow_html=True)

if st.button(
    "✨ Process and Save",
    type="primary",
    disabled=selected_audio is None,
):

    with st.spinner("Transcribing, translating and saving your health experience..."):
        result = transcribe_audio(
            audio_file=selected_audio,
            language=language_code,
        )

    if result.get("status") == "error":
        st.error("Unable to process your audio.")
        st.write(result.get("message", "Unknown error"))

    elif result.get("status") == "success":
        updated_records = get_patient_records(PATIENT_ID)

        if updated_records.get("status") == "success":
            st.session_state["health_records"] = updated_records.get("records", [])
            st.session_state["record_saved"] = True
            st.rerun()
        else:
            st.warning(
                "Your record was processed, but the updated "
                "health history could not be retrieved."
            )
            st.write(updated_records.get("message", "Unknown error"))

    else:
        st.error(result.get("message", "Unexpected response from backend."))
