from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from app.models import ActionProposal, ProposalView

SCHEMA = """
CREATE TABLE IF NOT EXISTS proposals (
  id TEXT PRIMARY KEY,
  tool_name TEXT NOT NULL,
  args_json TEXT NOT NULL,
  summary TEXT NOT NULL,
  risk TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  executed_at TEXT,
  result_json TEXT
);
"""

class ProposalStore:
    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.sqlite_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def create(self, tool_name: str, args: Dict[str, Any], summary: str, risk: str = "low") -> ActionProposal:
        proposal_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO proposals (id, tool_name, args_json, summary, risk, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (proposal_id, tool_name, json.dumps(args), summary, risk, "pending", created_at)
            )
            conn.commit()
        return ActionProposal(
            id=proposal_id,
            tool_name=tool_name,
            args=args,
            summary=summary,
            risk=risk,
            status="pending",
            created_at=datetime.fromisoformat(created_at)
        )

    def get(self, proposal_id: str) -> Optional[ActionProposal]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
        if not row:
            return None
        return ActionProposal(
            id=row["id"],
            tool_name=row["tool_name"],
            args=json.loads(row["args_json"]),
            summary=row["summary"],
            risk=row["risk"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def set_status(self, proposal_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        executed_at = datetime.utcnow().isoformat() if status in ("executed", "failed") else None
        result_json = json.dumps(result) if result is not None else None
        with self._connect() as conn:
            conn.execute(
                """UPDATE proposals
                   SET status = ?, executed_at = COALESCE(?, executed_at), result_json = COALESCE(?, result_json)
                   WHERE id = ?""",
                (status, executed_at, result_json, proposal_id)
            )
            conn.commit()

    def list_pending(self) -> List[ProposalView]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, tool_name, summary, risk, status, created_at FROM proposals WHERE status = 'pending' ORDER BY created_at DESC"
            ).fetchall()
        return [
            ProposalView(
                id=r["id"],
                tool_name=r["tool_name"],
                summary=r["summary"],
                risk=r["risk"],
                status=r["status"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]
