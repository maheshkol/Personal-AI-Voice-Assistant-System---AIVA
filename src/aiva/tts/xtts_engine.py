import os
import tempfile
from gtts import gTTS
import pygame


class TTSEngine:
    """
    Text-to-Speech Engine for AIVA.
    Uses gTTS (Google Text-to-Speech) for natural voice output.
    Supports English, Hindi and Marathi.
    Uses pygame for audio playback.
    """

    # Language codes for gTTS
    LANGUAGE_CODES = {
        "en": "en",      # English
        "hi": "hi",      # Hindi
        "mr": "mr",      # Marathi ✅
        "english": "en",
        "hindi": "hi",
        "marathi": "mr"
    }

    # Friendly language names
    LANGUAGE_NAMES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi"
    }

    def __init__(self):
        """
        Initialize the TTS engine and audio player.
        """
        print("Initializing TTS Engine...")

        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        print("✅ TTS Engine ready!")
        print("   Supported: English, Hindi, Marathi")

    def speak(self, text: str, language: str = "en") -> bool:
        """
        Convert text to speech and play it out loud.

        Args:
            text:     The text to speak
            language: Language code — "en", "hi", "mr"
                      or full name — "english", "hindi", "marathi"
                      or auto-detected code from Whisper

        Returns:
            True if successful, False if error
        """
        if not text or text.strip() == "":
            print("⚠️  No text to speak!")
            return False

        # Normalize language code
        lang_code = self.LANGUAGE_CODES.get(language.lower(), "en")
        lang_name = self.LANGUAGE_NAMES.get(lang_code, "English")

        print(f"\n🔊 Speaking in {lang_name}: '{text[:50]}...' " 
              if len(text) > 50 else f"\n🔊 Speaking in {lang_name}: '{text}'")

        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=lang_code, slow=False)

            # Save to a temp MP3 file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()

            tts.save(temp_path)

            # Play the audio using pygame
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Clean up temp file
            pygame.mixer.music.unload()
            os.remove(temp_path)

            print("✅ Done speaking!")
            return True

        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False

    def speak_with_detected_language(self, text: str, detected_lang: str) -> bool:
        """
        Speak using the language detected by Whisper ASR.
        This is the main method used in the conversation loop.

        Args:
            text:          Text to speak
            detected_lang: Language code from Whisper ("en", "hi", "mr")

        Returns:
            True if successful
        """
        # Map Whisper language codes to gTTS codes
        whisper_to_gtts = {
            "en": "en",
            "hi": "hi",
            "mr": "mr",
            "english": "en",
            "hindi": "hi",
            "marathi": "mr"
        }

        lang = whisper_to_gtts.get(detected_lang, "en")
        return self.speak(text, language=lang)

    def save_to_file(self, text: str, language: str = "en",
                     output_path: str = "output.mp3") -> str:
        """
        Save speech to an MP3 file instead of playing it.
        Useful for saving demo responses.

        Args:
            text:        Text to convert
            language:    Language code
            output_path: Where to save the file

        Returns:
            Path to saved file
        """
        lang_code = self.LANGUAGE_CODES.get(language.lower(), "en")

        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(output_path)

        print(f"✅ Audio saved to: {output_path}")
        return output_path

    def shutdown(self):
        """Clean up pygame mixer on exit."""
        pygame.mixer.quit()
        print("TTS Engine shut down.")