import sys
import re
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

import streamlit as st
import time
from dotenv import load_dotenv
load_dotenv(r"E:\Personal AI Voice Assistant System - AIVA\aiva\.env")

from aiva.llm.gemini_client import GeminiClient
from aiva.tts.xtts_engine import TTSEngine
from aiva.tools.weather import WeatherTool
from aiva.tools.wikipedia_tool import WikipediaTool
from aiva.multilingual.lang_detector import LanguageDetector

# ── Page Config ────────────────────────────────────────
st.set_page_config(
    page_title="AIVA — AI Voice Assistant",
    page_icon="🤖",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
    body { background-color: #0f0f1a; }
    .main { background-color: #0f0f1a; }

    .header-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .header-box h1 { color: #00d4ff; font-size: 3em; margin: 0; }
    .header-box p  { color: #aaaaaa; margin: 5px 0; }

    .chat-user {
        background: #0f3460;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 0px 18px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        width: fit-content;
        margin-left: auto;
    }
    .chat-aiva {
        background: #16213e;
        color: #00d4ff;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0px;
        margin: 8px 0;
        max-width: 75%;
        width: fit-content;
        border-left: 4px solid #00d4ff;
    }
    .status-pill {
        background: #16213e;
        color: #00d4ff;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        display: inline-block;
        margin: 4px;
        border: 1px solid #0f3460;
    }
    .stTextInput input {
        background: #16213e !important;
        color: white !important;
        border: 1px solid #0f3460 !important;
        border-radius: 10px !important;
    }
    .stButton button {
        background: #0f3460 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #00d4ff !important;
    }
    .stButton button:hover {
        background: #00d4ff !important;
        color: #0f0f1a !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize Session State ───────────────────────────
@st.cache_resource
def load_modules():
    """Load all AIVA modules once and cache them."""
    print("Loading AIVA modules...")
    return {
        "llm":          GeminiClient(),
        "tts":          TTSEngine(),
        "weather":      WeatherTool(),
        "wiki":         WikipediaTool(),
        "lang":         LanguageDetector("en")
    }

modules = load_modules()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "language" not in st.session_state:
    st.session_state.language = "en"

# ── Header ─────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🤖 AIVA</h1>
    <p style="font-size:18px; color:#00d4ff;">AI-Powered Voice Assistant with LLM Integration</p>
    <p style="font-size:13px; color:#888;">By Mahesh Kolekar &nbsp;|&nbsp; University Demo</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ AIVA Controls")
    st.divider()

    # Language selector
    st.markdown("### 🌐 Language")
    language = st.selectbox(
        "Choose Language",
        ["English", "Hindi", "Marathi"],
        index=0,
        label_visibility="collapsed"
    )
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr"}
    lang_code = lang_map[language]

    if st.button("✅ Apply Language", use_container_width=True):
        st.session_state.language = lang_code
        modules["lang"].set_language(lang_code)
        st.success(f"Switched to {language}!")

    st.divider()

    # Quick actions
    st.markdown("### ⚡ Quick Actions")

    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages   = []
        st.session_state.turn_count = 0
        modules["llm"].reset_conversation()
        st.success("Conversation reset!")
        st.rerun()

    if st.button("📊 System Status", use_container_width=True):
        elapsed = int(time.time() - st.session_state.start_time)
        st.info(f"""
**AIVA System Status**
- 🌐 Language : {language}
- 💬 Turns    : {st.session_state.turn_count}
- ⏱️ Uptime   : {elapsed}s
- 🧠 LLM      : Gemini 2.5 Flash
- 🎤 ASR      : faster-whisper
- 🔊 TTS      : gTTS
        """)

    st.divider()

    # Demo prompts
    st.markdown("### 🎯 Demo Prompts")

    demo_prompts = {
        "👋 Introduce AIVA":         "Hello AIVA! Please introduce yourself.",
        "🌤️ Nagpur Weather":         "What is the weather in Nagpur?",
        "🌧️ Mumbai Weather":         "What is the weather in Mumbai?",
        "🤖 What is AI?":            "What is Artificial Intelligence?",
        "🏛️ Shivaji Maharaj":        "Tell me about Chhatrapati Shivaji Maharaj",
        "🐍 What is Python?":        "What is Python programming language?",
        "🇮🇳 What is India?":         "Tell me about India",
        "🧠 How does AI work?":      "How does artificial intelligence work?",
    }

    for label, prompt in demo_prompts.items():
        if st.button(label, use_container_width=True):
            st.session_state["pending"] = prompt
            st.rerun()

    st.divider()

    # Metrics
    st.markdown("### 📈 Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Turns", st.session_state.turn_count)
    with col2:
        elapsed = int(time.time() - st.session_state.start_time)
        st.metric("⏱️ Uptime", f"{elapsed}s")

# ── Status Bar ─────────────────────────────────────────
lang_name = modules["lang"].get_language_name()
elapsed   = int(time.time() - st.session_state.start_time)

st.markdown(f"""
<div style="margin-bottom:15px;">
    <span class="status-pill">🟢 AIVA Online</span>
    <span class="status-pill">🌐 {lang_name}</span>
    <span class="status-pill">💬 Turns: {st.session_state.turn_count}</span>
    <span class="status-pill">🧠 Gemini 2.5 Flash</span>
    <span class="status-pill">⏱️ {elapsed}s</span>
</div>
""", unsafe_allow_html=True)

# ── Chat History ───────────────────────────────────────
st.markdown("### 💬 Conversation")

if not st.session_state.messages:
    st.markdown("""
    <div class="chat-aiva">
        🤖 Hello! I am AIVA, your AI-powered voice assistant.<br>
        Ask me anything in <b>English</b>, <b>Hindi</b> or <b>Marathi</b>!<br>
        Use the demo buttons on the left or type below. 👇
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-user">👤 {msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-aiva">🤖 {msg["content"]}</div>',
            unsafe_allow_html=True
        )

st.divider()

# ── Input Area ─────────────────────────────────────────
col1, col2, col3 = st.columns([5, 1, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Type your message in English, Hindi or Marathi...",
        key="input_box",
        label_visibility="collapsed"
    )
with col2:
    send = st.button("Send 🚀", use_container_width=True)

with col3:
    mic_clicked = st.button("🎤 Speak", use_container_width=True)

# ── Microphone Input ───────────────────────────────────
if mic_clicked:
    st.info("🎤 Listening... Please speak now!")
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            # Adjust for ambient noise
            st.toast("🔇 Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            st.toast("🎤 Speak now!")

            # Listen for speech
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        st.toast("⚙️ Transcribing...")

        # Try Google STT first (free, no key)
        try:
            lang_codes = {
                "en": "en-IN",
                "hi": "hi-IN",
                "mr": "mr-IN"
            }
            current_lang = st.session_state.language
            google_lang  = lang_codes.get(current_lang, "en-IN")

            spoken_text = recognizer.recognize_google(
                audio,
                language=google_lang
            )

            st.success(f"✅ You said: **{spoken_text}**")
            st.session_state["pending"] = spoken_text
            st.rerun()

        except sr.UnknownValueError:
            st.warning("⚠️ Could not understand audio. Please try again.")
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition error: {e}")

    except Exception as e:
        st.error(f"❌ Microphone error: {e}")
        st.info("💡 Make sure your microphone is connected and browser has permission.")    

# ── Handle Pending Demo Prompt ─────────────────────────
if "pending" in st.session_state:
    user_input = st.session_state.pop("pending")
    send       = True

# ── Process Input ──────────────────────────────────────
def process_input(text: str, lang: str) -> str:
    """Process user input and return AIVA response."""

    text_lower = text.lower()

    # ── Weather Intent ─────────────────────────────────
    weather_kw = {
        "en": ["weather", "temperature", "forecast", "rain"],
        "hi": ["मौसम", "तापमान", "बारिश"],
        "mr": ["हवामान", "तापमान", "पाऊस"]
    }

    if any(k in text_lower for k in weather_kw.get(lang, weather_kw["en"])):
        city = "Nagpur"  # default

        # Pattern 1: "weather in Pune"
        match = re.search(
            r"(?:weather|temperature|forecast|rain|mausam|havaman)"
            r"\s+(?:in|of|for|at)\s+([a-zA-Z\u0900-\u097F]+)",
            text,
            re.IGNORECASE
        )
        if match:
            city = match.group(1).strip()
        else:
            # Pattern 2: "Pune weather"
            match2 = re.search(
                r"([a-zA-Z\u0900-\u097F]+)"
                r"\s+(?:weather|temperature|forecast|mausam|havaman)",
                text,
                re.IGNORECASE
            )
            if match2:
                city = match2.group(1).strip()

        return modules["weather"].get_weather_for_aiva(city, language=lang)

    # ── Wikipedia Intent ───────────────────────────────
    wiki_kw = {
        "en": ["what is", "who is", "tell me about", "explain", "define"],
        "hi": ["क्या है", "कौन है", "बताओ", "समझाओ"],
        "mr": ["काय आहे", "कोण आहे", "सांगा", "समजावा"]
    }

    matched_kw = None
    for k in wiki_kw.get(lang, []):
        if k in text_lower:
            matched_kw = k
            break

    if matched_kw:
        # Keep original case — don't lowercase (breaks Wikipedia search)
        query = text.replace(matched_kw, "").replace(matched_kw.title(), "").strip()

        # Remove filler words
        for filler in ["Please", "please", "me", "?", "!", "about"]:
            query = query.replace(filler, "").strip()

        # Clean extra spaces
        query = " ".join(query.split())

        # Use original text if query too short
        if not query or len(query) < 3:
            query = text

        print(f"Wikipedia query: '{query}'")
        return modules["wiki"].search_for_aiva(query, language=lang)

    # ── Gemini LLM ─────────────────────────────────────
    lang_inst = {
        "en": "Reply in English only.",
        "hi": "Reply in Hindi only.",
        "mr": "Reply in Marathi only."
    }
    modules["llm"].system_prompt = f"""
    You are AIVA, an AI voice assistant by Mahesh Kolekar.
    Reply in short spoken sentences, no bullet points or markdown.
    Keep responses under 3 sentences.
    {lang_inst.get(lang, lang_inst['en'])}
    """
    return modules["llm"].chat(text)


if send and user_input and user_input.strip():

    # Add user message
    st.session_state.messages.append({
        "role":    "user",
        "content": user_input
    })
    st.session_state.turn_count += 1

    # Show spinner while processing
    with st.spinner("🧠 AIVA is thinking..."):
        lang = st.session_state.language
        response = process_input(user_input, lang)

    # Add AIVA response
    st.session_state.messages.append({
        "role":    "assistant",
        "content": response
    })

    # Speak the response
    try:
        modules["tts"].speak(response, language=st.session_state.language)
    except Exception as e:
        print(f"TTS error: {e}")

    st.rerun()


# ── Footer ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#444; font-size:12px; margin-top:30px;">
    AIVA — AI-Powered Voice Assistant | By Mahesh Kolekar | University Demo 2026
</div>
""", unsafe_allow_html=True)