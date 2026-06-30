import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.multilingual.lang_detector import LanguageDetector

detector = LanguageDetector(default_language="en")

print("\n--- Test 1: Detect from Whisper codes ---")
print(detector.detect_from_whisper("en"))   # → en
print(detector.detect_from_whisper("hi"))   # → hi
print(detector.detect_from_whisper("mr"))   # → mr

print("\n--- Test 2: Detect from text ---")
print(detector.detect_from_text("Hello how are you"))           # → en
print(detector.detect_from_text("नमस्ते आप कैसे हैं"))          # → hi
print(detector.detect_from_text("नमस्कार तुम्ही कसे आहात"))     # → mr

print("\n--- Test 3: Manual language switch ---")
detector.set_language("marathi")
print(f"Current: {detector.get_language_name()}")
print(f"Greeting: {detector.get_greeting()}")
print(f"LLM instruction: {detector.get_llm_instruction()}")

print("\n--- Test 4: Language history ---")
detector.detect_from_whisper("en")
detector.detect_from_whisper("hi")
detector.detect_from_whisper("mr")
detector.detect_from_whisper("en")
detector.detect_from_whisper("en")
print(f"History: {detector.detection_history}")
print(f"Dominant: {detector.get_dominant_language()}")

print("\n--- Full Status ---")
print(detector.get_status())

print("\n✅ All multilingual tests done!")