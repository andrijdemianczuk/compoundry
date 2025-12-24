from __future__ import annotations

from app.settings import settings

def ensure_openai_key():
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and set it.")

