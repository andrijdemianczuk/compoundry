from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.settings import settings
from app.models import ChatRequest, ChatResponse, ApprovalRequest
from app.storage.proposals import ProposalStore
from app.tools.notes import write_note
from app.graph.supervisor import build_graph
from app.graph.state import GraphState

app = FastAPI(title="Personal Assistant v1")

store = ProposalStore(settings.sqlite_path)
graph = build_graph(store)

@app.get("/health")
def health():
    #get the health of the endpoint
    return {"ok": True}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    state = GraphState(user_input=req.message)
    out = graph.invoke(state)
    return ChatResponse(
        response=out.get("response") or "",
        proposal_id=out.get("proposal_id"),
        proposal_summary=("Create a filesystem note" if out.get("proposal_id") else None),
    )

@app.get("/proposals/pending")
def pending():
    return store.list_pending()

@app.post("/proposals/approve/{proposal_id}")
def approve(proposal_id: str, req: ApprovalRequest):
    proposal = store.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.status != "pending":
        return {"id": proposal_id, "status": proposal.status, "detail": "Proposal is not pending"}

    if not req.approve:
        store.set_status(proposal_id, "rejected")
        return {"id": proposal_id, "status": "rejected"}

    # Execute the tool
    if proposal.tool_name != "write_note":
        store.set_status(proposal_id, "failed", {"error": f"Unknown tool: {proposal.tool_name}"})
        raise HTTPException(status_code=400, detail="Unknown tool")

    try:
        result = write_note(settings.notes_dir, proposal.args["title"], proposal.args["content"])
        store.set_status(proposal_id, "executed", result)
        return {"id": proposal_id, "status": "executed", "result": result}
    except Exception as e:
        store.set_status(proposal_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
