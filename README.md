# 🎙️ AIVA — AI-Powered Voice Assistant with LLM Integration

<p align="center">
  <img src="docs/images/aiva_logo.png" alt="AIVA Logo" width="180"/>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)
![Gemini](https://img.shields.io/badge/LLM-Gemini_2.0_Flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

</p>

---

## 📖 Overview

**AIVA (AI-Powered Voice Assistant with LLM Integration)** is a multilingual, modular voice assistant supporting **English, Hindi, and Marathi**. It was developed as an M.Sc. Data Science & AI dissertation project at **Savitribai Phule Pune University**, under the supervision of **Dr. Manisha Bharati**.

AIVA combines speech recognition, an LLM conversational engine, text-to-speech, wake-word activation, and tool integrations (weather, Wikipedia) into one modular Python package — accessible via a **CLI**, a **Streamlit web UI**, or a **FastAPI WebSocket API**.

---

## ✨ Features

- 🎤 Speech-to-Text using **faster-whisper**
- 🤖 Conversational intelligence via **Google Gemini 2.0 Flash**
- 🔊 Text-to-Speech via **gTTS** with audio playback through **pygame**
- 🌍 English, Hindi & Marathi support (ASR, TTS, and translation)
- 🪄 Wake-word activation ("Hey AIVA") with energy-based and openWakeWord detection modes
- 📚 Wikipedia knowledge lookup (multilingual)
- 🌦 Real-time weather lookup via the free Open-Meteo API (no key required)
- 🖥 Streamlit-based web interface
- 🌐 FastAPI + WebSocket server for real-time, low-latency interaction
- ⌨️ CLI conversation loop
- 📝 Structured session, interaction, and error logging
- 🧪 Pytest-based test suite

---

## 🏗️ Architecture

```
                    +----------------+
                    |     User       |
                    +-------+--------+
                            |
                  Voice / Text Input
                            |
                            ▼
                 +---------------------+
                 |  Wake Word Detector |
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 |  ASR (faster-       |
                 |  whisper)           |
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 | Language Detection  |
                 | & Translation Layer |
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 | Gemini 2.0 Flash    |
                 |   (LLM Engine)      |
                 +---------------------+
                    |      |
              Weather   Wikipedia
                    |      |
                    ▼      ▼
              Tool Integrations
                            |
                            ▼
                +----------------------+
                |   TTS (gTTS +        |
                |   pygame playback)   |
                +----------------------+
                            |
                            ▼
                        Audio Output
```

> Weather, Wikipedia, and LLM modules are intentionally kept decoupled to support future agentic routing (LangChain-based orchestration is planned for Phase 2).

---

## 📂 Project Structure

```
aiva/
│
├── src/aiva/
│   ├── asr/                 # faster-whisper speech recognition
│   ├── llm/                 # Gemini 2.0 Flash client
│   ├── tts/                 # gTTS + pygame text-to-speech engine
│   ├── wake/                 # Wake-word detection
│   ├── multilingual/          # Language detection & translation
│   ├── tools/                 # Weather (Open-Meteo) & Wikipedia tools
│   ├── cli/                    # CLI conversation loop
│   ├── web/                    # Streamlit app + FastAPI WebSocket server
│   ├── logging_system/          # Session, interaction & error logging
│   └── config/                  # Settings
│
├── tests/                  # Pytest test suite
├── logs/                   # Runtime logs (sessions / interactions / errors)
├── run_api.py              # Entry point: FastAPI WebSocket server
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Speech Recognition (ASR) | faster-whisper |
| LLM | Google Gemini 2.0 Flash (`google-genai`) |
| Text-to-Speech | gTTS + pygame |
| Wake Word | Energy-based detection / openWakeWord |
| Web UI | Streamlit |
| API Server | FastAPI + WebSockets, Uvicorn |
| Weather Data | Open-Meteo API (free, no key) |
| Knowledge | Wikipedia API |
| Config & Env | python-dotenv, pydantic, PyYAML |
| Caching | Redis |
| Testing | Pytest |

---

## 📋 Requirements

- Python 3.11+
- Git
- Microphone & speakers (for voice mode)
- Google Gemini API key

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/AIVA.git
cd AIVA
```

### Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

or, as an editable package:

```bash
pip install -e .
```

### Configure environment variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

⚠️ **Never commit your `.env` file or any file containing API keys to GitHub.**

---

## ▶️ Running AIVA

### CLI mode

```bash
python -m aiva.cli.conversation_loop
```

### Streamlit Web UI

```bash
streamlit run src/aiva/web/app.py
```

### FastAPI WebSocket Server

```bash
python run_api.py
```

- Server: `http://localhost:8080`
- API docs: `http://localhost:8080/docs`

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🌐 Supported Languages

- 🇺🇸 English
- 🇮🇳 Hindi
- 🇮🇳 Marathi

---

## 📝 Logging

AIVA logs structured records to `logs/`:

- `logs/sessions/` — session metadata
- `logs/interactions/` — user input, detected language, translated text, intent, tool used, response, latency
- `logs/errors/` — error traces and tracebacks

---

## 🚀 Roadmap (Phase 2)

- [ ] Containerized deployment (Docker Compose + Nginx)
- [ ] Cloud deployment on AWS EC2/ECS
- [ ] CI/CD via GitHub Actions
- [ ] React-based frontend
- [ ] MongoDB Atlas — persistent conversation memory
- [ ] LangChain-based agentic AI orchestration
- [ ] RAG-based knowledge retrieval

---

## ⚠️ Troubleshooting

**`GEMINI_API_KEY not found in .env`**
Make sure `.env` exists in the project root with a valid key.

**Module not found**
```bash
pip install -r requirements.txt
```

**Microphone not detected**
Check microphone permissions and that the correct input device is selected at the OS level.

**Streamlit not found**
```bash
pip install streamlit
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m "Added new feature"`
4. Push: `git push origin feature/new-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Mahesh Kolekar**

M.Sc. Data Science & AI · Savitribai Phule Pune University
Supervisor: Dr. Manisha Bharati

- 💼 Infrastructure | Backup | Cloud | AI
- 🐍 Python Developer · 🤖 Generative AI Developer
- 📍 Pune, Maharashtra, India

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub — it helps others discover the project and supports future development.
