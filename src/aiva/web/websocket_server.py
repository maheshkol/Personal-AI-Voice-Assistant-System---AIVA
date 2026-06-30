import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

import json
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from aiva.llm.gemini_client import GeminiClient
from aiva.tts.xtts_engine import TTSEngine
from aiva.tools.weather import WeatherTool
from aiva.tools.wikipedia_tool import WikipediaTool
from aiva.multilingual.lang_detector import LanguageDetector


# ── FastAPI App ────────────────────────────────────────
app = FastAPI(
    title="AIVA API",
    description="AI-Powered Voice Assistant Backend",
    version="1.0.0"
)

print("✅ FastAPI app object created")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Initialize Modules ─────────────────────────────────
llm           = GeminiClient()
tts           = TTSEngine()
weather_tool  = WeatherTool()
wiki_tool     = WikipediaTool()
lang_detector = LanguageDetector("en")

# Track stats
stats = {
    "total_requests": 0,
    "start_time":     time.time(),
    "active_connections": 0
}


class WebSocketServer:
    """
    FastAPI WebSocket Server for AIVA Web Frontend.
    Handles real-time bidirectional communication.
    """

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        stats["active_connections"] = len(self.active_connections)
        print(f"✅ WebSocket connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        stats["active_connections"] = len(self.active_connections)
        print(f"🔴 WebSocket disconnected. Active: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: dict):
        await websocket.send_text(json.dumps(message))


ws_server = WebSocketServer()


# ── REST Endpoints ─────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name":    "AIVA API",
        "version": "1.0.0",
        "status":  "running",
        "author":  "Mahesh Kolekar"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status":  "healthy",
        "uptime":  int(time.time() - stats["start_time"]),
        "active_connections": stats["active_connections"]
    }


@app.get("/api/v1/metrics")
async def get_metrics():
    """System metrics endpoint."""
    return {
        "total_requests":     stats["total_requests"],
        "active_connections": stats["active_connections"],
        "uptime_seconds":     int(time.time() - stats["start_time"]),
        "language":           lang_detector.get_current_language(),
        "language_name":      lang_detector.get_language_name()
    }


@app.post("/api/v1/chat")
async def chat_endpoint(request: dict):
    """
    REST chat endpoint.
    Accepts: { "message": "...", "language": "en" }
    Returns: { "response": "...", "language": "en" }
    """
    stats["total_requests"] += 1

    message  = request.get("message", "")
    language = request.get("language", "en")

    if not message:
        return JSONResponse(
            status_code=400,
            content={"error": "message is required"}
        )

    lang_detector.set_language(language)
    response = generate_response (message, language)

    return {
        "response": response,
        "language": language,
        "turn":     stats["total_requests"]
    }


@app.get("/api/v1/weather/{city}")
async def get_weather(city: str, lang: str = "en"):
    """Weather endpoint."""
    result = weather_tool.get_weather(city)
    voice  = weather_tool.format_for_voice(result, language=lang)
    return {"city": city, "weather": result, "voice_response": voice}


@app.get("/api/v1/wiki/{query}")
async def get_wiki(query: str, lang: str = "en"):
    """Wikipedia endpoint."""
    result = wiki_tool.search(query, language=lang)
    voice  = wiki_tool.format_for_voice(result, language=lang)
    return {"query": query, "result": result, "voice_response": voice}


# ── WebSocket Endpoint ─────────────────────────────────
@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice communication.

    Client sends: { "type": "text", "message": "...", "language": "en" }
    Server sends: { "type": "response", "message": "...", "language": "en" }
    """
    await ws_server.connect(websocket)

    try:
        # Send welcome message
        await ws_server.send_message(websocket, {
            "type":    "connected",
            "message": "AIVA WebSocket connected!",
            "status":  "ready"
        })

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            payload = json.loads(data)

            msg_type = payload.get("type", "text")
            message  = payload.get("message", "")
            language = payload.get("language", "en")

            stats["total_requests"] += 1

            # Send acknowledgment
            await ws_server.send_message(websocket, {
                "type":    "processing",
                "message": "Processing your request..."
            })

            # Generate response
            if msg_type == "text":
                response = generate_response (message, language)

                await ws_server.send_message(websocket, {
                    "type":     "response",
                    "message":  response,
                    "language": language,
                    "turn":     stats["total_requests"]
                })

            elif msg_type == "ping":
                await ws_server.send_message(websocket, {
                    "type": "pong",
                    "time": time.time()
                })

    except WebSocketDisconnect:
        ws_server.disconnect(websocket)

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await ws_server.send_message(websocket, {
                "type":  "error",
                "message": str(e)
            })
        except:
            pass
        ws_server.disconnect(websocket)


def generate_response (message: str, language: str) -> str:
    """
    Generate AIVA response for a message.
    Checks for tool intents before calling LLM.

    Args:
        message:  User message text
        language: Language code

    Returns:
        Response string
    """
    text_lower = message.lower()

    # Weather intent
    weather_keywords = {
        "en": ["weather", "temperature", "forecast"],
        "hi": ["मौसम", "तापमान"],
        "mr": ["हवामान", "तापमान"]
    }
    if any(k in text_lower for k in weather_keywords.get(language, [])):
        cities = [
            "nagpur", "mumbai", "pune", "delhi",
            "bangalore", "hyderabad", "chennai"
        ]
        city = "Nagpur"
        for c in cities:
            if c in text_lower:
                city = c.capitalize()
                break
        return weather_tool.get_weather_for_aiva(city, language=language)

    # Wikipedia intent
    wiki_keywords = {
        "en": ["what is", "who is", "tell me about", "explain"],
        "hi": ["क्या है", "कौन है", "बताओ"],
        "mr": ["काय आहे", "कोण आहे", "सांगा"]
    }
    if any(k in text_lower for k in wiki_keywords.get(language, [])):
        query = message
        for k in wiki_keywords.get(language, []):
            query = query.lower().replace(k, "").strip()
        return wiki_tool.search_for_aiva(query, language=language)

    # Gemini LLM
    lang_instructions = {
        "en": "Reply in English only. Keep it short and conversational.",
        "hi": "Reply in Hindi only. Keep it short and conversational.",
        "mr": "Reply in Marathi only. Keep it short and conversational."
    }
    llm.system_prompt = f"""
    You are AIVA, an AI voice assistant by Mahesh Kolekar.
    Reply in short spoken sentences, no bullet points or markdown.
    Keep responses under 3 sentences.
    {lang_instructions.get(language, lang_instructions['en'])}
    """
    return llm.chat(message)