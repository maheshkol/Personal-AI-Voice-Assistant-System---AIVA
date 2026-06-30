from .logger_config import interaction_logger


class InteractionLogger:

    @staticmethod
    def log_interaction(
        user_input="",
        language="",
        translated_text="",
        intent="",
        tool_used="",
        response="",
        latency="",
    ):

        log_message = f"""
==================================================
USER INPUT:
{user_input}

LANGUAGE:
{language}

TRANSLATED TEXT:
{translated_text}

INTENT:
{intent}

TOOL USED:
{tool_used}

FINAL RESPONSE:
{response}

LATENCY:
{latency}
==================================================
"""

        interaction_logger.info(log_message)