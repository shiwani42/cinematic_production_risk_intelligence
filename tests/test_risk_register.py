from matrix.tools.risk_register import build_risk_register, group_register


def test_register_covers_pyro_and_fatigue():
    scenes = [
        {
            "scene_number": 12,
            "hazard_flags": ["pyrotechnics", "aerial_work"],
            "adjusted_risk_score": 9.2,
            "interaction_notes": ["Pyro on fire-prone / hot terrain"],
        }
    ]
    crew = [{"crew_role": "Key Grip", "fatigue_score": 82, "top_contributing_factors": ["hours_on_set"]}]
    location = {
        "location_type": "remote",
        "elevation_m": 852,
        "terrain_hazards": ["Unstable sandstone"],
        "emergency_services": {
            "estimated_response_time_minutes": 22,
            "nearest_trauma_center": "Henry Mayo",
            "response_flag": "Within range",
            "recommendation": "Confirm EMS",
        },
        "regulatory": {"permit_notes": "FilmLA 72h"},
    }
    rows = build_risk_register(scenes, crew, location)
    flags = {r["source_flag"] for r in rows}
    assert "pyrotechnics" in flags
    assert "aerial_work" in flags
    assert "fatigue" in flags
    assert "terrain" in flags
    pyro = next(r for r in rows if r["source_flag"] == "pyrotechnics")
    assert pyro["controls"]
    assert 12 in pyro["scene_refs"]
    sections = group_register(rows)
    assert any(s["category"] == "Production Activities" for s in sections)
    assert any(s["category"] == "Team" for s in sections)
