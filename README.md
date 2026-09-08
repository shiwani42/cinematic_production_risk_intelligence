# MATRIX — Production Risk Intelligence

> The lot already has hazards. Then the unit arrives. MATRIX scores both, then the collision — and hangs it on the shot list.

Google ADK + Gemini · IBM Bob track · [Agentic Cinema](https://agentic-cinema.devpost.com)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## Who it is for

1st ADs, line producers, and safety supervisors who need a **shoot-specific first draft** before cameras — not a template, not a chatbot essay.

## What it does

Four ADK specialists share one orchestrator:

```
script + call sheet + location
        ↓
matrix_orchestrator
  ├── hazard_scanner      → scene flags on the slug line
  ├── fatigue_forecaster  → hours, days, circadian, commute, altitude
  ├── location_enricher   → terrain, EMS, permits, season
  └── risk_synthesizer    → Hazard | Risk | Controls + collisions
```

The dashboard is a full RA product (brief → editable hazards → printable register). Gemini narrates when a key is present. The tools always run — same functions the agents call.

## Demo

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
cp .env.example .env   # add GOOGLE_API_KEY to talk to the agents
uvicorn main:app --port 8080
```

- Product: http://localhost:8080/dashboard — click **Play the Vasquez western**
- ADK UI: http://localhost:8080
- Judge notes: [JUDGES.md](JUDGES.md)
- IBM Bob log: [BOB_USAGE.md](BOB_USAGE.md)

```bash
python -m pytest tests/ -q
```

## Deploy (Cloud Run, scale to zero)

```bash
gcloud run deploy matrix-risk --source . --region us-central1 \
  --allow-unauthenticated --min-instances 0 --max-instances 2 \
  --memory 512Mi --cpu 1 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=FALSE,MATRIX_MODEL=gemini-3.5-flash-lite" \
  --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

## License

Apache 2.0
