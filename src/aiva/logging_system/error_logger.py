from .logger_config import error_logger
import traceback


class ErrorLogger:

    @staticmethod
    def log_error(module="", error=""):

        error_message = f"""
==================================================
MODULE:
{module}

ERROR:
{str(error)}

TRACEBACK:
{traceback.format_exc()}
==================================================
"""

        error_logger.error(error_message)