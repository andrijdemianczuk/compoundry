from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal
from datetime import datetime

Risk = Literal["low", "medium", "high"]
Status = Literal["pending", "approved", "rejected", "executed", "failed"]

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    proposal_id: Optional[str] = None
    proposal_summary: Optional[str] = None

class ApprovalRequest(BaseModel):
    approve: bool = True

class ActionProposal(BaseModel):
    id: str
    tool_name: str
    args: Dict[str, Any]
    summary: str
    risk: Risk = "low"
    status: Status = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProposalView(BaseModel):
    id: str
    tool_name: str
    summary: str
    risk: Risk
    status: Status
    created_at: datetime
