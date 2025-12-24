# Personal Assistant v1 (LangGraph + FastAPI + Approval-Gated Notes)

This is a minimal but *production-shaped* scaffold:
- **OpenAI** for inference
- **LangGraph/LangChain** for orchestration
- **FastAPI** for a simple "chat" endpoint
- An **approval endpoint** that gates any *action* (writing a filesystem note)

## What this v1 can do
- Turn a natural-language request into a **proposed action**
- You approve (or reject) the action via HTTP
- If approved, it writes a note to `NOTES_DIR`

## Quick start (Mac dev)
1. Install Poetry, then:
   ```bash
   poetry install
   cp .env.example .env
   # edit .env and set OPENAI_API_KEY
   ```

2. Run the API:
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

3. Create a proposal:
   ```bash
   curl -s -X POST http://localhost:8080/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"Make a note titled \"Octatrack ideas\" with bullet points about transitions and placeholders."}' | jq
   ```

4. See pending proposals:
   ```bash
   curl -s http://localhost:8080/proposals/pending | jq
   ```

5. Approve one (replace ID):
   ```bash
   curl -s -X POST http://localhost:8080/proposals/approve/<PROPOSAL_ID> \
     -H "Content-Type: application/json" \
     -d '{"approve": true}' | jq
   ```

## Deploy to Jetson (simple)
Option A: run with Python + Poetry on the Jetson (fastest to iterate).
Option B: use Docker Compose (recommended for always-on).

A starter compose file is in `docker/docker-compose.jetson.yml`.

## Extend later
This scaffold is designed to add more tools with the same pattern:
- Gmail send
- Google Calendar create/update
- Evernote create note

Each should be modeled as:
1) propose (LLM creates ActionProposal)
2) approve
3) execute + audit log

