import os
import sys
import time
from urllib import response
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all AIVA modules
from aiva.llm.gemini_client import GeminiClient
from aiva.asr.whisper_engine import WhisperEngine
from aiva.tts.xtts_engine import TTSEngine
from aiva.wake.wake_word import WakeWordDetector
from aiva.multilingual.lang_detector import LanguageDetector
from aiva.tools.weather import WeatherTool
from aiva.tools.wikipedia_tool import WikipediaTool
from aiva.multilingual.translator import Translator

#LOGGING
from aiva.logging_system.interaction_logger import InteractionLogger
from aiva.logging_system.error_logger import ErrorLogger
from aiva.logging_system.session_manager import SessionManager

#MONGODB
import asyncio

from aiva.database.mongo_client import MongoDBClient
from aiva.database.repositories.message_repository import (
    MessageRepository
)
from aiva.database.repositories.session_repository import (
    SessionRepository
)

MongoDBClient.connect()

class ConversationLoop:
    """
    AIVA Main Conversation Loop.
    Connects all modules into one complete voice assistant.

    Flow:
    Wake Word → ASR → Language Detection → 
    Tool Check → Gemini LLM → TTS → Loop
    """

    # Built-in commands
    COMMANDS = {
        "exit":     "Shutdown AIVA",
        "quit":     "Shutdown AIVA",
        "reset":    "Clear conversation history",
        "status":   "Show system status",
        "history":  "Show conversation history",
        "help":     "Show all commands",
        "language": "Switch language (e.g. language hi)",
    }

    # Tool trigger keywords per language
    WEATHER_KEYWORDS = {
        "en": ["weather", "temperature", "forecast", "rain", "sunny", "humid"],
        "hi": ["मौसम", "तापमान", "बारिश", "धूप", "ठंड", "गर्मी"],
        "mr": ["हवामान", "तापमान", "पाऊस", "ऊन", "थंडी", "उष्णता"]
    }

    WIKIPEDIA_KEYWORDS = {
        "en": ["what is", "who is", "tell me about", "explain", "define", "wikipedia"],
        "hi": ["क्या है", "कौन है", "बताओ", "समझाओ", "परिभाषा", "विकिपीडिया"],
        "mr": ["काय आहे", "कोण आहे", "सांगा", "समजावा", "व्याख्या", "विकिपीडिया"]
    }

    def __init__(self,
                 model_size: str = "small",
                 default_language: str = "en",
                 use_wake_word: bool = True):
        """
        Initialize AIVA Conversation Loop.

        Args:
            model_size:       Whisper model size "base", "small", "medium"
            default_language: Starting language "en", "hi", "mr"
            use_wake_word:    Enable wake word detection
        """
        print("\n" + "="*50)
        print("   🤖 AIVA — AI Voice Assistant")
        print("   Initializing all modules...")
        print("="*50 + "\n")

        self.default_language = default_language
        self.use_wake_word    = use_wake_word
        self.is_running       = False
        self.turn_count       = 0
        self.start_time       = None

        # Session tracking
        self.session_id = SessionManager.generate_session_id()
        print(f"🆔 Session ID: {self.session_id}")

        MongoDBClient.connect()

        asyncio.run(
            SessionRepository.create_session(
                session_id=self.session_id,
                language=default_language
            )
        )

        # Translator
        #print("\n[Translator] Initializing...")
        #self.translator = Translator()

        # Initialize all modules
        print("📦 Loading modules...\n")

        # 1. Language Detector
        print("[1/6] Language Detector...")
        self.lang_detector = LanguageDetector(
            default_language=default_language
        )

        # 2. Translator
        print("\n[2/6] Translator...")
        self.translator = Translator()

        # 3. LLM Client
        print("\n[3/6] Gemini LLM...")
        self.llm = GeminiClient()

        # 3. ASR Engine
        print("\n[3/6] Whisper ASR...")
        self.asr = WhisperEngine(model_size=model_size)

        # 4. TTS Engine
        print("\n[4/6] TTS Engine...")
        self.tts = TTSEngine()

        # 5. Tools
        print("\n[5/6] Tools (Weather + Wikipedia)...")
        self.weather   = WeatherTool()
        self.wikipedia = WikipediaTool()

        # 6. Wake Word Detector
        print("\n[6/6] Wake Word Detector...")
        self.wake_detector = WakeWordDetector(
            mode="energy",
            sensitivity=0.6,
            wake_word="hey aiva",
            language=default_language
        )

        print("\n" + "="*50)
        print("✅ AIVA fully initialized!")
        print("="*50)

    def _speak(self, text: str):
        """Speak text in current language."""
        lang = self.lang_detector.get_current_language()
        self.tts.speak(text, language=lang)

    def _update_llm_language(self):
        """Update Gemini system prompt with current language instruction."""
        instruction = self.lang_detector.get_llm_instruction()
        self.llm.system_prompt = f"""
        You are AIVA, an AI-powered voice assistant created by Mahesh Kolekar.
        - Reply in short, clear spoken sentences (not bullet points)
        - Avoid special characters or markdown in responses
        - Be helpful, friendly and concise
        - Keep responses under 3 sentences for voice output
        - {instruction}
        """

    def _check_weather_intent(self, text: str) -> str:
        """
        Check if user is asking about weather.
        Returns city name if weather intent detected, else None.
        """
        text_lower = text.lower()
        lang    = self.lang_detector.get_current_language()
        # Check keywords in current language AND English
        #keywords = (
            #self.WEATHER_KEYWORDS.get(lang, []) +
            #self.WEATHER_KEYWORDS["en"]
        #)

        #text_lower = text.lower()
        #keywords = self.WEATHER_KEYWORDS.get(lang, self.WEATHER_KEYWORDS["en"])
      
        # Internal processing is now English
        keywords = self.WEATHER_KEYWORDS["en"]

        if any(keyword in text_lower for keyword in keywords):
            # Try to extract city name
            # Common Indian cities
            cities = [
                "nagpur", "mumbai", "pune", "delhi", "bangalore",
                "hyderabad", "chennai", "kolkata", "ahmedabad", "jaipur",
                "surat", "lucknow", "kanpur", "indore", "bhopal",
                "नागपुर", "मुंबई", "पुणे", "दिल्ली", "बैंगलोर"
            ]

            for city in cities:
                if city in text_lower:
                    return city.capitalize()

            # Default to Nagpur if no city found
            return "Nagpur"

        return None

    def _check_wikipedia_intent(self, text: str) -> str:
        """
        Check if user is asking a factual question.
        Returns search query if Wikipedia intent detected, else None.
        """
        text_lower = text.lower()
        lang       = self.lang_detector.get_current_language()
        # Check keywords in current language AND English
        #keywords = (
            #self.WIKIPEDIA_KEYWORDS.get(lang, []) +
            #self.WIKIPEDIA_KEYWORDS["en"]
        #)
        #text_lower = text.lower()
        #keywords = self.WIKIPEDIA_KEYWORDS.get(
            #lang, self.WIKIPEDIA_KEYWORDS["en"]       

        # Internal processing is now English
        keywords = self.WIKIPEDIA_KEYWORDS["en"]

        if any(keyword in text_lower for keyword in keywords):
            # Clean up the query
            query = text
            removals = [
                "what is", "who is", "tell me about",
                "explain", "define", "wikipedia",
                "क्या है", "कौन है", "बताओ", "समझाओ",
                "काय आहे", "कोण आहे", "सांगा"
            ]
            for r in removals:
                query = query.lower().replace(r, "").strip()

            return query if query else text

        return None

    def _handle_command(self, text: str) -> bool:
        """
        Handle built-in commands.

        Returns:
            True if command was handled
            False if not a command
        """
        text_lower = text.lower().strip()

        # Exit command
        if text_lower in ["exit", "quit", "bye", "goodbye"]:
            lang = self.lang_detector.get_current_language()
            messages = {
                "en": "Goodbye! AIVA is shutting down. Have a great day!",
                "hi": "अलविदा! AIVA बंद हो रही है। आपका दिन शुभ हो!",
                "mr": "निरोप! AIVA बंद होत आहे। तुमचा दिवस चांगला जावो!"
            }
            self._speak(messages[lang])
            self.is_running = False
            return True

        # Reset command
        if text_lower == "reset":
            self.llm.reset_conversation()
            self.turn_count = 0
            lang = self.lang_detector.get_current_language()
            messages = {
                "en": "Conversation reset. Starting fresh!",
                "hi": "बातचीत रीसेट हो गई। नए सिरे से शुरू करते हैं!",
                "mr": "संभाषण रीसेट झाले. नव्याने सुरुवात करूया!"
            }
            self._speak(messages[lang])
            return True

        # Status command
        if text_lower == "status":
            elapsed = int(time.time() - self.start_time) if self.start_time else 0
            status  = (
                f"AIVA Status: "
                f"Language: {self.lang_detector.get_language_name()}, "
                f"Turns: {self.turn_count}, "
                f"Uptime: {elapsed} seconds."
            )
            print(f"\n📊 {status}")
            self._speak(status)
            return True

        # History command
        if text_lower == "history":
            history = self.llm.get_history()
            print(f"\n📜 Conversation History:\n{history}")
            self._speak("Showing conversation history on screen.")
            return True

        # Help command
        if text_lower == "help":
            help_text = "Available commands: " + ", ".join(self.COMMANDS.keys())
            print(f"\n💡 {help_text}")
            self._speak(help_text)
            return True

        # Language switch command
        if text_lower.startswith("language"):
            parts = text_lower.split()
            if len(parts) >= 2:
                new_lang = parts[1]
                switched = self.lang_detector.set_language(new_lang)
                if switched:
                    self._update_llm_language()
                    greeting = self.lang_detector.get_greeting()
                    self._speak(greeting)
                else:
                    self._speak("Supported languages are English, Hindi and Marathi.")
            return True

        return False

    def _process_turn(self, user_input: str):
        """
        Process one conversation turn.

        Args:
            user_input: Text from ASR or keyboard
        """

        if not user_input or user_input.strip() == "":
            return

        # Start latency timer
        start_time = time.time()

        # Default tracking values
        intent = "general_chat"
        tool_used = "gemini_llm"
        response = ""
        translated_text = user_input
        language = self.lang_detector.get_current_language()

        # Translate to English for internal processing
        translated_text = self.translator.translate_to_english(user_input)

        print(f"\n👤 You: {user_input}")
        print(f"🌐 Translated: {translated_text}")
        self.turn_count += 1

        try:
            # =========================
            # COMMAND HANDLING
            # =========================
            if self._handle_command(user_input):

                latency = round(time.time() - start_time, 2)

                InteractionLogger.log_interaction(
                    user_input=user_input,
                    language=language,
                    translated_text=translated_text,
                    intent="system_command",
                    tool_used="command_handler",
                    response="Command executed successfully",
                    latency_ms=latency,
                )

                return

        # =========================
        # WEATHER TOOL
        # =========================
        city = self._check_weather_intent(translated_text)

        if city:
            intent = "weather_query"
            tool_used = "weather_api"

            print(f"🌤️  Weather intent detected for: {city}")

            response = self.weather.get_weather_for_aiva(
                city,
                language=language
            )

            response = self.translator.translate_from_english(
                response,
                language
            )

            print(f"\n🤖 AIVA: {response}")
            self._speak(response)

            latency = round(time.time() - start_time, 2)

            InteractionLogger.log_interaction(
                user_input=user_input,
                language=language,
                translated_text=translated_text,
                intent=intent,
                tool_used=tool_used,
                response=response,
                latency_ms=latency,
            )

            asyncio.run(
                MessageRepository.save_message(
                    session_id=self.session_id,
                    turn_index=self.turn_count,
                    user_input=user_input,
                    translated_text=translated_text,
                    response=response,
                    intent=intent,
                    tool_used=tool_used,
                    latency_ms=latency,
                    language=language,
                )
            )

            asyncio.run(
                SessionRepository.increment_turn_count(
                    self.session_id
                )
            )

            return

        # =========================
        # WIKIPEDIA TOOL
        # =========================
        query = self._check_wikipedia_intent(translated_text)

        if query:
            intent = "wikipedia_query"
            tool_used = "wikipedia_api"

            print(f"🔍 Wikipedia intent detected: {query}")

            response = self.wikipedia.search_for_aiva(
                query,
                language=language
            )

            response = self.translator.translate_from_english(
                response,
                language
            )

            print(f"\n🤖 AIVA: {response}")
            self._speak(response)

            latency = round(time.time() - start_time, 2)

            InteractionLogger.log_interaction(
                user_input=user_input,
                language=language,
                translated_text=translated_text,
                intent=intent,
                tool_used=tool_used,
                response=response,
                latency_ms=latency,
            )

            asyncio.run(
                MessageRepository.save_message(
                    session_id=self.session_id,
                    turn_index=self.turn_count,
                    user_input=user_input,
                    translated_text=translated_text,
                    response=response,
                    intent=intent,
                    tool_used=tool_used,
                    latency_ms=latency,
                    language=language,
                )
            )

            asyncio.run(
                SessionRepository.increment_turn_count(
                    self.session_id
                )
            )

            return

        # =========================
        # GEMINI LLM
        # =========================
        print("🧠 Thinking...")

        self._update_llm_language()

        response = self.llm.chat(translated_text)

        response = self.translator.translate_from_english(
            response,
            language
        )

        print(f"\n🤖 AIVA: {response}")

        self._speak(response)

        latency = round(time.time() - start_time, 2)

        InteractionLogger.log_interaction(
            user_input=user_input,
            language=language,
            translated_text=translated_text,
            intent=intent,
            tool_used=tool_used,
            response=response,
            latency_ms=latency,
        )

        asyncio.run(
            MessageRepository.save_message(
                session_id=self.session_id,
                turn_index=self.turn_count,
                user_input=user_input,
                translated_text=translated_text,
                response=response,
                intent=intent,
                tool_used=tool_used,
                latency_ms=latency,
                language=language,
            )
        )

        asyncio.run(
            SessionRepository.increment_turn_count(
                self.session_id
            )
        )

        except Exception as e:

        # Log error
        ErrorLogger.log_error(
            module="ConversationLoop._process_turn",
            error=e
        )

        latency = round(time.time() - start_time, 2)

        # Log failed interaction
        InteractionLogger.log_interaction(
            user_input=user_input,
            language=language,
            translated_text=translated_text,
            intent="failed_request",
            tool_used=tool_used,
            response=f"ERROR: {str(e)}",
            latency_ms=latency,
        )

        error_messages = {
            "en": "Sorry, I had trouble processing that. Please try again.",
            "hi": "क्षमा करें, मुझे समझने में परेशानी हुई। कृपया पुनः प्रयास करें।",
            "mr": "माफ करा, मला समजण्यात अडचण आली. कृपया पुन्हा प्रयत्न करा."
        }

        self._speak(error_messages.get(language, error_messages["en"]))

        print(f"❌ LLM Error: {e}")

    def run_voice_mode(self):
        """
        Run AIVA in full voice mode.
        Uses microphone for input and speakers for output.
        """
        self.is_running = True
        self.start_time = time.time()

        print("\n🎤 AIVA Voice Mode started!")
        print("   Speak to AIVA after wake word")
        print("   Say 'exit' to quit\n")

        # Speak greeting
        greeting = self.lang_detector.get_greeting()
        self._speak(greeting)

        while self.is_running:
            try:
                # Step 1 — Wait for wake word
                if self.use_wake_word:
                    self.wake_detector.wait_for_activation()

                # Step 2 — Listen and transcribe
                print("\n🎤 Listening...")
                result = self.asr.listen_and_transcribe(duration=5)

                user_text = result.get("text", "").strip()
                detected_lang = result.get("language", "en")

                if not user_text:
                    print("⚠️  No speech detected. Try again.")
                    continue

                # Step 3 — Update language
                normalized_lang = self.lang_detector.detect_from_whisper(
                    detected_lang
                )
                self.lang_detector.update_language(normalized_lang)

                # Step 4 — Process the turn
                self._process_turn(user_text)

            except KeyboardInterrupt:
                print("\n\n⌨️  Keyboard interrupt received.")
                self.is_running = False
                break

            except Exception as e:

                ErrorLogger.log_error(
                    module="run_voice_mode",
                    error=e
                )

                print(f"❌ Error in voice loop: {e}")
                continue

        self._shutdown()

    def run_text_mode(self):
        """
        Run AIVA in text mode.
        Type input instead of speaking — great for testing!
        """
        self.is_running = True
        self.start_time = time.time()

        print("\n⌨️  AIVA Text Mode started!")
        print("   Type your message and press Enter")
        print("   Commands: exit, reset, status, history, help")
        print("   Language: language en / language hi / language mr\n")

        # Speak greeting
        greeting = self.lang_detector.get_greeting()
        print(f"🤖 AIVA: {greeting}")
        self._speak(greeting)

        while self.is_running:
            try:
                # Get text input
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Process the turn
                self._process_turn(user_input)

            except KeyboardInterrupt:
                print("\n\n⌨️  Keyboard interrupt received.")
                self.is_running = False
                break

            except Exception as e:
                ErrorLogger.log_error(
                    module="run_text_mode",
                    error=e
                )
                print(f"❌ Error: {e}")
                continue

        self._shutdown()

    def run_hybrid_mode(self):
        """
        Hybrid mode — voice input with text fallback.
        Best for university demo!
        Press Enter to type instead of speaking.
        """
        self.is_running = True
        self.start_time = time.time()

        print("\n🎯 AIVA Hybrid Mode started!")
        print("   Speak OR type your message")
        print("   Press V + Enter for voice input")
        print("   Press T + Enter for text input")
        print("   Type 'exit' to quit\n")

        greeting = self.lang_detector.get_greeting()
        print(f"🤖 AIVA: {greeting}")
        self._speak(greeting)

        while self.is_running:
            try:
                mode = input("\n[V]oice or [T]ext? ").strip().lower()

                if mode == "v":
                    print("🎤 Listening for 5 seconds...")
                    result = self.asr.listen_and_transcribe(duration=5)
                    user_text     = result.get("text", "").strip()
                    detected_lang = result.get("language", "en")

                    if not user_text:
                        print("⚠️  No speech detected.")
                        continue

                    normalized = self.lang_detector.detect_from_whisper(
                        detected_lang
                    )
                    self.lang_detector.update_language(normalized)
                    self._process_turn(user_text)

                elif mode == "t":
                    user_input = input("👤 You: ").strip()
                    if user_input:
                        self._process_turn(user_input)

                elif mode in ["exit", "quit"]:
                    self.is_running = False

            except KeyboardInterrupt:
                print("\n⌨️  Keyboard interrupt.")
                self.is_running = False
            except Exception as e:

                ErrorLogger.log_error(
                    module="run_hybrid_mode",
                    error=e
                )
                print(f"❌ Hybrid Mode Error: {e}")

        self._shutdown()

    def _shutdown(self):
        """Clean shutdown of all modules."""
        print("\n" + "="*50)
        print("🔴 AIVA Shutting down...")
        print(f"   Total turns: {self.turn_count}")
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            print(f"   Session duration: {elapsed} seconds")
        print("="*50)
        self.tts.shutdown()
        self.wake_detector.shutdown()
        print("✅ AIVA shut down cleanly. Goodbye!")