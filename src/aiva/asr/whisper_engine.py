import os
import wave
import tempfile
import numpy as np
import pyaudio
from faster_whisper import WhisperModel


class WhisperEngine:
    """
    Handles all Speech-to-Text (ASR) for AIVA.
    Supports English, Hindi and Marathi.
    """

    # Supported languages map
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi"   # ✅ Marathi added
    }

    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper model.

        Model size recommendation:
        - "base"   → good for EN/HI (fast)
        - "small"  → better for Marathi (recommended)
        - "medium" → best Marathi accuracy (slower)

        💡 For Marathi accuracy, "small" is recommended over "base"
        """
        print(f"Loading Whisper model: {model_size} ...")

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

        print("✅ Whisper model loaded!")
        print(f"   Supported languages: English, Hindi, Marathi")

        # Audio recording settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16

    def record_audio(self, duration: int = 5) -> str:
        """
        Record audio from microphone and save to a temp WAV file.
        """
        print(f"\n🎤 Listening... (speak for up to {duration} seconds)")
        print(f"   Speak in English, Hindi or Marathi")

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        frames = []

        for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        print("✅ Recording done!")

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        return temp_file.name

    def transcribe(self, audio_path: str, force_language: str = None) -> dict:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to WAV file
            force_language: Force a specific language
                            "en" = English
                            "hi" = Hindi
                            "mr" = Marathi
                            None = Auto detect (default)

        Returns:
            dict with 'text', 'language', 'language_name', 'confidence'
        """
        print("⚙️  Transcribing audio...")

        # If language is forced, use it — otherwise auto detect
        lang = force_language if force_language else None

        if lang:
            lang_name = self.SUPPORTED_LANGUAGES.get(lang, lang)
            print(f"   Forced language: {lang_name}")
        else:
            print("   Auto-detecting language (EN / HI / MR)...")

        segments, info = self.model.transcribe(
            audio_path,
            language=lang,          # None = auto detect
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500
            )
        )

        # Combine all segments
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "

        full_text = full_text.strip()

        detected_lang = info.language
        confidence = round(info.language_probability * 100, 1)
        lang_name = self.SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)

        print(f"✅ Transcribed: '{full_text}'")
        print(f"   Language: {lang_name} ({detected_lang}) — {confidence}% confidence")

        # Warn if unsupported language detected
        if detected_lang not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  Warning: Detected '{detected_lang}' which is outside EN/HI/MR")

        # Clean up temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "text": full_text,
            "language": detected_lang,
            "language_name": lang_name,
            "confidence": confidence
        }

    def listen_and_transcribe(self, duration: int = 5, force_language: str = None) -> dict:
        """
        One-shot: Record from mic + transcribe.

        Args:
            duration: Recording duration in seconds
            force_language: "en", "hi", "mr" or None for auto

        Returns:
            dict with text, language, language_name, confidence
        """
        audio_path = self.record_audio(duration=duration)
        result = self.transcribe(audio_path, force_language=force_language)
        return result