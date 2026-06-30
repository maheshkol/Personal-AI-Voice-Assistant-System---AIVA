import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

print("Testing imports one by one...\n")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI: {e}")

try:
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ CORSMiddleware imported")
except Exception as e:
    print(f"❌ CORSMiddleware: {e}")

try:
    from aiva.llm.gemini_client import GeminiClient
    print("✅ GeminiClient imported")
except Exception as e:
    print(f"❌ GeminiClient: {e}")

try:
    from aiva.tts.xtts_engine import TTSEngine
    print("✅ TTSEngine imported")
except Exception as e:
    print(f"❌ TTSEngine: {e}")

try:
    from aiva.tools.weather import WeatherTool
    print("✅ WeatherTool imported")
except Exception as e:
    print(f"❌ WeatherTool: {e}")

try:
    from aiva.tools.wikipedia_tool import WikipediaTool
    print("✅ WikipediaTool imported")
except Exception as e:
    print(f"❌ WikipediaTool: {e}")

try:
    from aiva.multilingual.lang_detector import LanguageDetector
    print("✅ LanguageDetector imported")
except Exception as e:
    print(f"❌ LanguageDetector: {e}")

try:
    from aiva.web.websocket_server import app
    print("✅ app imported")
except Exception as e:
    print(f"❌ app: {e}")