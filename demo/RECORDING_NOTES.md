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
| Browser capture | Python 3 + **Playwright** Chromium (`demo/record_walkthrough.py`) |
| Resolution | 1280×720, 30 fps → `demo/raw/walkthrough.webm` |
| Edit / titles | **ffmpeg** 6.x (`demo/build_final.sh`) — ink/orange title cards, concat, caption burn-in |
| Captions | `demo/captions.srt` (English, bottom-centered) |

## Live quirks observed

- **Cold start:** First dashboard GET ~0.14s during this session (instance already warm). Script uses `networkidle` + 4.5s hero hold to absorb spin-up on cold views.
- **Analyze latency:** `POST /api/analyze` for sample western ~**0.17–0.5s** warm; UI overlay ~2–5s depending on animation and paint.
- **Judge demo button:** Skips wizard; lands directly on **Assessment** (`judgeDemo` in `useAssessment.ts`).
- **Parallel citations:** Not required for demo; lot table baseline always present. Citions block appears only when `PARALLEL_API_KEY` is set on the service.
- **Gemini Ask:** Intel “Ask” panel shows “Add a Gemini key…” when unset — not shown in cut (draft path is tools-only).
- **Print:** Print button shown; `window.print()` not triggered (would open system dialog and break headless capture).

## Repro

```bash
pip install playwright
python3 -m playwright install chromium
python3 demo/record_walkthrough.py
bash demo/build_final.sh
```

## Output

- Raw walkthrough: ~**83.5 s**
- Final with titles + captions: ~**162.5 s** (`demo/MATRIX_demo_final.mp4`, H.264 yuv420p, faststart, no audio track)
