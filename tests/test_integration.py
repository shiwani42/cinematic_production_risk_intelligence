import json
from pathlib import Path

from matrix.pipeline import run_assessment
from matrix.tools.location_enricher import enrich_location_context


ROOT = Path(__file__).resolve().parents[1]


def test_vasquez_is_a_known_remote_lot():
    loc = enrich_location_context("Vasquez Rocks, Agua Dulce, CA", "2026-09-20")
    assert loc["data_confidence"] == "database_match"
    assert loc["location_type"] == "remote"
    assert loc["risk_multiplier"] >= 1.3


def test_sample_western_end_to_end():
    script = (ROOT / "sample_data" / "sample_script.txt").read_text(encoding="utf-8")
    callsheet = json.loads((ROOT / "sample_data" / "sample_callsheet.json").read_text(encoding="utf-8"))
    brief = run_assessment(
        script_text=script,
        callsheet=callsheet,
        location_name=callsheet["location"],
        shoot_date=callsheet["shoot_date"],
        production_title=callsheet["production"],
    )
    assert brief["parsed_scene_count"] == 4
    assert brief["executive_summary"]["critical_scenes"] >= 1
    assert brief["executive_summary"]["crew_at_risk"] >= 1
    assert brief["top_critical_scenes"][0]["adjusted_risk_score"] >= 7
    assert any(s.get("interaction_notes") for s in brief["scenes"])
    assert len(brief["risk_register"]) >= 6
    cats = {r["category"] for r in brief["risk_register"]}
    assert "Production Activities" in cats
    assert "Team" in cats
    assert brief["risk_register_sections"]
    assert brief["thesis"]["do_not_roll"]
    assert brief["thesis"]["location_brings"]
    assert brief["thesis"]["collisions"]
    assert len(brief["agent_trace"]) == 4
    assert brief["agent_trace"][0]["agent"] == "hazard_scanner"
    crew = brief["crew_fatigue_summary"]["all"]
    assert crew[0]["factor_breakdown"]["environment_role_fusion"] >= 0
    assert "citations" in brief["location_intelligence"]
    assert brief["location_intelligence"]["live_intel"]["used"] is False
