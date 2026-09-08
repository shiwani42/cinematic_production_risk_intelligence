# MATRIX — what to show in 3 minutes

Audience: 1st AD / safety supervisor. Not a chatbot. A draft they can take to set.

## The idea (20 seconds)

Most AI film tools storyboard or schedule. Safety still lives in a spreadsheet nobody opens after call.

Secret Compass drafts a generic RA. MATRIX does the thing safety people actually argue about:

1. What hazards does the **lot already have**?
2. What does the **unit introduce**?
3. How do they **collide**?
4. Hang the answer on the **shot list**, not a tab nobody checks.

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
| `/` chat + Step 4 “Run matrix_orchestrator” | Live ADK `LlmAgent` + Gemini (needs `GOOGLE_API_KEY`) |
| IBM track | IBM Bob as the development partner — see `BOB_USAGE.md` |

Deterministic tools are intentional. Aviation does not let the model invent stall speeds. The model routes and narrates; the tools score.

## If we miss this

Dry-brush pyro under a helicopter, on a remote lot, with a 16-hour key grip. That is not “fire = high.” That is the collision.
