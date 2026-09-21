# Recording notes — MATRIX hackathon demo

## Path used

**Primary (success):** Live hosted product on Google Cloud Run  
- Dashboard: `https://matrix-632958340118.us-central1.run.app/dashboard/`  
- ADK Dev UI: `https://matrix-632958340118.us-central1.run.app/dev-ui/?app=matrix`  
- Health checked before record: `GET /health` → `{"status":"ok"}`  

**Fallback (not needed):** Local `uvicorn main:app` + sample western — documented in README.

## Tools

| Step | Tool |
|------|------|
| Dashboard capture | `demo/record_walkthrough.py` → `demo/raw/walkthrough.webm` |
| Dev UI capture | `demo/record_devui.py` → `demo/raw/devui.webm` (dismisses **No Thanks** telemetry modal, opens **edit** agent graph) |
| Assembly | `demo/build_final.sh` — 10 s intro, **xfade** dashboard→Dev UI (no hard cut / black flash), 26 s closing cards, caption burn-in |
| Resolution | 1280×720, 30 fps, H.264 |

## Live quirks observed

- **ADK telemetry modal:** First visit shows **Help Improve ADK!** — recording clicks **No Thanks** before showing agent structure.
- **Dev UI graph:** Click the **edit** (pencil) control to open **Agent Structure** with `matrix_orchestrator` and four sub-agents; raw capture trims ~7.8 s lead-in so the crossfade lands on the graph, not an empty Events pane.
- **Transition:** Dashboard and Dev UI are separate Playwright recordings joined with a **0.45 s crossfade** (avoids `page.goto` black frame in a single capture).

## Repro

```bash
pip install playwright && python3 -m playwright install chromium
python3 demo/record_walkthrough.py
python3 demo/record_devui.py
bash demo/build_final.sh
```

## Output

- Raw dashboard: ~**100 s**; Dev UI graph segment: ~**12 s** (after trim)
- Final with 10 s intro + 26 s closing + crossfade: ~**145 s** (`demo/MATRIX_demo_final.mp4`)
