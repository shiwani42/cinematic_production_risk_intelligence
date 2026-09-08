from matrix.tools.fatigue_forecaster import forecast_crew_fatigue


def test_long_day_plus_early_call_is_high():
    result = forecast_crew_fatigue(
        crew_role="Key Grip",
        department="G&E",
        call_time_24h=4.0,
        wrap_time_24h=20.5,
        consecutive_shoot_days=6,
        travel_to_set_km=130,
        physically_demanding_role=True,
        days_since_last_rest_day=5,
    )
    assert result["hours_on_set"] == 16.5
    assert result["fatigue_score"] >= 60
    assert result["requires_supervisor_notification"]


def test_overnight_wrap_adds_24():
    result = forecast_crew_fatigue(
        "Camera Operator",
        "Camera",
        call_time_24h=22.0,
        wrap_time_24h=6.0,
        consecutive_shoot_days=1,
        travel_to_set_km=10,
        is_overnight_shoot=True,
    )
    assert result["hours_on_set"] == 8.0


def test_easy_day_is_low():
    result = forecast_crew_fatigue(
        "PA", "Production", 9.0, 17.0, 1, 5.0
    )
    assert result["risk_level"] in {"minimal", "low"}
    assert result["fatigue_score"] < 40


def test_heavy_role_on_hot_lot_scores_higher_than_office():
    lot = {
        "location_type": "remote",
        "weather": {"seasonal_risks": ["Heat stress", "Wildfire season"]},
        "terrain_hazards": [],
        "live_signals": ["wildfire / fire-weather"],
    }
    grip = forecast_crew_fatigue(
        "Key Grip",
        "G&E",
        6.0,
        20.0,
        4,
        80,
        location_elevation_m=1900,
        physically_demanding_role=True,
        location_context=lot,
    )
    office = forecast_crew_fatigue(
        "Production Coordinator",
        "Production Office",
        6.0,
        20.0,
        4,
        80,
        location_elevation_m=1900,
        physically_demanding_role=False,
        location_context=lot,
    )
    assert grip["fatigue_score"] > office["fatigue_score"]
    assert grip["factor_breakdown"]["environment_role_fusion"] > 0
    assert grip["fusion_notes"]
