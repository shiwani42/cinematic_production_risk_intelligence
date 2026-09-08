from matrix.agent import hazard_agent, root_agent
from matrix.tools.fatigue_forecaster import forecast_crew_fatigue
from matrix.tools.hazard_scanner import scan_scene_for_hazards
from matrix.tools.location_enricher import enrich_location_context
from matrix.tools.report_generator import generate_safety_brief
from matrix.tools.script_parser import parse_script_scenes


def test_root_agent_is_adk_orchestrator():
    assert root_agent.name == "matrix_orchestrator"
    names = [a.name for a in root_agent.sub_agents]
    assert names == [
        "hazard_scanner",
        "fatigue_forecaster",
        "location_enricher",
        "risk_synthesizer",
    ]
    assert "gemini" in (root_agent.model or "").lower()


def test_specialist_tools_are_bound():
    tools = list(hazard_agent.tools or [])
    assert len(tools) >= 2
    blob = " ".join(getattr(t, "__name__", str(t)) for t in tools)
    assert callable(scan_scene_for_hazards)
    assert callable(forecast_crew_fatigue)
    assert callable(enrich_location_context)
    assert callable(generate_safety_brief)
    assert callable(parse_script_scenes)
