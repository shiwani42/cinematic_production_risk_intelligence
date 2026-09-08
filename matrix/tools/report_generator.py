"""Safety brief: scene scores × location multiplier + the production-vs-lot interactions."""

from __future__ import annotations

from datetime import datetime, timezone


def _apply_interactions(scenes: list[dict], crew: list[dict], location: dict) -> list[dict]:
    """Location already has hazards. Production adds more. Score the collision."""
    ems = location.get("emergency_services", {}).get("estimated_response_time_minutes", 0)
    loc_type = location.get("location_type", "")
    terrain = " ".join(location.get("terrain_hazards", [])).lower()
    season = " ".join(location.get("weather", {}).get("seasonal_risks", [])).lower()
    cell = location.get("emergency_services", {}).get("cell_coverage", "")
    tired = any(c.get("fatigue_score", 0) >= 60 for c in crew)
    out = []

    for scene in scenes:
        extra = 0.0
        notes: list[str] = []
        flags = set(scene.get("hazard_flags", []))

        if ems > 30:
            extra += 2
            notes.append(f"EMS {ems} min — delayed trauma care")
        if "night_shoot" in flags and loc_type == "remote":
            extra += 1.5
            notes.append("Night + remote: navigation and evac degrade together")
        if tired and scene.get("hazard_count", 0) >= 2:
            extra += 2
            notes.append("Fatigued crew on a multi-hazard scene")
        if "pyrotechnics" in flags and ("wildfire" in season or "heat" in season or "dry" in terrain):
            extra += 1.5
            notes.append("Pyro on fire-prone / hot terrain")
        if "elevated_work" in flags and ("unstable" in terrain or "sandstone" in terrain):
            extra += 1.5
            notes.append("Heights on unstable ground")
        if "water_work" in flags and ("rip" in terrain or "hypothermia" in terrain or "river" in terrain):
            extra += 1.0
            notes.append("Water work on a lot that already has water/cold risk")
        if cell == "none" and scene.get("base_risk_score", 0) >= 6:
            extra += 1.0
            notes.append("No cell on a high-risk scene")

        row = dict(scene)
        row["interaction_notes"] = notes
        row["interaction_bump"] = min(extra, 4.0)
        out.append(row)
    return out


def generate_safety_brief(
    production_title: str,
    shoot_date: str,
    location_name: str,
    scene_risk_data: list[dict],
    crew_fatigue_data: list[dict],
    location_context: dict,
    location_risk_multiplier: float = 1.0,
    producer_name: str = "Production Leadership",
) -> dict:
    stamped = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scenes = _apply_interactions(scene_risk_data, crew_fatigue_data, location_context)

    adjusted = []
    for scene in scenes:
        score = min(
            round(
                scene.get("base_risk_score", 0) * location_risk_multiplier
                + scene.get("interaction_bump", 0),
                2,
            ),
            10.0,
        )
        row = dict(scene)
        row["adjusted_risk_score"] = score
        if score >= 8:
            row["risk_level"] = "critical"
        elif score >= 6:
            row["risk_level"] = "high"
        elif score >= 4:
            row["risk_level"] = "moderate"
        else:
            row["risk_level"] = "low"
        row["requires_supervisor_signoff"] = score >= 7.0
        adjusted.append(row)
    adjusted.sort(key=lambda s: s["adjusted_risk_score"], reverse=True)

    critical = [s for s in adjusted if s["adjusted_risk_score"] >= 7]
    high = [s for s in adjusted if 5 <= s["adjusted_risk_score"] < 7]
    moderate = [s for s in adjusted if 3 <= s["adjusted_risk_score"] < 5]
    crew_crit = [c for c in crew_fatigue_data if c.get("fatigue_score", 0) >= 80]
    crew_high = [c for c in crew_fatigue_data if 60 <= c.get("fatigue_score", 0) < 80]

    scores = [s["adjusted_risk_score"] for s in adjusted]
    avg = round(sum(scores) / len(scores), 2) if scores else 0
    peak = max(scores) if scores else 0

    if peak >= 8 or len(critical) >= 3:
        overall, emoji = "CRITICAL", "🔴"
    elif peak >= 6 or critical:
        overall, emoji = "HIGH", "🟠"
    elif avg >= 4:
        overall, emoji = "MODERATE", "🟡"
    else:
        overall, emoji = "MANAGEABLE", "🟢"

    actions = []
    for scene in critical:
        actions.append(
            {
                "priority": "CRITICAL",
                "category": "scene_hazard",
                "action": (
                    f"Scene {scene['scene_number']}: supervisor sign-off before cameras. "
                    f"Hazards: {', '.join(scene.get('hazard_flags', [])) or 'escalated'}"
                ),
                "required_roles": scene.get("required_safety_roles", []),
            }
        )
    for crew in crew_crit:
        actions.append(
            {
                "priority": "CRITICAL",
                "category": "crew_fatigue",
                "action": (
                    f"{crew['crew_role']} ({crew['department']}): "
                    f"fatigue {crew['fatigue_score']}/100 — rest eval before next call"
                ),
            }
        )
    for crew in crew_high:
        actions.append(
            {
                "priority": "HIGH",
                "category": "crew_fatigue",
                "action": (
                    f"{crew['crew_role']} ({crew['department']}): "
                    f"fatigue {crew['fatigue_score']}/100 — safety buddy"
                ),
            }
        )
    if location_context.get("emergency_services", {}).get("estimated_response_time_minutes", 0) > 30:
        actions.append(
            {
                "priority": "HIGH",
                "category": "location",
                "action": "EMS > 30 min — on-set medic mandatory, confirm helicopter LZ",
            }
        )
    if location_context.get("elevation_m", 0) > 1800:
        actions.append(
            {
                "priority": "MODERATE",
                "category": "location",
                "action": f"Elevation {location_context['elevation_m']}m — 48h acclimatisation",
            }
        )

    return {
        "meta": {
            "product": "MATRIX — Production Risk Intelligence",
            "production_title": production_title,
            "generated_at": stamped,
            "shoot_date": shoot_date,
            "location": location_name,
            "prepared_for": producer_name,
            "version": "1.0",
        },
        "executive_summary": {
            "overall_risk": f"{emoji} {overall}",
            "overall_label": overall,
            "one_liner": (
                f"{len(critical)} scene(s) need safety sign-off, "
                f"{len(crew_crit) + len(crew_high)} crew at elevated fatigue."
                if critical or crew_crit or crew_high
                else "No critical flags. Run standard safety protocols."
            ),
            "total_scenes_analysed": len(adjusted),
            "critical_scenes": len(critical),
            "high_risk_scenes": len(high),
            "moderate_scenes": len(moderate),
            "crew_at_risk": len(crew_crit) + len(crew_high),
            "average_scene_risk_score": avg,
            "highest_scene_risk_score": peak,
        },
        "top_critical_scenes": adjusted[:3],
        "scenes": adjusted,
        "crew_fatigue_summary": {
            "critical": crew_crit,
            "high_risk": crew_high,
            "total_assessed": len(crew_fatigue_data),
            "all": crew_fatigue_data,
        },
        "location_intelligence": location_context,
        "action_items": actions,
        "emergency_reference": {
            "nearest_trauma": location_context.get("emergency_services", {}).get(
                "nearest_trauma_center", "Verify pre-production"
            ),
            "response_time": (
                f"{location_context.get('emergency_services', {}).get('estimated_response_time_minutes', '?')} minutes"
            ),
            "on_set_protocol": [
                "Call emergency services (911 in the USA)",
                "Notify 1st AD and Safety Supervisor",
                "Stop filming — secure the set",
                "Do not move an injured person unless they are in further danger",
                "Send one person to meet EMS and walk them in",
                "Preserve the scene until cleared",
            ],
            "cell_coverage": location_context.get("emergency_services", {}).get("cell_coverage", "unknown"),
        },
        "disclaimer": (
            "MATRIX is AI-assisted planning support. "
            "A qualified safety supervisor must validate every decision before production."
        ),
    }
