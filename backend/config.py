"""
Configuration for OMNIAI.

Reads environment variables (with sensible defaults).
"""
from __future__ import annotations
import os

from dotenv import load_dotenv

# Load .env if present
load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # user can override
AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "1234")
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/memory.db")
SANDBOX_DIR: str = os.getenv("SANDBOX_DIR", "sandbox/apps")
OPENAI_API_URL: str = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
# Timeout for HTTP requests (seconds)
HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "15"))
