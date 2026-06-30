"""
wake_word.py — Wake Word Detector for AIVA
==========================================
Listens continuously for "Hey AIVA" before activating the main pipeline.

Two detection modes:
  - "energy"  : Simple RMS energy threshold (no extra deps, fast)
  - "oww"     : openWakeWord model (more accurate, requires openwakeword)

Multilingual audio instructions (English, Hindi, Marathi) via gTTS + pygame.

Usage:
    from wake_word import WakeWordDetector

    detector = WakeWordDetector(mode="energy", language="en")
    if detector.listen_for_wake_word(timeout=30):
        # start main AIVA pipeline
        ...
    detector.shutdown()
"""

import os
import time
import threading
import tempfile

import pyaudio
import numpy as np
from gtts import gTTS
import pygame


class WakeWordDetector:
    """
    Wake Word Detector for AIVA.

    Listens continuously for "Hey AIVA" before activating the pipeline.
    Speaks audio instructions in English, Hindi and Marathi.

    Args:
        mode (str):         "energy" for volume-based detection (default),
                            "oww" for openWakeWord model (more accurate).
        sensitivity (float): 0.0 (least sensitive) to 1.0 (most sensitive).
                              Default 0.6.
        wake_word (str):    Phrase to listen for. Default "hey aiva".
        language (str):     Instruction audio language — "en", "hi", or "mr".
    """

    # ------------------------------------------------------------------ #
    #  Constants                                                           #
    # ------------------------------------------------------------------ #

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
    }

    INSTRUCTIONS = {
        "en": {
            "startup":  "AIVA is starting up. Please wait.",
            "ready":    "AIVA is ready. Say Hey AIVA to wake me up, or press Enter.",
            "detected": "Wake word detected! AIVA is now listening.",
            "timeout":  "No wake word detected. Please try again.",
            "activated":"AIVA activated! I am listening, please speak now.",
            "sleeping": "AIVA is sleeping. Say Hey AIVA to wake me up.",
        },
        "hi": {
            "startup":  "AIVA शुरू हो रही है। कृपया प्रतीक्षा करें।",
            "ready":    "AIVA तैयार है। मुझे जगाने के लिए Hey AIVA बोलें।",
            "detected": "वेक वर्ड मिला! AIVA अब सुन रही है।",
            "timeout":  "कोई वेक वर्ड नहीं मिला। कृपया पुनः प्रयास करें।",
            "activated":"AIVA सक्रिय हो गई! मैं सुन रही हूँ, कृपया बोलें।",
            "sleeping": "AIVA सो रही है। जगाने के लिए Hey AIVA बोलें।",
        },
        "mr": {
            "startup":  "AIVA सुरू होत आहे. कृपया थांबा.",
            "ready":    "AIVA तयार आहे. मला जागे करण्यासाठी Hey AIVA म्हणा.",
            "detected": "वेक वर्ड आढळले! AIVA आता ऐकत आहे.",
            "timeout":  "वेक वर्ड आढळले नाही. कृपया पुन्हा प्रयत्न करा.",
            "activated":"AIVA सक्रिय झाली! मी ऐकत आहे, कृपया बोला.",
            "sleeping": "AIVA झोपत आहे. जागे करण्यासाठी Hey AIVA म्हणा.",
        },
    }

    # PyAudio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE  = 1024
    FORMAT      = pyaudio.paInt16
    CHANNELS    = 1

    # ------------------------------------------------------------------ #
    #  Initialisation                                                      #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        mode: str = "energy",
        sensitivity: float = 0.6,
        wake_word: str = "hey aiva",
        language: str = "en",
    ):
        self.mode        = mode
        self.sensitivity = sensitivity
        self.wake_word   = wake_word.lower()
        self.language    = language if language in self.SUPPORTED_LANGUAGES else "en"

        # Energy threshold: higher sensitivity → lower threshold → triggers more easily
        self.energy_threshold = int(500 * (1.0 - sensitivity))

        # pygame for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        print("✅ WakeWordDetector initialised")
        print(f"   mode        : {self.mode}")
        print(f"   wake word   : '{self.wake_word}'")
        print(f"   language    : {self.SUPPORTED_LANGUAGES[self.language]}")
        print(f"   sensitivity : {self.sensitivity}  (energy threshold: {self.energy_threshold})")

        self._speak_instruction("startup")

        # openWakeWord model (loaded only when mode == "oww")
        self.oww_model = None
        if self.mode == "oww":
            self._load_oww()

    # ------------------------------------------------------------------ #
    #  Audio instruction playback                                          #
    # ------------------------------------------------------------------ #

    def _speak_instruction(self, key: str) -> None:
        """
        Speak a localised instruction message using gTTS + pygame.

        Falls back to console print if audio fails (e.g. no speakers).

        Args:
            key: One of "startup", "ready", "detected", "timeout",
                 "activated", "sleeping".
        """
        message = self.INSTRUCTIONS[self.language][key]
        print(f"🔊 [{key.upper()}] {message}")

        try:
            tts = gTTS(text=message, lang=self.language, slow=False)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            tts.save(tmp_path)
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

            # Block until playback finishes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(tmp_path)

        except Exception as exc:
            # Audio failure is non-fatal — message was already printed above
            print(f"⚠️  Audio playback failed: {exc}")

    # ------------------------------------------------------------------ #
    #  Detection helpers                                                   #
    # ------------------------------------------------------------------ #

    def _rms_energy(self, chunk: bytes) -> float:
        """Return the RMS energy of a raw PCM audio chunk."""
        arr = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
        return float(np.sqrt(np.mean(arr ** 2)))

    def _detect_energy(self, chunk: bytes) -> bool:
        """
        Energy-based detection.

        Returns True when the audio chunk is louder than the configured
        threshold — a simple but effective proxy for speech activity in
        a quiet environment.
        """
        return self._rms_energy(chunk) > self.energy_threshold

    def _load_oww(self) -> None:
        """
        Load the openWakeWord model.

        Gracefully falls back to energy mode if the package is missing
        or the model fails to load.
        """
        try:
            from openwakeword.model import Model  # type: ignore
            print("⏳ Loading openWakeWord model…")
            self.oww_model = Model(wakeword_models=[], inference_framework="onnx")
            print("✅ openWakeWord model loaded")
        except ImportError:
            print("⚠️  openwakeword not installed → falling back to energy mode")
            self.mode = "energy"
        except Exception as exc:
            print(f"⚠️  openWakeWord load error: {exc} → falling back to energy mode")
            self.mode = "energy"

    def _detect_oww(self, chunk: bytes) -> bool:
        """
        openWakeWord-based detection.

        Returns True when any model score exceeds the configured
        sensitivity threshold.
        """
        try:
            arr = np.frombuffer(chunk, dtype=np.int16)
            predictions = self.oww_model.predict(arr)
            return any(score > self.sensitivity for score in predictions.values())
        except Exception as exc:
            print(f"⚠️  OWW predict error: {exc}")
            return False

    def _is_wake_word(self, chunk: bytes) -> bool:
        """Dispatch to the configured detection backend."""
        if self.mode == "oww" and self.oww_model is not None:
            return self._detect_oww(chunk)
        return self._detect_energy(chunk)

    # ------------------------------------------------------------------ #
    #  Public listening API                                                #
    # ------------------------------------------------------------------ #

    def listen_for_wake_word(self, timeout: int = 30) -> bool:
        """
        Block until the wake word is heard or the timeout expires.

        Speaks localised audio prompts to guide the user.
        A keyboard interrupt (Ctrl-C) counts as immediate activation.

        Args:
            timeout: Maximum seconds to listen. 0 = listen forever.

        Returns:
            True  — wake word detected (or keyboard interrupt).
            False — timed out without detection.
        """
        self._speak_instruction("ready")

        audio  = pyaudio.PyAudio()
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        print(f"\n😴 Listening for '{self.wake_word}' "
              f"({'∞' if timeout == 0 else timeout}s timeout)…")

        detected   = False
        start_time = time.time()

        try:
            while True:
                # Check timeout
                if timeout > 0 and (time.time() - start_time) > timeout:
                    self._speak_instruction("timeout")
                    break

                chunk = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

                if self._is_wake_word(chunk):
                    self._speak_instruction("detected")
                    time.sleep(0.3)   # brief pause so the prompt finishes
                    detected = True
                    break

        except KeyboardInterrupt:
            print("\n⌨️  Keyboard interrupt — activating AIVA")
            self._speak_instruction("activated")
            detected = True

        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        return detected

    def wait_for_activation(self) -> bool:
        """
        Demo / presentation mode.

        Speaks the 'sleeping' prompt then waits for either:
          • a sound loud enough to cross the energy threshold, or
          • the user pressing Enter in the terminal.

        This is the most convenient mode for classroom demos where you
        want a visible fallback. Always returns True.
        """
        self._speak_instruction("sleeping")

        activated = threading.Event()

        def _audio_listener():
            """Background thread: watch for audio energy."""
            audio  = pyaudio.PyAudio()
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE,
            )

            # Short delay so the startup speech doesn't trigger detection
            time.sleep(1.5)

            try:
                while not activated.is_set():
                    chunk = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    if self._detect_energy(chunk):
                        activated.set()
            except Exception:
                pass
            finally:
                stream.stop_stream()
                stream.close()
                audio.terminate()

        thread = threading.Thread(target=_audio_listener, daemon=True)
        thread.start()

        try:
            input()   # unblocks on Enter key
        except Exception:
            pass

        activated.set()   # ensure the background thread exits
        self._speak_instruction("activated")
        return True

    # ------------------------------------------------------------------ #
    #  Configuration & utility                                             #
    # ------------------------------------------------------------------ #

    def set_language(self, language: str) -> None:
        """
        Switch the instruction language at runtime.

        Args:
            language: "en", "hi", or "mr".
        """
        if language in self.SUPPORTED_LANGUAGES:
            self.language = language
            print(f"✅ Language set to: {self.SUPPORTED_LANGUAGES[language]}")
        else:
            supported = ", ".join(self.SUPPORTED_LANGUAGES.keys())
            print(f"⚠️  Unknown language '{language}'. Use one of: {supported}")

    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Adjust detection sensitivity at runtime.

        Args:
            sensitivity: Float in [0.0, 1.0].
        """
        self.sensitivity      = max(0.0, min(1.0, sensitivity))
        self.energy_threshold = int(500 * (1.0 - self.sensitivity))
        print(f"✅ Sensitivity set to {self.sensitivity} "
              f"(energy threshold: {self.energy_threshold})")

    def get_status(self) -> dict:
        """
        Return a snapshot of the current detector configuration.

        Returns:
            dict with keys: mode, wake_word, sensitivity, language,
            language_name, energy_threshold, oww_loaded.
        """
        return {
            "mode":             self.mode,
            "wake_word":        self.wake_word,
            "sensitivity":      self.sensitivity,
            "language":         self.language,
            "language_name":    self.SUPPORTED_LANGUAGES[self.language],
            "energy_threshold": self.energy_threshold,
            "oww_loaded":       self.oww_model is not None,
        }

    def shutdown(self) -> None:
        """Release pygame mixer resources."""
        pygame.mixer.quit()
        print("Wake Word Detector shut down.")


# ------------------------------------------------------------------ #
#  Quick smoke-test — run this file directly to verify it works       #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import sys

    print("=" * 50)
    print("  AIVA Wake Word Detector — self-test")
    print("=" * 50)

    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    mode = sys.argv[2] if len(sys.argv) > 2 else "energy"

    detector = WakeWordDetector(mode=mode, sensitivity=0.6, language=lang)
    print(f"\nStatus: {detector.get_status()}\n")

    print("--- Demo activation (speak or press Enter) ---")
    detector.wait_for_activation()

    print("\n--- Switching language to Hindi ---")
    detector.set_language("hi")
    detector._speak_instruction("ready")

    print("\n--- Adjusting sensitivity ---")
    detector.set_sensitivity(0.8)

    detector.shutdown()
    print("\n✅ Self-test complete.")