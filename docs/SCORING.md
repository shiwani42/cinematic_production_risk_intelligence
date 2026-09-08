# How MATRIX scores a shoot

Two ideas from `knowledge_dump/` are in the product. Neither is a black-box model.

## Lot × unit (location RA)

The lot already has hazards. The unit brings more. The brief scores the collision and hangs it on the shot list.

1. Known lots (Vasquez, Venice, Death Valley, Brooklyn Bridge, Tahoe) are a baseline: terrain, EMS, permits, season.
2. If `PARALLEL_API_KEY` is set, Parallel Search adds **cited** live notes (fire weather, heat, permits, closures).
3. Live excerpts never replace the baseline. If Parallel is down or unset, analyze still returns the table.
4. Collision rules read both the table and live signals (e.g. pyro × fire-weather).

Treat citations as things a supervisor clicks. Not certified EMS times.

## Fatigue (multi-source, not hours-only)

The Liu paper argues fatigue is multidimensional. MATRIX does not train that neural net — there is no biometric stream on a call sheet. It uses the factor list a 1st AD can audit:

| Term | What it is |
|---|---|
| Hours | Call to wrap, overnight wrap +24 |
| Consecutive days + week load | Accumulation, not one long day |
| Circadian | Early call / overnight |
| Commute | km to set |
| Altitude | Elevation bands |
| Role weight | G&E / stunts heavier than production office |
| Environment × role fusion | Heat/fire + long day, elevation + heavy role, remote + long drive, overnight + physical |

`factor_breakdown` and `fusion_notes` are on every crew row.

## What does not run unless you opt in

- Gemini: dashboard analyze is tools-only. Ask / ADK chat needs a Gemini or Vertex key.
- Parallel: optional. No key → lot table only.
