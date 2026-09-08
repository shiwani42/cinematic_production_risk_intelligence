"""
MATRIX — Production Risk Intelligence
Google ADK + Gemini. Four specialist agents, one orchestrator.
"""

import os

from google.adk.agents import LlmAgent

from matrix.tools.fatigue_forecaster import forecast_crew_fatigue
from matrix.tools.hazard_scanner import scan_scene_for_hazards
from matrix.tools.location_enricher import enrich_location_context
from matrix.tools.report_generator import generate_safety_brief
from matrix.tools.script_parser import parse_script_scenes

MODEL = os.environ.get("MATRIX_MODEL", "gemini-2.5-flash-lite")

hazard_agent = LlmAgent(
    name="hazard_scanner",
    model=MODEL,
    description="Scans script scenes for stunts, pyro, water, vehicles, aerial, crowds, weapons.",
    instruction=(
        "You are a film-set safety specialist. "
        "Call parse_script_scenes once, then scan_scene_for_hazards once per scene. "
        "Do not merge scenes. Over-flag rather than miss a hazard. "
        "Return scene number, slug, flags, base score, required roles, sign-off (score ≥ 7)."
    ),
    tools=[parse_script_scenes, scan_scene_for_hazards],
)

fatigue_agent = LlmAgent(
    name="fatigue_forecaster",
    model=MODEL,
    description="Forecasts crew fatigue from call sheet hours, days, commute, and elevation.",
    instruction=(
        "You are an occupational-health specialist for film crews. "
        "Call forecast_crew_fatigue for each crew member. "
        "Times past midnight can be 24+ (2 AM = 26). "
        "Escalate anyone ≥ 80. Flag ≥ 60 plus heavy equipment or heights."
    ),
    tools=[forecast_crew_fatigue],
)

location_agent = LlmAgent(
    name="location_enricher",
    model=MODEL,
    description="Adds weather season, terrain, EMS, and permit context for a filming location.",
    instruction=(
        "You are a location safety researcher. "
        "Call enrich_location_context with the location name and shoot date. "
        "Flag EMS > 30 min, elevation > 1500m, and remote lots. "
        "Always say: scout in person and confirm EMS with local dispatch."
    ),
    tools=[enrich_location_context],
)

synthesizer_agent = LlmAgent(
    name="risk_synthesizer",
    model=MODEL,
    description="Combines hazard, fatigue, and location into a safety brief.",
    instruction=(
        "You are the lead safety coordinator. Call generate_safety_brief with the compiled data. "
        "Structure the result like a production RA: Hazard | Likelihood + Consequence | Controls, "
        "grouped Team / Medical / Environment / Production Activities / Transport / Legal. "
        "Then give a 2–3 sentence producer summary, the top 3 scenes with one mitigation each, "
        "and a traffic light. End with: "
        "This MATRIX risk assessment is AI-assisted. "
        "Qualified safety professionals must validate all decisions before production."
    ),
    tools=[generate_safety_brief],
)

root_agent = LlmAgent(
    name="matrix_orchestrator",
    model=MODEL,
    description=(
        "MATRIX — Production Risk Intelligence. "
        "Orchestrates hazard, fatigue, location, and safety-brief agents."
    ),
    instruction="""
You are MATRIX. Help producers and safety supervisors see risk before cameras roll.

Full assessment:
1. Send script/scenes to hazard_scanner
2. Send call sheet to fatigue_forecaster
3. Send location + date to location_enricher
4. Pass all three results to risk_synthesizer
5. Show the brief

If something is missing, ask for it. If they only have scenes, run a quick hazard scan.
If they have nothing yet, greet them and ask for: script scenes, call sheet, location + date.
""",
    sub_agents=[hazard_agent, fatigue_agent, location_agent, synthesizer_agent],
)
