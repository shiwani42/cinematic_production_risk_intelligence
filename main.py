"""MATRIX FastAPI app — ADK agent server + a no-LLM analyze route for the dashboard."""

from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

from matrix.agent import MODEL, root_agent
from matrix.pipeline import run_assessment

load_dotenv()

ROOT = Path(__file__).resolve().parent


def _session_db_uri() -> str:
    configured = os.environ.get("SESSION_DB_URI")
    if configured:
        return configured
    # Cloud Run's container FS is read-only except /tmp (app runs as non-root).
    if os.environ.get("K_SERVICE"):
        return "sqlite+aiosqlite:////tmp/sessions.db"
    return "sqlite+aiosqlite:///./sessions.db"


SESSION_SERVICE_URI = _session_db_uri()

app: FastAPI = get_fast_api_app(
    agents_dir=str(ROOT),
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=["*"],
    web=True,
)


class AskBody(BaseModel):
    message: str
    context: dict = Field(default_factory=dict)


class AnalyzeBody(BaseModel):
    production_title: str = "Untitled Production"
    script_text: str = ""
    callsheet: dict = Field(default_factory=dict)
    location_name: str
    shoot_date: str
    producer_name: str = "Production Leadership"
    project_context: dict = Field(default_factory=dict)
    extra_hazards: list = Field(default_factory=list)


def _pdf_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _gemini_ready() -> bool:
    if os.environ.get("GOOGLE_API_KEY"):
        return True
    return os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").upper() in {"1", "TRUE", "YES"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "product": "MATRIX", "agent": "matrix", "version": "1.2.0"}


@app.get("/api/stack")
async def stack_status():
    import google.adk as adk

    return {
        "product": "MATRIX",
        "adk": True,
        "adk_version": getattr(adk, "__version__", "installed"),
        "root_agent": root_agent.name,
        "model": MODEL,
        "sub_agents": [a.name for a in (root_agent.sub_agents or [])],
        "gemini_configured": _gemini_ready(),
        "parallel_configured": bool(os.environ.get("PARALLEL_API_KEY")),
        "apps": ["matrix"],
    }


@app.post("/api/agent/ask")
async def agent_ask(body: AskBody):
    """Live Google ADK + Gemini path. Needs GOOGLE_API_KEY."""
    if not _gemini_ready():
        raise HTTPException(
            status_code=503,
            detail="Add GOOGLE_API_KEY or set GOOGLE_GENAI_USE_VERTEXAI=TRUE so the agents can call Gemini.",
        )

    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from google.genai.errors import ClientError

    prompt = body.message
    if body.context:
        prompt += "\n\nProduction context (JSON):\n" + json.dumps(body.context, default=str)[:12000]

    try:
        runner = InMemoryRunner(agent=root_agent, app_name="matrix")
        session = await runner.session_service.create_session(app_name="matrix", user_id="dashboard")
        texts: list[str] = []
        tools: list[str] = []
        authors: list[str] = []
        async for event in runner.run_async(
            user_id="dashboard",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=prompt)]),
        ):
            if getattr(event, "author", None):
                authors.append(event.author)
            for call in getattr(event, "get_function_calls", lambda: [])() or []:
                tools.append(getattr(call, "name", str(call)))
            content = getattr(event, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    if getattr(part, "text", None):
                        texts.append(part.text)
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "text": "\n".join(texts).strip() or "(agents ran but returned no text)",
        "tools_called": tools,
        "authors": list(dict.fromkeys(authors)),
        "session_id": session.id,
        "stack": "google-adk",
        "model": MODEL,
    }


@app.get("/api/sample")
async def sample_payload():
    script = (ROOT / "sample_data" / "sample_script.txt").read_text(encoding="utf-8")
    callsheet = json.loads((ROOT / "sample_data" / "sample_callsheet.json").read_text(encoding="utf-8"))
    return {
        "script_text": script,
        "callsheet": callsheet,
        "project_context": {
            "production_type": "scripted",
            "who": {
                "crew_size": "42 (unit + stunts + wrangling)",
                "key_roles": "1st AD, Stunt Coordinator (FREC 3), on-set medic, wrangler",
                "specialists": "Pyrotechnician, helicopter unit, armorer, animal wrangler",
                "experience": "Key grip and camera on day 6 without a rest day. Several day-players new to Vasquez.",
            },
            "what": {
                "activities": "Horse chase on a cliff trail, pyro in dry brush, helicopter coverage, river crossing, highway car chase, saloon fight",
                "equipment": "Picture horses, two picture vehicles, aerial unit, pyro charges, blanks / replica firearms",
            },
            "where": {
                "environment": "Remote sandstone canyon. Partial cell. Rattlesnakes April–October. Flash-flood arroyos.",
            },
            "when": {
                "notes": "Night unit on cliff and highway. Company call 04:00. Consecutive day 6–7 for several departments.",
            },
        },
    }


@app.post("/api/analyze")
async def analyze(body: AnalyzeBody):
    return run_assessment(
        script_text=body.script_text,
        callsheet=body.callsheet,
        location_name=body.location_name,
        shoot_date=body.shoot_date,
        production_title=body.production_title,
        producer_name=body.producer_name,
        project_context=body.project_context,
        extra_hazards=body.extra_hazards,
    )


@app.post("/api/analyze/upload")
async def analyze_upload(
    location_name: str = Form(...),
    shoot_date: str = Form(...),
    production_title: str = Form("Untitled Production"),
    script: UploadFile | None = File(None),
    callsheet: UploadFile | None = File(None),
):
    script_text = ""
    if script:
        raw = await script.read()
        name = (script.filename or "").lower()
        script_text = _pdf_text(raw) if name.endswith(".pdf") else raw.decode("utf-8", errors="replace")

    sheet = {}
    if callsheet:
        sheet = json.loads((await callsheet.read()).decode("utf-8"))

    return run_assessment(
        script_text=script_text,
        callsheet=sheet,
        location_name=location_name,
        shoot_date=shoot_date,
        production_title=sheet.get("production", production_title),
    )


_web = ROOT / "frontend" / "dist"
if _web.is_dir():
    app.mount("/dashboard", StaticFiles(directory=str(_web), html=True), name="dashboard")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
