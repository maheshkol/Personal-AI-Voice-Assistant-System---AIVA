import os
import time
import random
import logging
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ── Retry configuration ───────────────────────────────────────────────────────
_RETRYABLE_CODES = {429, 500, 503}
_MAX_ATTEMPTS    = 5
_BASE_DELAY_S    = 2.0
_MAX_DELAY_S     = 32.0


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, (ServerError, APIError)):
        code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        if code in _RETRYABLE_CODES:
            return True
        msg = str(exc).upper()
        if "UNAVAILABLE" in msg or "RESOURCE_EXHAUSTED" in msg:
            return True
    return False


def _call_with_retry(fn, *args, **kwargs):
    """Exponential backoff with full jitter for transient API errors."""
    last_exc = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if not _should_retry(exc):
                raise
            if attempt == _MAX_ATTEMPTS - 1:
                break
            delay = min(_BASE_DELAY_S * (2 ** attempt), _MAX_DELAY_S)
            delay = delay * random.uniform(0.5, 1.5)
            logger.warning(
                "[GeminiClient] Transient error on attempt %d/%d — "
                "retrying in %.1fs. Error: %s",
                attempt + 1, _MAX_ATTEMPTS, delay, exc,
            )
            time.sleep(delay)
    raise last_exc


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_content(role: str, text: str) -> types.Content:
    """
    Build a properly typed Content object.

    FIX: the google-genai SDK validates via pydantic and rejects plain
    {"role": ..., "parts": [...]} dicts — they must be types.Content
    instances with types.Part children.
    """
    return types.Content(
        role=role,
        parts=[types.Part(text=text)],
    )


# ── Client ────────────────────────────────────────────────────────────────────

class GeminiClient:
    """
    Thin wrapper around google-genai for AIVA.

    Fix log vs previous version:
      - History stored as list[types.Content] instead of list[dict].
        Plain dicts raise pydantic ValidationError inside the SDK.
      - _make_content() builds proper typed objects for every history turn.
      - generate() also uses typed Content, not raw dicts.
      - Retry / backoff logic unchanged.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are AIVA, an AI-powered voice assistant created by Mahesh Kolekar.\n"
        "- Reply in short, clear spoken sentences (not bullet points)\n"
        "- Avoid special characters or markdown in responses\n"
        "- Be helpful, friendly and concise\n"
        "- Keep responses under 3 sentences for voice output"
    )

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_output_tokens: int = 512,
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        self.client            = genai.Client(api_key=api_key)
        self.model             = model
        self.temperature       = temperature
        self.max_output_tokens = max_output_tokens
        self.system_prompt     = self.DEFAULT_SYSTEM_PROMPT

        # FIX: list[types.Content], not list[dict]
        self._history: list[types.Content] = []

        logger.info("[GeminiClient] Initialized — model: %s", self.model)

    # ── Public API ────────────────────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """
        Send a message and receive a reply. Maintains conversation history.
        Retries automatically on 503 / 429 / 500 errors.
        """
        self._history.append(_make_content("user", user_message))

        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )

        response = _call_with_retry(
            self.client.models.generate_content,
            model=self.model,
            contents=self._history,      # list[types.Content] — SDK accepts this
            config=config,
        )

        reply = response.text.strip()
        self._history.append(_make_content("model", reply))
        return reply

    def generate(self, prompt: str) -> str:
        """
        Single-turn generation with no conversation history.
        Useful for utility tasks: intent classification, city extraction, etc.
        """
        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )

        response = _call_with_retry(
            self.client.models.generate_content,
            model=self.model,
            contents=[_make_content("user", prompt)],   # FIX: typed, not dict
            config=config,
        )

        return response.text.strip()

    def reset_conversation(self):
        """Clear conversation history (called by the 'reset' command)."""
        self._history.clear()
        logger.info("[GeminiClient] Conversation history cleared.")

    def get_history(self) -> str:
        """Return a human-readable conversation transcript."""
        if not self._history:
            return "No conversation history yet."

        lines = []
        for content in self._history:
            role = "You" if content.role == "user" else "AIVA"
            text = " ".join(p.text for p in content.parts if p.text)
            lines.append(f"{role}: {text}")

        return "\n".join(lines)

    def get_history_raw(self) -> list[types.Content]:
        """Return raw typed history (for LangChain or other integrations)."""
        return list(self._history)