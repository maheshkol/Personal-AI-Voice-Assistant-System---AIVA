# AIVA – AI Voice Assistant

AIVA (Artificial Intelligence Voice Assistant) is a modular AI-powered voice assistant built in Python. It combines speech recognition, multilingual support, Gemini LLM integration, text-to-speech, weather and Wikipedia tools, logging, and both CLI and Streamlit interfaces.

## Features

- 🎤 Speech-to-Text using Faster Whisper
- 🧠 Gemini LLM Integration
- 🔊 Text-to-Speech Engine
- 🌐 Multilingual Support (English, Hindi, Marathi)
- 📖 Wikipedia Search Tool
- 🌦 Weather Information Tool
- 💬 CLI Conversation Modes
- 🖥 Streamlit Web Interface
- 📝 Interaction & Error Logging
- ⏰ Wake Word Support

---

## Project Structure

```text
aiva/
├── src/aiva/
│   ├── asr/
│   ├── cli/
│   ├── config/
│   ├── llm/
│   ├── logging_system/
│   ├── multilingual/
│   ├── tools/
│   ├── tts/
│   ├── wake/
│   └── web/
├── tests/
├── requirements.txt
├── pyproject.toml
└── .env
```

## Prerequisites

- Python 3.11+
- Git
- Microphone and speakers
- Gemini API Key

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/aiva.git
cd aiva

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run CLI Version

```bash
python -m aiva
```

Available modes:

1. Voice Mode
2. Text Mode
3. Hybrid Mode

## Run Streamlit UI

```bash
streamlit run src/aiva/web/app.py
```

## Testing

```bash
pytest tests/
```

## Current Modules

| Module | Purpose |
|----------|----------|
| ASR | Speech Recognition |
| LLM | Gemini Integration |
| TTS | Text To Speech |
| Tools | Weather + Wikipedia |
| Multilingual | Language Detection & Translation |
| Logging | Session and Error Logs |
| Wake Word | Voice Activation |

## Known Issues / Improvements

- Remove hardcoded Windows paths
- Add MongoDB memory layer
- Add ChromaDB vector database
- Implement RAG pipeline
- Add Agentic AI orchestration
- Docker deployment
- AWS deployment

## Recommended GitHub Improvements

### Replace hardcoded paths

Current code contains absolute paths such as:

```python
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")
load_dotenv(r"E:\Personal AI Voice Assistant System - AIVA\aiva\.env")
```

Use relative paths with `pathlib` instead.

### Do not commit

- .env
- API keys
- logs
- cache files
- __pycache__

## Roadmap

### Phase 1
- Voice Assistant Core

### Phase 2
- Streamlit UI

### Phase 3
- Multilingual Assistant

### Phase 4
- RAG with ChromaDB

### Phase 5
- MongoDB Memory

### Phase 6
- Agentic AI

### Phase 7
- AWS Production Deployment

## Author

Mahesh S. Kolekar

Senior Infrastructure / Backup Engineer | AI & Data Science Enthusiast

## License

MIT License
