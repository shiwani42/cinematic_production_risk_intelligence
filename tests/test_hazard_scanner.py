from matrix.tools.hazard_scanner import scan_scene_for_hazards
from matrix.tools.script_parser import parse_script_scenes


def test_pyro_and_stunt_flags():
    result = scan_scene_for_hazards(
        12,
        "Jack dives from the horse. A pyrotechnic charge detonates. Helicopter unit above the cliff.",
        time_of_day="NIGHT",
        slug_line="EXT. CANYON RIDGE — NIGHT",
    )
    assert "pyrotechnics" in result["hazard_flags"]
    assert "aerial_work" in result["hazard_flags"]
    assert result["base_risk_score"] >= 6
    assert result["requires_supervisor_signoff"]


def test_quiet_scene_is_low():
    result = scan_scene_for_hazards(1, "Two people talk at a kitchen table.", int_ext="INT")
    assert result["hazard_count"] == 0
    assert result["risk_level"] == "low"


def test_parser_splits_numbered_scenes():
    scenes = parse_script_scenes(
        "SCENE 12 — EXT. CANYON RIDGE — NIGHT\nBoom.\n\nSCENE 13 — EXT. RIVER CROSSING — DAY\nWater.\n"
    )
    assert [s["scene_number"] for s in scenes] == [12, 13]
    assert scenes[0]["time_of_day"] == "NIGHT"
    assert "Boom" in scenes[0]["description"]
