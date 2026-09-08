"""Keyword scan → scene hazard flags. Deterministic so the dashboard stays free."""

from __future__ import annotations

import re

HAZARD_MAP = {
    "stunt": "stunt_work",
    "fight": "stunt_work",
    "brawl": "stunt_work",
    "fall": "stunt_work",
    "falls": "stunt_work",
    "jump": "stunt_work",
    "leap": "stunt_work",
    "tackle": "stunt_work",
    "thrown": "stunt_work",
    "dives": "stunt_work",
    "dive": "stunt_work",
    "explosion": "pyrotechnics",
    "explodes": "pyrotechnics",
    "fire": "pyrotechnics",
    "flame": "pyrotechnics",
    "flames": "pyrotechnics",
    "pyro": "pyrotechnics",
    "pyrotechnic": "pyrotechnics",
    "detonates": "pyrotechnics",
    "ignites": "pyrotechnics",
    "smoke": "pyrotechnics",
    "burning": "pyrotechnics",
    "car chase": "vehicle_operation",
    "vehicle": "vehicle_operation",
    "driving": "vehicle_operation",
    "motorcycle": "vehicle_operation",
    "truck": "vehicle_operation",
    "crash": "vehicle_operation",
    "crashes": "vehicle_operation",
    "collision": "vehicle_operation",
    "gallops": "vehicle_operation",
    "horseback": "vehicle_operation",
    "rams": "vehicle_operation",
    "water": "water_work",
    "underwater": "water_work",
    "river": "water_work",
    "ocean": "water_work",
    "lake": "water_work",
    "swimming": "water_work",
    "drowning": "water_work",
    "flood": "water_work",
    "rooftop": "elevated_work",
    "roof": "elevated_work",
    "cliff": "elevated_work",
    "ledge": "elevated_work",
    "scaffold": "elevated_work",
    "crane": "elevated_work",
    "rappel": "elevated_work",
    "helicopter": "aerial_work",
    "aerial": "aerial_work",
    "drone": "aerial_work",
    "plane": "aerial_work",
    "parachute": "aerial_work",
    "crowd": "crowd_management",
    "riot": "crowd_management",
    "mob": "crowd_management",
    "gun": "live_weapon_prop",
    "gunman": "live_weapon_prop",
    "firearm": "live_weapon_prop",
    "shoots": "live_weapon_prop",
    "fired": "live_weapon_prop",
    "gunshot": "live_weapon_prop",
    "knife": "sharp_prop",
    "sword": "sharp_prop",
    "blade": "sharp_prop",
    "machete": "sharp_prop",
    "horse": "animal_wrangling",
    "horseback": "animal_wrangling",
    "dog": "animal_wrangling",
    "snake": "animal_wrangling",
    "animal": "animal_wrangling",
    "bull": "animal_wrangling",
    "wolf": "animal_wrangling",
    "electrical": "electrical_hazard",
    "power line": "electrical_hazard",
    "generator": "electrical_hazard",
    "night": "night_shoot",
    "darkness": "night_shoot",
    "dawn": "night_shoot",
    "dusk": "night_shoot",
    "blizzard": "weather_hazard",
    "storm": "weather_hazard",
    "lightning": "weather_hazard",
    "fog": "weather_hazard",
}

HAZARD_SEVERITY = {
    "pyrotechnics": 9.5,
    "aerial_work": 9.0,
    "water_work": 8.5,
    "vehicle_operation": 8.5,
    "live_weapon_prop": 8.5,
    "stunt_work": 8.0,
    "elevated_work": 7.5,
    "electrical_hazard": 7.5,
    "crowd_management": 6.0,
    "animal_wrangling": 6.0,
    "weather_hazard": 5.5,
    "night_shoot": 4.0,
    "sharp_prop": 4.0,
}

REQUIRED_ROLES = {
    "stunt_work": ["Stunt Coordinator", "On-Set Medic"],
    "pyrotechnics": ["Pyrotechnician", "Fire Safety Officer", "On-Set Medic"],
    "water_work": ["Water Safety Diver", "Marine Coordinator", "On-Set Medic"],
    "aerial_work": ["Aviation Safety Officer", "On-Set Medic"],
    "vehicle_operation": ["Transportation Coordinator", "Stunt Driver"],
    "elevated_work": ["Rigging Gaffer", "On-Set Medic"],
    "live_weapon_prop": ["Armorer / Weapons Master"],
    "animal_wrangling": ["Animal Wrangler", "AHA Representative"],
    "electrical_hazard": ["Best Boy Electric", "Safety Supervisor"],
    "crowd_management": ["Crowd Safety Coordinator", "Security Personnel"],
    "weather_hazard": ["Safety Supervisor"],
    "night_shoot": [],
    "sharp_prop": ["Property Master"],
}


def _risk_level(score: float) -> str:
    if score >= 8:
        return "critical"
    if score >= 6:
        return "high"
    if score >= 4:
        return "moderate"
    return "low"


def scan_scene_for_hazards(
    scene_number: int,
    scene_description: str,
    int_ext: str = "EXT",
    time_of_day: str = "DAY",
    location_type: str = "practical_location",
    slug_line: str = "",
) -> dict:
    text = f"{slug_line} {scene_description}".lower()
    found: dict[str, float] = {}

    for keyword, category in HAZARD_MAP.items():
        if re.search(rf"(?<![a-z]){re.escape(keyword)}(?![a-z])", text):
            found.setdefault(category, HAZARD_SEVERITY.get(category, 5.0))

    if time_of_day.upper() in {"NIGHT", "DUSK", "DAWN"}:
        found["night_shoot"] = HAZARD_SEVERITY["night_shoot"]

    if not found:
        base_score = 1.0
    else:
        max_sev = max(found.values())
        count_bonus = min(len(found) * 0.4, 2.0)
        remote_mult = 1.25 if location_type == "remote" else 1.0
        base_score = min(round((max_sev * 0.75 + count_bonus) * remote_mult, 2), 10.0)

    roles: set[str] = set()
    for category in found:
        roles.update(REQUIRED_ROLES.get(category, []))
    if base_score >= 5:
        roles.add("On-Set Safety Supervisor")

    return {
        "scene_number": scene_number,
        "slug_line": slug_line,
        "int_ext": int_ext,
        "time_of_day": time_of_day,
        "location_type": location_type,
        "hazard_flags": sorted(found),
        "hazard_count": len(found),
        "severity_breakdown": dict(sorted(found.items(), key=lambda x: -x[1])),
        "base_risk_score": base_score,
        "risk_level": _risk_level(base_score),
        "required_safety_roles": sorted(roles),
        "requires_supervisor_signoff": base_score >= 7.0,
        "notes": "Remote location escalates scores 25%." if location_type == "remote" else "",
    }
