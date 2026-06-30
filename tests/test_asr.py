import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.asr.whisper_engine import WhisperEngine

asr = WhisperEngine(model_size="small")  # small is better for Marathi

print("\n--- Test 1: Auto Language Detection ---")
print("Speak in English, Hindi or Marathi...")
result = asr.listen_and_transcribe(duration=5)
print(f"📝 Text: {result['text']}")
print(f"🌐 Language: {result['language_name']} ({result['language']})")
print(f"📊 Confidence: {result['confidence']}%")

print("\n--- Test 2: Force Marathi ---")
print("Speak in Marathi...")
result = asr.listen_and_transcribe(duration=5, force_language="mr")
print(f"📝 Text: {result['text']}")
print(f"🌐 Language: {result['language_name']}")