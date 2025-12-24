from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def _safe_filename(title: str) -> str:
    # Very conservative slug: keep alnum, dash, underscore; collapse spaces.
    t = title.strip().lower()
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"[^a-z0-9\-_]+", "", t)
    return t[:80] or "note"

def write_note(notes_dir: Path, title: str, content: str) -> Dict[str, Any]:
    notes_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}__{_safe_filename(title)}.md"
    path = notes_dir / fname
    path.write_text(f"# {title}\n\n{content.strip()}\n", encoding="utf-8")
    return {"path": str(path.resolve()), "bytes": path.stat().st_size}
