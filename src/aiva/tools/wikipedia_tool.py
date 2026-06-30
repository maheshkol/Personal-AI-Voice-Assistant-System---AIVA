import wikipedia


class WikipediaTool:
    """
    Wikipedia Search Tool for AIVA.
    Fetches factual knowledge from Wikipedia.
    Supports English, Hindi and Marathi Wikipedia.
    Free — no API key needed!
    """

    # Wikipedia language codes
    WIKI_LANGUAGES = {
        "en": "en",   # English Wikipedia
        "hi": "hi",   # Hindi Wikipedia
        "mr": "mr"    # Marathi Wikipedia
    }

    def __init__(self, default_language: str = "en"):
        """
        Initialize Wikipedia Tool.

        Args:
            default_language: Default Wikipedia language
        """
        self.current_language = default_language
        self.max_summary_chars = 500  # Max chars to return
        self.max_sentences = 3        # Max sentences in summary

        # Set Wikipedia language
        wikipedia.set_lang(
            self.WIKI_LANGUAGES.get(default_language, "en")
        )

        print(f"✅ Wikipedia Tool initialized!")
        print(f"   Language: {default_language} Wikipedia")

    def search(self, query: str, language: str = None) -> dict:
        """
        Search Wikipedia and return a summary.

        Args:
            query:    Search query string
            language: Override language for this search

        Returns:
            dict with title, summary, url
            or error dict if not found
        """
        # Set language if specified
        if language and language in self.WIKI_LANGUAGES:
            wikipedia.set_lang(self.WIKI_LANGUAGES[language])
            self.current_language = language

        print(f"🔍 Searching Wikipedia: '{query}'")

        try:
            # Search for the query
            search_results = wikipedia.search(query, results=7)

            if not search_results:
                return self._not_found_response(query)

            # Try to get the best matching page
            for result in search_results:
                try:
                    # Get page summary
                    summary = wikipedia.summary(
                        result,
                        sentences=self.max_sentences,
                        auto_suggest=True,
                        redirect=True
                    )

                    page = wikipedia.page(result, auto_suggest=True)

                    print(f"✅ Found: '{page.title}'")

                    return {
                        "found":   True,
                        "title":   page.title,
                        "summary": summary[:self.max_summary_chars],
                        "url":     page.url,
                        "query":   query
                    }

                except wikipedia.DisambiguationError as e:
                    # Multiple matches — try first option
                    try:
                        summary = wikipedia.summary(
                            e.options[0],
                            sentences=self.max_sentences
                        )
                        print(f"✅ Disambiguation resolved: '{e.options[0]}'")
                        return {
                            "found":   True,
                            "title":   e.options[0],
                            "summary": summary[:self.max_summary_chars],
                            "url":     "",
                            "query":   query
                        }
                    except:
                        continue

                except wikipedia.PageError:
                    continue

            return self._not_found_response(query)

        except Exception as e:
            print(f"❌ Wikipedia error: {e}")
            return {
                "found":   False,
                "error":   str(e),
                "query":   query,
                "summary": ""
            }

    def _not_found_response(self, query: str) -> dict:
        """Return a standard not-found response."""
        print(f"⚠️  No Wikipedia result for: '{query}'")
        return {
            "found":   False,
            "query":   query,
            "summary": "",
            "error":   "No results found"
        }

    def format_for_voice(self, result: dict, language: str = "en") -> str:
        """
        Format Wikipedia result into natural spoken sentence.

        Args:
            result:   Result dict from search()
            language: "en", "hi", "mr"

        Returns:
            Voice-ready string for TTS
        """
        if not result.get("found"):
            messages = {
                "en": f"Sorry, I could not find information about {result.get('query', 'that topic')} on Wikipedia.",
                "hi": f"क्षमा करें, मुझे {result.get('query', 'उस विषय')} के बारे में Wikipedia पर जानकारी नहीं मिली।",
                "mr": f"माफ करा, मला {result.get('query', 'त्या विषयाबद्दल')} Wikipedia वर माहिती मिळाली नाही।"
            }
            return messages.get(language, messages["en"])

        title   = result["title"]
        summary = result["summary"]

        if language == "hi":
            return f"Wikipedia के अनुसार, {title} के बारे में: {summary}"
        elif language == "mr":
            return f"Wikipedia नुसार, {title} बद्दल: {summary}"
        else:
            return f"According to Wikipedia, about {title}: {summary}"

    def search_for_aiva(self, query: str, language: str = "en") -> str:
        """
        Main method called by AIVA conversation loop.
        Returns a ready-to-speak Wikipedia summary.

        Args:
            query:    Search query
            language: Current language code

        Returns:
            Voice-ready string
        """
        result = self.search(query, language=language)
        return self.format_for_voice(result, language)

    def set_language(self, language: str):
        """Change Wikipedia language."""
        if language in self.WIKI_LANGUAGES:
            self.current_language = language
            wikipedia.set_lang(self.WIKI_LANGUAGES[language])
            print(f"✅ Wikipedia language set to: {language}")