from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Optimizer Service (placeholder)")

class Task(BaseModel):
    name: str
    minutes: int
    due: Optional[str] = None

class OptimizeRequest(BaseModel):
    tasks: List[Task]
    focus_minutes: int = 120

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # Placeholder heuristic: sort by minutes descending (replace later with OR-Tools)
    tasks = sorted(req.tasks, key=lambda t: t.minutes, reverse=True)
    plan = []
    remaining = req.focus_minutes
    for t in tasks:
        if remaining <= 0:
            break
        chunk = min(t.minutes, remaining)
        plan.append({"task": t.name, "minutes": chunk})
        remaining -= chunk
    return {"plan": plan, "unused_minutes": remaining}
