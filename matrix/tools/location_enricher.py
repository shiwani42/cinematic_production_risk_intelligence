"""Location lookup: known lots first, optional Parallel live layer, defaults otherwise."""

from __future__ import annotations

import os

from matrix.tools.parallel_intel import live_location_intel, merge_live_intel

LOCATION_DATABASE = {
    "vasquez rocks": {
        "elevation_m": 852,
        "terrain_hazards": [
            "Unstable sandstone — no climbing without rigging",
            "Diamondback rattlesnakes April–October",
            "Flash flood risk in arroyos after rain",
            "20°C day/night temperature swing",
        ],
        "nearest_trauma": "Henry Mayo Newhall Hospital, Valencia CA",
        "est_response_min": 22,
        "permit_notes": "FilmLA, 72h notice, fire safety officer mandatory",
        "cell_coverage": "partial",
        "type": "remote",
    },
    "venice beach": {
        "elevation_m": 3,
        "terrain_hazards": [
            "High civilian pedestrian traffic",
            "Salt air + sand ingress on equipment",
            "Rip currents near the waterline",
        ],
        "nearest_trauma": "Ronald Reagan UCLA Medical Center",
        "est_response_min": 12,
        "permit_notes": "FilmLA permit; lifeguard coordination for water work",
        "cell_coverage": "full",
        "type": "urban",
    },
    "death valley": {
        "elevation_m": -86,
        "terrain_hazards": [
            "Extreme heat — summer surface temps can exceed 70°C",
            "No cell service — satellite comms required",
            "Medical response severely delayed",
        ],
        "nearest_trauma": "Desert Valley Hospital, Victorville CA",
        "est_response_min": 95,
        "permit_notes": "NPS filming permit + written safety plan + on-set medical officer",
        "cell_coverage": "none",
        "type": "remote",
    },
    "brooklyn bridge": {
        "elevation_m": 40,
        "terrain_hazards": [
            "Active traffic below the deck",
            "High wind; fall protection mandatory",
            "Structural limits on equipment weight",
        ],
        "nearest_trauma": "NewYork-Presbyterian/Weill Cornell",
        "est_response_min": 8,
        "permit_notes": "NYC MOME + NYPD/DOT; structural engineer for heavy gear",
        "cell_coverage": "full",
        "type": "urban",
    },
    "lake tahoe": {
        "elevation_m": 1897,
        "terrain_hazards": [
            "Altitude — acclimatise crew from sea level",
            "Lake water 4–18°C — hypothermia risk",
            "Winter ice/avalanche; summer wildfire",
        ],
        "nearest_trauma": "Barton Memorial Hospital, South Lake Tahoe",
        "est_response_min": 18,
        "permit_notes": "USFS / local municipalities — confirm the exact parcel",
        "cell_coverage": "partial",
        "type": "remote",
    },
}

SEASONAL_RISKS = {
    1: {"summary": "Winter — cold weather protocols", "risks": ["Hypothermia", "Ice/snow", "Short daylight"]},
    2: {"summary": "Late winter — variable cold", "risks": ["Cold protocols", "Unpredictable precipitation"]},
    3: {"summary": "Early spring — unpredictable", "risks": ["Flash rain", "Mud / vehicle access"]},
    4: {"summary": "Spring — generally mild", "risks": ["Pollen", "Occasional heavy rain"]},
    5: {"summary": "Late spring — longer days", "risks": ["CA wildfire season starting", "Heat building"]},
    6: {"summary": "Summer — heat risk", "risks": ["Heat stress", "Wildfire season", "Afternoon storms"]},
    7: {"summary": "Peak summer — high heat", "risks": ["Critical heat", "Red-flag wildfire", "Equipment overheating"]},
    8: {"summary": "Late summer — still hot", "risks": ["Heat stress", "Wildfire", "Southwest monsoon"]},
    9: {"summary": "Early fall — improving", "risks": ["CA fire season tail", "Variable cool"]},
    10: {"summary": "Fall — good shooting weather", "risks": ["Early rain", "Shorter days"]},
    11: {"summary": "Late fall — cold arriving", "risks": ["Cold protocols", "Early dark"]},
    12: {"summary": "Winter — cold weather protocols", "risks": ["Hypothermia", "Short days"]},
}


def _should_call_live() -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return bool(os.environ.get("PARALLEL_API_KEY"))


def enrich_location_context(
    location_name: str,
    shoot_date: str,
    location_type: str = "practical_location",
    live: bool | None = None,
) -> dict:
    key = location_name.lower().strip()
    matched = None
    for name, data in LOCATION_DATABASE.items():
        if name in key:
            matched = data
            break

    try:
        month = int(shoot_date.split("-")[1])
    except (IndexError, ValueError):
        month = 6
    season = SEASONAL_RISKS.get(month, SEASONAL_RISKS[6])

    if matched:
        elevation = matched["elevation_m"]
        terrain = matched["terrain_hazards"]
        trauma = matched["nearest_trauma"]
        response = matched["est_response_min"]
        permits = matched["permit_notes"]
        cell = matched["cell_coverage"]
        loc_type = matched["type"]
        confidence = "database_match"
    else:
        elevation = 100
        terrain = [
            "Location not in MATRIX lots — scout in person",
            "Confirm EMS access routes before the company move",
        ]
        trauma = "Unknown — verify with local dispatch"
        response = 30
        permits = "Confirm filming permit with the local authority"
        cell = "unknown"
        loc_type = location_type if location_type != "practical_location" else "unknown"
        confidence = "default_estimates"

    multiplier = 1.0
    if loc_type == "remote" or response > 30:
        multiplier = 1.3
    if response > 60:
        multiplier = 1.5
    if elevation > 2000:
        multiplier = max(multiplier, 1.2)

    record = {
        "location_name": location_name,
        "shoot_date": shoot_date,
        "location_type": loc_type,
        "elevation_m": elevation,
        "weather": {
            "seasonal_summary": season["summary"],
            "seasonal_risks": list(season["risks"]),
            "recommendation": "Lock a 10-day forecast 48h before the shoot",
        },
        "terrain_hazards": list(terrain),
        "emergency_services": {
            "nearest_trauma_center": trauma,
            "estimated_response_time_minutes": response,
            "response_flag": "CRITICAL: >30 min" if response > 30 else "Within range",
            "cell_coverage": cell,
            "recommendation": (
                "Satellite comms mandatory — no cell"
                if cell == "none"
                else "Confirm EMS time with local dispatch"
            ),
        },
        "regulatory": {"permit_notes": permits},
        "risk_multiplier": multiplier,
        "data_confidence": confidence,
        "citations": [],
        "live_signals": [],
        "live_intel": {"used": False, "source": None},
        "disclaimer": "Scout the lot. Confirm with local authorities. This is a planning start, not a certified assessment.",
    }

    use_live = _should_call_live() if live is None else live
    if use_live:
        fetched = live_location_intel(location_name, shoot_date)
        if fetched.get("ok") and fetched.get("results"):
            record = merge_live_intel(record, fetched["results"])
        else:
            record["live_intel"] = {
                "used": False,
                "source": "parallel",
                "error": fetched.get("error") or "empty",
            }
    return record
