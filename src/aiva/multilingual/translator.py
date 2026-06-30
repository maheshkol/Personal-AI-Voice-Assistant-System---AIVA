from aiva.llm.gemini_client import GeminiClient


class Translator:
    """
    AIVA Translation Layer
    Handles multilingual normalization.
    """

    def __init__(self):

        self.llm = GeminiClient()

    def translate_to_english(self, text: str) -> str:
        """
        Translate any language input to English.
        """

        prompt = f"""
        Translate the following text to English.

        Rules:
        - Only return translated text
        - Do not explain
        - Keep meaning accurate
        - Preserve city names and person names

        Text:
        {text}
        """

        try:
            translated = self.llm.chat(prompt)

            return translated.strip()

        except Exception:
            return text

    def translate_from_english(
        self,
        text: str,
        target_language: str
    ) -> str:
        """
        Translate English response back to target language.
        """

        if target_language == "en":
            return text

        language_map = {
            "hi": "Hindi",
            "mr": "Marathi"
        }

        language_name = language_map.get(
            target_language,
            "English"
        )

        prompt = f"""
        Translate the following text to {language_name}.

        Rules:
        - Keep it natural and conversational
        - Keep response short
        - Preserve technical words if needed
        - Only return translated text

        Text:
        {text}
        """

        try:
            translated = self.llm.chat(prompt)

            return translated.strip()

        except Exception:
            return text