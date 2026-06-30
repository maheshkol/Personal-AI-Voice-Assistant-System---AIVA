import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.tts.xtts_engine import TTSEngine

tts = TTSEngine()

# Test 1 - English
print("\n--- Test 1: English ---")
tts.speak("Hello! I am AIVA, your AI voice assistant.", language="en")

# Test 2 - Hindi
print("\n--- Test 2: Hindi ---")
tts.speak("नमस्ते! मैं AIVA हूँ, आपका AI वॉयस असिस्टेंट।", language="hi")

# Test 3 - Marathi
print("\n--- Test 3: Marathi ---")
tts.speak("नमस्कार! मी AIVA आहे, तुमचा AI व्हॉइस असिस्टंट।", language="mr")

# Test 4 - Auto language from Whisper
print("\n--- Test 4: Auto language (simulating Whisper output) ---")
tts.speak_with_detected_language(
    "This is an automated language detection test.",
    detected_lang="en"
)

tts.shutdown()
print("\n✅ All TTS tests done!")