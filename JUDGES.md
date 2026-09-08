# MATRIX — what to show in 3 minutes

Audience: 1st AD / safety supervisor. Not a chatbot. A draft they can take to set.

## The idea (20 seconds)

Most AI film tools storyboard or schedule. Safety still lives in a spreadsheet nobody opens after call.

Secret Compass drafts a generic RA. MATRIX does the thing safety people actually argue about:

1. What hazards does the **lot already have**? (known lots + optional live web, cited)
2. What does the **unit introduce**?
3. How do they **collide**?
4. Hang the answer on the **shot list**, not a tab nobody checks.

Fatigue is not hours alone: circadian, commute, altitude, week load, and lot × role (a 16-hour grip on a fire-prone lot is not a 16-hour coordinator).

## Click path

1. Open `/dashboard`
2. **Play the Vasquez western** (judge demo)
3. Read the three cards: Lot already / Unit introduces / Do not roll
4. Scroll the ADK panel (four specialists, named tools)
5. Open Scene 12 on the shot list — pyro + horse + cliff + helicopter + night + fatigued G&E
6. Print / JSON if you want the artifact
7. Optional: `/` ADK Dev UI — same `root_agent`

## What is Google Cloud vs what is not

| You see | Stack |
|---|---|
| Four-agent trace on the report | `google-adk` tools the Gemini agents also call |
| Live lot sources (when a Parallel key is set) | Parallel Search excerpts + URLs; lot table is the fallback |
| Crew fusion notes | Multi-source fatigue, not a neural net — see `docs/SCORING.md` |
| `/` chat + dashboard Ask | Live ADK `LlmAgent` + Gemini (needs a Gemini or Vertex key) |
| IBM track | IBM Bob as the development partner — see `BOB_USAGE.md` |

Deterministic tools are intentional. Aviation does not let the model invent stall speeds. The model routes and narrates; the tools score.

## If we miss this

Dry-brush pyro under a helicopter, on a remote lot, with a 16-hour key grip. That is not “fire = high.” That is the collision.
