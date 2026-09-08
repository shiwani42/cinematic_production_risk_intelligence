"""Crew fatigue: hours, days, circadian, commute, altitude, then environment × role fusion.

The Liu paper's useful idea is multi-source load, not a neural net. We keep every
term visible so a supervisor can audit the score.
"""

from __future__ import annotations

HEAVY_MARKERS = (
    "g&e",
    "grip",
    "electric",
    "lighting",
    "stunt",
    "camera",
    "construction",
    "locations",
    "special effects",
    "sfx",
    "key grip",
    "best boy",
)
LIGHT_MARKERS = ("script", "office", "accounting", "casting")


def _role_weight(crew_role: str, department: str, physically_demanding_role: bool) -> tuple[float, str]:
    blob = f"{crew_role} {department}".lower()
    if physically_demanding_role or any(m in blob for m in HEAVY_MARKERS):
        return 1.12, "heavy_set_role"
    if any(m in blob for m in LIGHT_MARKERS):
        return 0.92, "low_exertion_role"
    return 1.0, "standard_role"


def _env_text(location_context: dict | None) -> str:
    if not location_context:
        return ""
    weather = location_context.get("weather") or {}
    parts = [
        " ".join(location_context.get("terrain_hazards") or []),
        " ".join(weather.get("seasonal_risks") or []),
        weather.get("seasonal_summary") or "",
        weather.get("live_summary") or "",
        " ".join(location_context.get("live_signals") or []),
        location_context.get("location_type") or "",
    ]
    return " ".join(parts).lower()


def _environment_fusion(
    hours_worked: float,
    circadian_score: float,
    commute_score: float,
    altitude_m: float,
    physically: bool,
    location_context: dict | None,
) -> tuple[float, list[str]]:
    """Paper §3: environment and job load change fatigue. Transparent bumps only."""
    text = _env_text(location_context)
    loc_type = (location_context or {}).get("location_type", "")
    bump = 0.0
    notes: list[str] = []
    if hours_worked > 10 and any(k in text for k in ("heat", "wildfire", "fire")):
        bump += 8
        notes.append("Long day on heat / fire-prone lot")
    if altitude_m > 1800 and physically:
        bump += 6
        notes.append("Heavy role at elevation")
    if circadian_score >= 14 and physically:
        bump += 6
        notes.append("Circadian load on a physical role")
    if loc_type == "remote" and commute_score >= 10:
        bump += 4
        notes.append("Remote lot plus long drive")
    return min(bump, 18), notes


def forecast_crew_fatigue(
    crew_role: str,
    department: str,
    call_time_24h: float,
    wrap_time_24h: float,
    consecutive_shoot_days: int,
    travel_to_set_km: float,
    location_elevation_m: float = 0.0,
    is_overnight_shoot: bool = False,
    days_since_last_rest_day: int = 0,
    physically_demanding_role: bool = False,
    location_context: dict | None = None,
) -> dict:
    hours_worked = wrap_time_24h - call_time_24h
    if hours_worked <= 0:
        hours_worked += 24

    if hours_worked <= 8:
        hours_score = 5
    elif hours_worked <= 10:
        hours_score = 18
    elif hours_worked <= 12:
        hours_score = 28
    elif hours_worked <= 14:
        hours_score = 42
    elif hours_worked <= 16:
        hours_score = 58
    else:
        hours_score = 72

    if physically_demanding_role and hours_worked > 10:
        hours_score = min(hours_score + 8, 72)

    consec_score = min((consecutive_shoot_days - 1) * 6, 24)
    if days_since_last_rest_day >= 7:
        consec_score = min(consec_score + 20, 35)
    elif days_since_last_rest_day >= 5:
        consec_score = min(consec_score + 12, 30)

    week_load = min(round(consecutive_shoot_days * (hours_worked / 12.0) * 3, 1), 12)

    if is_overnight_shoot or call_time_24h >= 23.0 or call_time_24h < 4.5:
        circadian_score = 22
    elif call_time_24h < 5.5 or call_time_24h >= 21.0:
        circadian_score = 14
    elif call_time_24h < 7.0 or call_time_24h >= 19.5:
        circadian_score = 7
    else:
        circadian_score = 0

    commute_score = min(round((travel_to_set_km / 50.0) * 5, 1), 15)

    if location_elevation_m > 3500:
        altitude_score = 18
    elif location_elevation_m > 2500:
        altitude_score = 12
    elif location_elevation_m > 1800:
        altitude_score = 7
    elif location_elevation_m > 1200:
        altitude_score = 3
    else:
        altitude_score = 0

    role_weight, role_label = _role_weight(crew_role, department, physically_demanding_role)
    hours_adj = round(hours_score * role_weight, 1)
    altitude_adj = round(altitude_score * (1.15 if role_weight > 1 else 1.0), 1)

    fusion_score, fusion_notes = _environment_fusion(
        hours_worked,
        circadian_score,
        commute_score,
        location_elevation_m,
        physically_demanding_role or role_weight > 1,
        location_context,
    )

    fatigue_score = min(
        round(
            hours_adj
            + consec_score
            + week_load
            + circadian_score
            + commute_score
            + altitude_adj
            + fusion_score,
            1,
        ),
        100,
    )

    if fatigue_score >= 80:
        risk_level = "critical"
    elif fatigue_score >= 60:
        risk_level = "high"
    elif fatigue_score >= 40:
        risk_level = "moderate"
    elif fatigue_score >= 20:
        risk_level = "low"
    else:
        risk_level = "minimal"

    if fatigue_score >= 75:
        turnaround_hours = 12
    elif fatigue_score >= 55:
        turnaround_hours = 10
    else:
        turnaround_hours = 8

    recs: list[str] = []
    if fatigue_score >= 80:
        recs.append(f"MANDATORY: {turnaround_hours}h turnaround before next call")
        recs.append("Notify production insurance; consider a day-player for heavy scenes")
    if fatigue_score >= 60:
        recs.append("Safety buddy — no solo heavy equipment")
        recs.append("15-min break every 2 hours")
    if consecutive_shoot_days >= 6 or days_since_last_rest_day >= 5:
        recs.append("Schedule a rest day within 48 hours")
    if circadian_score >= 14:
        recs.append("Hot meals + hydration on the overnight; invite fatigue self-report")
    if commute_score >= 10:
        recs.append(f"Hotel or production transport — {travel_to_set_km:.0f} km to set")
    if altitude_adj >= 7:
        recs.append(f"48h acclimatisation at {location_elevation_m:.0f}m before high-exertion work")
    recs.extend(fusion_notes)

    factors = {
        "hours_on_set": hours_adj,
        "consecutive_days": consec_score,
        "week_load": week_load,
        "circadian_disruption": circadian_score,
        "commute": commute_score,
        "altitude": altitude_adj,
        "environment_role_fusion": fusion_score,
    }

    return {
        "crew_role": crew_role,
        "department": department,
        "hours_on_set": round(hours_worked, 1),
        "fatigue_score": fatigue_score,
        "risk_level": risk_level,
        "top_contributing_factors": [k for k, v in sorted(factors.items(), key=lambda x: -x[1])[:2] if v > 0],
        "factor_breakdown": factors,
        "role_load": role_label,
        "fusion_notes": fusion_notes,
        "recommendations": recs,
        "turnaround_hours_required": turnaround_hours,
        "requires_supervisor_notification": fatigue_score >= 60,
        "critical_combination_flag": fatigue_score >= 60 and physically_demanding_role,
    }
