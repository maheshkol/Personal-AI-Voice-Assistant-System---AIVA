import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.wake.wake_word import WakeWordDetector

print("=== Wake Word Detector Test ===\n")

# Test with English instructions
print("--- Testing English Instructions ---")
detector = WakeWordDetector(
    mode="energy",
    sensitivity=0.6,
    wake_word="hey aiva",
    language="en"       # ← change to "hi" or "mr" to test other languages
)

# Test demo activation
print("\n--- Demo Mode Activation ---")
detector.wait_for_activation()

# Test language switching
print("\n--- Switching to Marathi ---")
detector.set_language("mr")
detector._speak_instruction("ready")

# Show status
print(f"\nStatus: {detector.get_status()}")

detector.shutdown()
print("\n✅ All wake word tests done!")