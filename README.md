# MATRIX — Production Risk Intelligence

> The lot already has hazards. Then the unit arrives. MATRIX scores both, then the collision — and hangs it on the shot list.

Google ADK + Gemini · optional Parallel Search · [Agentic Cinema](https://agentic-cinema.devpost.com)

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
  ├── fatigue_forecaster  → hours, days, circadian, commute, altitude, lot×role fusion
  ├── location_enricher   → lot table + optional live web (cited)
  └── risk_synthesizer    → Hazard | Risk | Controls + collisions
```

The dashboard is a full RA product (brief → editable hazards → printable register). Gemini narrates when a key is present. The tools always run — same functions the agents call.

Scoring is documented in [docs/SCORING.md](docs/SCORING.md). Analyze works with **no** Gemini and **no** Parallel key.

## Demo

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
cp .env.example .env   # Gemini optional (Ask / ADK). PARALLEL_API_KEY optional (live lot).
uvicorn main:app --port 8080
```

- Product: http://localhost:8080/dashboard — click **Try the sample western**
- Live: https://matrix-632958340118.us-central1.run.app/dashboard/
- ADK UI: http://localhost:8080 or `/dev-ui/?app=matrix`
- Judge notes: [JUDGES.md](JUDGES.md)
- IBM Bob log: [BOB_USAGE.md](BOB_USAGE.md)

```bash
python -m pytest tests/ -q
```

## Env

| Variable | Required? | What it does |
|---|---|---|
| `GOOGLE_API_KEY` or Vertex (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) | No | Ask + ADK chat |
| `PARALLEL_API_KEY` | No | Live lot intel (fire, weather, permits) with citations |
| `SESSION_DB_URI` | No | ADK sessions. Cloud Run should use `/tmp` |
| `MATRIX_MODEL` | No | Defaults to `gemini-2.5-flash-lite` |

## Deploy (Cloud Run, scale to zero)

```bash
gcloud run deploy matrix --source . --region us-central1 \
  --allow-unauthenticated --min-instances 0 --max-instances 2 \
  --memory 1Gi --cpu 1 \
  --update-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=us-central1,MATRIX_MODEL=gemini-2.5-flash-lite,SESSION_DB_URI=sqlite+aiosqlite:////tmp/sessions.db"
```

Add `PARALLEL_API_KEY` the same way if you want live lot sources. Without it, the lot table still scores.

## License

Apache 2.0
