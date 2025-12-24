from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class NoteDraft(BaseModel):
    should_create_note: bool = False
    title: Optional[str] = None
    content: Optional[str] = None
    confidence: float = 0.0

class GraphState(BaseModel):
    user_input: str
    draft: NoteDraft = Field(default_factory=NoteDraft)
    proposal_id: Optional[str] = None
    response: Optional[str] = None
