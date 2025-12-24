from __future__ import annotations

from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.settings import settings
from app.llm.client import ensure_openai_key
from app.graph.state import GraphState, NoteDraft
from app.storage.proposals import ProposalStore

SYSTEM = """You are a personal assistant.
Your current capability is ONLY to propose creating filesystem notes.

Rules:
- If the user asks to create/save/remember/write a note, set should_create_note=true and extract a clear title + content.
- If the user is not asking for a note, set should_create_note=false.
- Be conservative: if unsure, set should_create_note=false.
"""

def build_graph(store: ProposalStore):
    ensure_openai_key()
    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.2,
    )

    # Structured output model
    llm_structured = llm.with_structured_output(NoteDraft)

    def draft_note(state: GraphState) -> Dict[str, Any]:
        draft: NoteDraft = llm_structured.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=state.user_input)
        ])
        return {"draft": draft}

    def maybe_create_proposal(state: GraphState) -> Dict[str, Any]:
        if not state.draft.should_create_note or not state.draft.title or not state.draft.content:
            return {"response": "Got it. For now I can only create filesystem notes (with approval). If you'd like, tell me what note to create (title + what to include)."}
        summary = f"Create a note titled '{state.draft.title}'"
        proposal = store.create(
            tool_name="write_note",
            args={"title": state.draft.title, "content": state.draft.content},
            summary=summary,
            risk="low"
        )
        resp = (
            f"I drafted a note and created a proposal: **{proposal.summary}**.\n\n"
            f"To approve and execute it, POST to `/proposals/approve/{proposal.id}` with `{{"approve": true}}`. "
            f"To reject: `{{"approve": false}}`."
        )
        return {"proposal_id": proposal.id, "response": resp}

    graph = StateGraph(GraphState)
    graph.add_node("draft_note", draft_note)
    graph.add_node("maybe_create_proposal", maybe_create_proposal)

    graph.set_entry_point("draft_note")
    graph.add_edge("draft_note", "maybe_create_proposal")
    graph.add_edge("maybe_create_proposal", END)

    return graph.compile()
