# 🎙️ AIVA — AI-Powered Voice Assistant with LLM Integration

<p align="center">
  <img src="docs/images/aiva_logo.png" alt="AIVA Logo" width="180"/>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg)
![Gemini](https://img.shields.io/badge/LLM-Gemini_2.0_Flash-orange.svg)
![Docker](https://img.shields.io/badge/Deploy-Docker_Compose-2496ED.svg)
![AWS](https://img.shields.io/badge/Cloud-AWS_EC2-FF9900.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

</p>

---

## 📖 Overview

**AIVA (AI-Powered Voice Assistant with LLM Integration)** is a cloud-deployed, multilingual voice assistant supporting **English, Hindi, and Marathi**. It was developed as an M.Sc. Data Science & AI dissertation project at **Savitribai Phule Pune University**, under the supervision of **Dr. Manisha Bharati**.

AIVA evolved from an early two-module CLI/Streamlit prototype into a production-grade system built through a full 7-phase software engineering lifecycle — requirements (SRS), architecture design, implementation, testing, deployment, and submission.

> 🎯 Target performance: sub-2.3s end-to-end latency, ~$70/month operating cost on AWS.

---

## ✨ Features

- 🎤 High-accuracy Speech Recognition (ASR)
- 🤖 LLM-powered conversational intelligence
- 🔊 Natural, multilingual Text-to-Speech
- 🌍 English, Hindi & Marathi support
- 🪄 Wake-word activation
- 📚 Wikipedia knowledge lookup
- 🌦 Real-time weather information
- 🖥 Modern React web interface
- ⚡ Sub-2.3s end-to-end response latency
- ☁️ Fully containerized cloud deployment
- 🔁 Automated CI/CD pipeline
- 🧪 Comprehensive test coverage

---

## 🏗️ System Architecture

```
                    +----------------+
                    |   User (Web)   |
                    +-------+--------+
                            |
                  Voice / Text Input
                            |
                            ▼
                 +---------------------+
                 |  Wake Word Detector |
                 |   (openWakeWord)    |
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 |   ASR (faster-      |
                 |   whisper, Large-v3)|
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 |  Language Detection |
                 |  & Preprocessing    |
                 +---------------------+
                            |
                            ▼
                 +---------------------+
                 | Gemini 2.0 Flash    |
                 |     (LLM Engine)    |
                 +---------------------+
                    |      |
              Weather   Wikipedia
              Module    Module
                    |      |
                    ▼      ▼
              Tool Integrations
                            |
                            ▼
                +----------------------+
                | TTS (Coqui XTTS-v2)  |
                +----------------------+
                            |
                            ▼
                        Audio Output
```

**Backend:** FastAPI · **Frontend:** React
**Deployment:** Docker Compose + Nginx on AWS EC2 (ap-south-1)
**CI/CD:** GitHub Actions

> Weather, Wikipedia, and LLM modules are intentionally kept as separate, decoupled components to support future agentic AI orchestration (LangChain-based routing).

---

## 📂 Project Structure

```
AIVA/
│
├── backend/
│   ├── asr/              # faster-whisper integration
│   ├── llm/               # Gemini 2.0 Flash integration
│   ├── tts/               # Coqui XTTS-v2 integration
│   ├── wake/               # openWakeWord
│   ├── tools/              # weather, wikipedia modules
│   ├── multilingual/        # EN/HI/MR preprocessing
│   ├── api/                # FastAPI routes
│   └── utils/
│
├── frontend/
│   ├── src/
│   └── public/
│
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx/
│   └── .github/workflows/   # CI/CD
│
├── tests/
├── docs/
├── logs/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Speech Recognition (ASR) | faster-whisper (Whisper Large-v3) |
| LLM | Google Gemini 2.0 Flash |
| Text-to-Speech | Coqui XTTS-v2 |
| Wake Word | openWakeWord (CNN classifier) |
| Backend | FastAPI |
| Frontend | React |
| Deployment | AWS EC2 (ap-south-1), Docker Compose, Nginx |
| CI/CD | GitHub Actions |
| Weather Data | Open-Meteo API |
| Knowledge | Wikipedia API |

---

## 📊 Key Performance Benchmarks

| Metric | Result |
|---|---|
| WER (English) | ~6.8% |
| WER (Hindi) | ~14.2% |
| End-to-end latency | ~2286 ms (avg) |
| Mean Opinion Score (MOS) | ~4.1 / 5.0 |
| System Usability Scale (SUS) | ~82 / 100 |
| Uptime | ~99.8% |

---

## 📋 Requirements

- Python 3.11+
- Node.js (for frontend build)
- Docker & Docker Compose
- Git
- Google Gemini API Key
- AWS account (for cloud deployment)

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/AIVA.git
cd AIVA
```

### Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

⚠️ **Never commit your `.env` file to GitHub.** Use `.env.example` instead.

### Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Backend
uvicorn backend.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Dockerized Deployment

```bash
docker compose -f deployment/docker-compose.yml up --build -d
```

This spins up the backend, frontend, and Nginx reverse proxy as defined in `docker-compose.yml`.

---

## ☁️ Cloud Deployment (AWS EC2)

1. Provision an EC2 instance in `ap-south-1`
2. Install Docker & Docker Compose on the instance
3. Pull the repository and configure `.env`
4. Run `docker compose up -d`
5. Nginx handles routing and reverse proxy on port 80/443
6. GitHub Actions automates build → push → deploy on each merge to `main`

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🌐 Supported Languages

- 🇺🇸 English
- 🇮🇳 Hindi
- 🇮🇳 Marathi *(initial support; full production parity in progress)*

---

## 📝 Logging

AIVA logs the following to `logs/`:

- User conversations
- ASR/TTS errors
- Session metadata
- Debug information

---

## 🚀 Future Roadmap (Phase 2)

- [ ] MongoDB Atlas — persistent conversation memory
- [ ] LangChain-based agentic AI orchestration
- [ ] AWS ECS/Fargate deployment (auto-scaling)
- [ ] RAG-based knowledge retrieval
- [ ] Mobile application
- [ ] Calendar & email assistant integrations

---

## ⚠️ Troubleshooting

**`GEMINI_API_KEY` is not set**
Add it to your `.env` file.

**Module not found**
```bash
pip install -r requirements.txt
```

**Docker build fails**
Ensure Docker Compose v2+ is installed and `.env` is present in the project root before running `docker compose up`.

**Microphone not detected (local dev)**
Check browser microphone permissions and the selected input device.

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
