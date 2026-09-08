# IBM Bob Usage Log — MATRIX

**Product:** MATRIX — Production Risk Intelligence
**Hackathon:** Agentic Cinema — IBM Track
**IBM Bob version:** fill after you run Bob (required for IBM-track evidence)

IBM track judging needs evidence that **IBM Bob** was part of development.
This file is the log. Paste Bob screenshots and outputs below.

The app itself is Google ADK + Gemini. Bob is the development partner, not a runtime dependency.

---

## Phase 1 — Architecture (Bob Plan mode)

**Prompt used:**
> Building MATRIX for Agentic Cinema (IBM track) on Google ADK 2.0.
> Four specialist agents: hazard scanner, fatigue forecaster, location enricher, risk synthesizer.
> Generate the project architecture.

**Bob output / screenshot:** _paste here_

---

## Phase 2 — Scaffold (Bob Agent mode)

**Prompt:** Create the ADK package (`matrix/` with `root_agent`) plus FastAPI `main.py`.

**Files Bob created:** _list_

---

## Phase 3 — Tools

| File | Prompt |
|---|---|
| `hazard_scanner.py` | Keyword-to-category map with severity scores |
| `fatigue_forecaster.py` | Hours, consecutive days, circadian, commute, altitude |
| `location_enricher.py` | Lot database + seasonal risk + EMS |
| `report_generator.py` | Combine the three signals; score location × production interaction |

**Suggestions adopted:** _note 2–3_

---

## Phase 4 — Review (Bob `/review`)

**Findings:** _paste_

**Fixed:**
1. Overnight wrap (`wrap < call`) now adds 24 hours
2. Fatigue rest-day bonus no longer dead-codes the ≥7 branch
3. Dashboard `/api/analyze` runs tools directly so the demo does not burn Gemini

---

## Phase 5 — Deploy

**Prompt:** Cloud Run, scale to zero, cheapest instance.

```bash
gcloud run deploy matrix-risk \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --memory 512Mi \
  --cpu 1
```

---

## Productivity

| Task | Without Bob (est.) | With Bob |
|---|---|---|
| Architecture | 2h | 20min |
| Tools | 3h | 45min |
| Review | 1h | 10min |
| Deploy config | 1h | 15min |
