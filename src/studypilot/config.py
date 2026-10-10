"""
StudyPilot configuration module.

Loads settings from environment variables (.env locally or system environment on Render).
All LLM provider settings are configurable so you can switch between Groq and Gemini
by changing only .env.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file
# ---------------------------------------------------------------------------
load_dotenv()


def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a secret from environment variables."""
    value = os.getenv(key)
    if value:
        return value
    return default


# ---------------------------------------------------------------------------
# API Key
# ---------------------------------------------------------------------------
GROQ_API_KEY: Optional[str] = _get_secret("GROQ_API_KEY")

# ---------------------------------------------------------------------------
# LLM Provider Settings
# ---------------------------------------------------------------------------
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
LLM_BASE_URL: str = os.getenv(
    "LLM_BASE_URL",
    "https://api.groq.com/openai/v1",
)
LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_FALLBACK_MODELS: List[str] = [
    m.strip()
    for m in os.getenv("LLM_FALLBACK_MODELS", "qwen/qwen3.8-27b,openai/gpt-oss-20b").split(",")
    if m.strip()
]
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# ---------------------------------------------------------------------------
# Agent Limits
# ---------------------------------------------------------------------------
MAX_TOOL_CALLS_PER_STEP: int = 6
MAX_TOOL_CALLS_PER_RUN: int = 20
AGENT_TIMEOUT_SECONDS: int = 120
MAX_PLAN_STEPS: int = 6
MIN_PLAN_STEPS: int = 2
SHORT_TERM_MEMORY_MESSAGES: int = 20
MAX_INPUT_LENGTH: int = 2000

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
DB_PATH: Path = PROJECT_ROOT / "studypilot.db"
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "studypilot.log"

# ---------------------------------------------------------------------------
# Demo mode
# ---------------------------------------------------------------------------
DEMO_MODE: bool = os.getenv("STUDYPILOT_DEMO", "false").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure application-wide logging. Never logs secrets."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("studypilot")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler (INFO level)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_fmt = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    console.setFormatter(console_fmt)
    logger.addHandler(console)

    # File handler (DEBUG level)
    try:
        file_handler = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not create log file at %s", LOG_FILE)

    return logger


logger = setup_logging()
