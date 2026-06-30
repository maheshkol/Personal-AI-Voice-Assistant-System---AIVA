import re


class LanguageDetector:
    """
    Language Detector for AIVA.
    Detects and manages language switching between
    English, Hindi and Marathi.

    Works in two ways:
    1. Uses Whisper's detected language code directly
    2. Text-based detection using character patterns
    """

    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "gtts_code": "en",
            "whisper_code": "en",
            "greeting": "Hello! I am AIVA. How can I help you?",
            "prompt_instruction": "Reply in English only. Keep responses short and conversational."
        },
        "hi": {
            "name": "Hindi",
            "gtts_code": "hi",
            "whisper_code": "hi",
            "greeting": "नमस्ते! मैं AIVA हूँ। मैं आपकी कैसे मदद कर सकती हूँ?",
            "prompt_instruction": "Reply in Hindi only. Keep responses short and conversational."
        },
        "mr": {
            "name": "Marathi",
            "gtts_code": "mr",
            "whisper_code": "mr",
            "greeting": "नमस्कार! मी AIVA आहे. मी तुमची कशी मदत करू शकतो?",
            "prompt_instruction": "Reply in Marathi only. Keep responses short and conversational."
        }
    }

    def __init__(self, default_language: str = "en"):
        """
        Initialize Language Detector.

        Args:
            default_language: Default language code "en", "hi", "mr"
        """
        self.current_language = default_language \
            if default_language in self.SUPPORTED_LANGUAGES else "en"

        self.previous_language = None
        self.switch_count = 0       # Track how many times language switched
        self.detection_history = [] # Keep last 5 detections

        print(f"✅ Language Detector initialized!")
        print(f"   Default language: {self.get_language_name()}")
        print(f"   Supported: English, Hindi, Marathi")

    def detect_from_whisper(self, whisper_lang_code: str) -> str:
        """
        Get language from Whisper's auto-detection output.
        This is the PRIMARY detection method.

        Args:
            whisper_lang_code: Language code from Whisper
                               e.g. "en", "hi", "mr"

        Returns:
            Normalized language code "en", "hi", or "mr"
        """
        code = whisper_lang_code.lower().strip()

        # Direct match
        if code in self.SUPPORTED_LANGUAGES:
            detected = code

        # Handle variations Whisper might return
        elif code in ["english", "en-in", "en-us", "en-gb"]:
            detected = "en"

        elif code in ["hindi", "hin", "hi-in"]:
            detected = "hi"

        elif code in ["marathi", "mar", "mr-in"]:
            detected = "mr"

        else:
            # Unknown language — keep current
            print(f"⚠️  Unknown language '{code}' — keeping {self.current_language}")
            detected = self.current_language

        # Update history
        self._update_history(detected)

        return detected

    def detect_from_text(self, text: str) -> str:
        """
        Detect language from text using Unicode character patterns.
        Used as fallback when Whisper confidence is low.

        Args:
            text: Input text to analyze

        Returns:
            Detected language code "en", "hi", or "mr"
        """
        if not text or text.strip() == "":
            return self.current_language

        # Count character types
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
        latin_count = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(text.replace(" ", ""))

        if total_chars == 0:
            return self.current_language

        devanagari_ratio = devanagari_count / total_chars

        # If mostly Devanagari script → Hindi or Marathi
        if devanagari_ratio > 0.4:
            # Look for Marathi-specific words
            marathi_words = [
                "आहे", "आहेत", "होते", "होती", "करा", "सांगा",
                "मला", "तुम्ही", "काय", "कसे", "माझे", "तुमचे",
                "नाही", "हे", "ते", "मी", "तू", "आम्ही"
            ]
            hindi_words = [
                "है", "हैं", "था", "थी", "करो", "बताओ",
                "मुझे", "आप", "क्या", "कैसे", "मेरा", "आपका",
                "नहीं", "यह", "वह", "मैं", "तुम", "हम"
            ]

            marathi_score = sum(1 for w in marathi_words if w in text)
            hindi_score = sum(1 for w in hindi_words if w in text)

            if marathi_score > hindi_score:
                detected = "mr"
            elif hindi_score > marathi_score:
                detected = "hi"
            else:
                # Default Devanagari to Hindi if can't distinguish
                detected = "hi"

        # Mostly Latin characters → English
        elif latin_count / total_chars > 0.5:
            detected = "en"

        else:
            detected = self.current_language

        self._update_history(detected)
        return detected

    def update_language(self, new_language: str) -> bool:
        """
        Update the current active language.
        Called after each Whisper transcription.

        Args:
            new_language: New language code "en", "hi", "mr"

        Returns:
            True if language changed, False if same language
        """
        if new_language not in self.SUPPORTED_LANGUAGES:
            print(f"⚠️  Unsupported language: {new_language}")
            return False

        if new_language != self.current_language:
            self.previous_language = self.current_language
            self.current_language = new_language
            self.switch_count += 1

            old_name = self.SUPPORTED_LANGUAGES[self.previous_language]["name"]
            new_name = self.SUPPORTED_LANGUAGES[new_language]["name"]

            print(f"🌐 Language switched: {old_name} → {new_name}")
            return True

        return False

    def set_language(self, language: str) -> bool:
        """
        Manually set language (from user command).

        Args:
            language: "en", "hi", "mr",
                      or "english", "hindi", "marathi"

        Returns:
            True if set successfully
        """
        # Handle full names
        name_to_code = {
            "english": "en",
            "hindi": "hi",
            "marathi": "mr",
            "en": "en",
            "hi": "hi",
            "mr": "mr"
        }

        code = name_to_code.get(language.lower())

        if not code:
            print(f"⚠️  Unknown language: '{language}'")
            print(f"   Use: en, hi, mr, english, hindi, marathi")
            return False

        return self.update_language(code)

    def get_llm_instruction(self) -> str:
        """
        Get the LLM prompt instruction for current language.
        Injected into Gemini system prompt to force correct language reply.

        Returns:
            Instruction string for Gemini
        """
        return self.SUPPORTED_LANGUAGES[self.current_language]["prompt_instruction"]

    def get_greeting(self) -> str:
        """
        Get greeting message in current language.
        Used when AIVA first starts.

        Returns:
            Greeting string
        """
        return self.SUPPORTED_LANGUAGES[self.current_language]["greeting"]

    def get_gtts_code(self) -> str:
        """Get gTTS language code for current language."""
        return self.SUPPORTED_LANGUAGES[self.current_language]["gtts_code"]

    def get_language_name(self) -> str:
        """Get friendly name of current language."""
        return self.SUPPORTED_LANGUAGES[self.current_language]["name"]

    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language

    def _update_history(self, detected_lang: str):
        """Keep last 5 detections in history."""
        self.detection_history.append(detected_lang)
        if len(self.detection_history) > 5:
            self.detection_history.pop(0)

    def get_dominant_language(self) -> str:
        """
        Get the most used language from recent history.
        Useful for stabilizing language detection.

        Returns:
            Most frequent language in last 5 detections
        """
        if not self.detection_history:
            return self.current_language

        # Count occurrences
        counts = {}
        for lang in self.detection_history:
            counts[lang] = counts.get(lang, 0) + 1

        return max(counts, key=counts.get)

    def get_status(self) -> dict:
        """Return full language detector status."""
        return {
            "current_language": self.current_language,
            "current_language_name": self.get_language_name(),
            "previous_language": self.previous_language,
            "switch_count": self.switch_count,
            "detection_history": self.detection_history,
            "dominant_language": self.get_dominant_language(),
            "supported_languages": list(self.SUPPORTED_LANGUAGES.keys())
        }