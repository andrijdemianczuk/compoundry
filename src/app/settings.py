from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    notes_dir: Path = Path(os.getenv("NOTES_DIR", "./notes"))
    sqlite_path: Path = Path(os.getenv("SQLITE_PATH", "./data/assistant.sqlite3"))

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8080"))

settings = Settings()
