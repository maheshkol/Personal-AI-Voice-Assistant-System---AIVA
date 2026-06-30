import logging
from pathlib import Path
from datetime import datetime

# Create logs directory
#BASE_LOG_DIR = Path("logs")
BASE_LOG_DIR = Path(__file__).resolve().parents[4] / "logs"
print(f"📁 Logs directory: {BASE_LOG_DIR.resolve()}")

INTERACTION_DIR = BASE_LOG_DIR / "interactions"
ERROR_DIR = BASE_LOG_DIR / "errors"
SESSION_DIR = BASE_LOG_DIR / "sessions"

INTERACTION_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Log filenames
date_str = datetime.now().strftime("%Y-%m-%d")

interaction_log_file = INTERACTION_DIR / f"{date_str}.log"
error_log_file = ERROR_DIR / f"{date_str}.log"

# Interaction Logger
interaction_logger = logging.getLogger("interaction_logger")
interaction_logger.setLevel(logging.INFO)

interaction_handler = logging.FileHandler(interaction_log_file, encoding="utf-8")

interaction_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

interaction_handler.setFormatter(interaction_formatter)

interaction_logger.addHandler(interaction_handler)

# Error Logger
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)

error_handler = logging.FileHandler(error_log_file, encoding="utf-8")

error_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

error_handler.setFormatter(error_formatter)

error_logger.addHandler(error_handler)