"""Build a Secret Compass-style risk register: Hazard | Likelihood + Consequence | Controls."""

from __future__ import annotations

from itertools import count

CATEGORIES = [
    "Team",
    "Medical",
    "Environment",
    "Production Activities",
    "Activity Specific",
    "Accommodation & Transport",
    "Legal, Insurance & PR",
]

# What / how bad / what we do — production-standard, not generic chatbot filler.
LIBRARY: dict[str, dict] = {
    "stunt_work": {
        "category": "Production Activities",
        "subsection": "Stunts & fight action",
        "hazard": "Uncontrolled stunt, fall, or fight action causing impact injury",
        "likelihood": "Likely without a coordinator and rehearsal",
        "consequence": "Fracture, concussion, or time-loss injury; possible stoppage",
        "controls": [
            "Stunt coordinator designs and signs the action",
            "Full-speed rehearsal on the lot before cameras",
            "On-set medic with trauma kit staged at the action",
            "Clear 'cut / abort' protocol owned by the 1st AD",
        ],
    },
    "pyrotechnics": {
        "category": "Production Activities",
        "subsection": "Pyrotechnics & fire",
        "hazard": "Pyrotechnic charge or practical fire leaving the planned burn area",
        "likelihood": "Possible on dry ground or in wind; higher in fire season",
        "consequence": "Burns, wildfire, equipment loss, production shutdown",
        "controls": [
            "Licensed pyrotechnician and fire safety officer on the day",
            "Exclusion zone, extinguishers, and water tender staged",
            "Hot-work permit; check red-flag / CalFire conditions",
            "No pyro if wind or humidity is outside the licensed envelope",
        ],
    },
    "water_work": {
        "category": "Production Activities",
        "subsection": "Water work",
        "hazard": "Crew or cast in moving or cold water — sweep, immersion, hypothermia",
        "likelihood": "Likely in current or when horses / vehicles enter water",
        "consequence": "Drowning risk, hypothermia, lost animal or camera package",
        "controls": [
            "Marine / water-safety coordinator and rescue swimmer",
            "PFDs for anyone in or over water; throw lines staged",
            "Rehearse exit path; abort if current exceeds briefed limit",
            "Hot box / dry clothes immediately off camera",
        ],
    },
    "vehicle_operation": {
        "category": "Production Activities",
        "subsection": "Picture vehicles",
        "hazard": "Picture-vehicle chase, ram, or crash going off the planned line",
        "likelihood": "Possible at speed or on an open highway",
        "consequence": "Collision with public, crew, or unit vehicles; fatality potential",
        "controls": [
            "Stunt driver and transportation coordinator",
            "Road closure or rolling hold with local authority",
            "Camera positions outside the vehicle envelope",
            "Tech scout the run-out and escape lanes",
        ],
    },
    "aerial_work": {
        "category": "Production Activities",
        "subsection": "Aerial / helicopter",
        "hazard": "Aircraft or drone operating over crew, animals, or cliff edge",
        "likelihood": "Possible in wind, canyon rotor, or congested airspace",
        "consequence": "Crash, rotor-wash debris, hearing and eye injury",
        "controls": [
            "Aviation safety officer; published flight brief",
            "No one under the rotor disc; PPE for downwash",
            "Weather abort authority sits with the pilot",
            "NOTAM / local aviation coordination as required",
        ],
    },
    "elevated_work": {
        "category": "Production Activities",
        "subsection": "Heights & cliff edge",
        "hazard": "Work or performance at an unprotected edge or unstable formation",
        "likelihood": "Likely on sandstone / cliff lots without rigging",
        "consequence": "Fall from height — life-changing injury or fatality",
        "controls": [
            "Fall-protection plan; rigging gaffer signed off",
            "No talent at the edge without a harness or crash pad",
            "Spotters and a hard exclusion zone below",
            "Scout for loose rock before the company move",
        ],
    },
    "live_weapon_prop": {
        "category": "Production Activities",
        "subsection": "Weapons",
        "hazard": "Firearm or blank discharge, or a live-looking weapon on the floor",
        "likelihood": "Possible whenever a gun is in the scene",
        "consequence": "Hearing damage, projectile injury, public panic",
        "controls": [
            "Armorer / weapons master has custody at all times",
            "Safety brief before every weapons take",
            "Barrel never covers a person; eye/ear protection as briefed",
            "No personal weapons on set",
        ],
    },
    "animal_wrangling": {
        "category": "Production Activities",
        "subsection": "Animals",
        "hazard": "Horse or other animal bolt, kick, or crush in action",
        "likelihood": "Possible with pyro, rotor-wash, or inexperienced riders",
        "consequence": "Kick/crush injury; animal welfare incident; wrap delay",
        "controls": [
            "Animal wrangler and AHA representative",
            "Quiet set for first takes; no pyro until animals are clear",
            "Escape path and holding area away from the action",
            "Vet / wrangler abort authority",
        ],
    },
    "crowd_management": {
        "category": "Production Activities",
        "subsection": "Crowd & public",
        "hazard": "Public or background crowding the working area",
        "likelihood": "Likely on a public lot or highway",
        "consequence": "Trip, vehicle strike, lost child, social-media incident",
        "controls": [
            "Crowd safety coordinator and security",
            "Physical barrier between public and action",
            "PA announcement and marshals at every hold",
        ],
    },
    "night_shoot": {
        "category": "Environment",
        "subsection": "Night work",
        "hazard": "Reduced visibility plus circadian load on a working crew",
        "likelihood": "Certain on a night unit",
        "consequence": "Slips, vehicle incidents, poor judgement on stunts",
        "controls": [
            "Walk the lot in daylight; mark edges and cables",
            "Adequate unit lighting on paths, not just the frame",
            "Hot food and mandatory breaks on the overnight",
        ],
    },
    "weather_hazard": {
        "category": "Environment",
        "subsection": "Weather",
        "hazard": "Heat, storm, or fire-weather changing the risk picture mid-day",
        "likelihood": "Season-dependent — check the 48h forecast",
        "consequence": "Heat illness, lightning, or fire that stops the day",
        "controls": [
            "Lock forecast 48h out; 1st AD owns the weather abort",
            "Shade, water, and work/rest cycles in heat",
            "No aerials or pyro in electrical storm or red-flag wind",
        ],
    },
    "electrical_hazard": {
        "category": "Production Activities",
        "subsection": "Temporary power",
        "hazard": "Temporary power, generators, or cables on uneven ground",
        "likelihood": "Possible on a remote practical",
        "consequence": "Shock, fire, trip",
        "controls": [
            "Best Boy Electric owns distribution",
            "RCD protection; no daisy-chained cubes on dirt",
            "Cable ramps on walkways",
        ],
    },
    "sharp_prop": {
        "category": "Production Activities",
        "subsection": "Sharp props",
        "hazard": "Practical blade or breakaway glass in a fight",
        "likelihood": "Possible in bar-fight / close combat",
        "consequence": "Laceration",
        "controls": [
            "Property master issues and retrieves blades",
            "Rehearse with dummies; live edge only if signed off",
        ],
    },
}

FATIGUE_ROW = {
    "category": "Team",
    "subsection": "Hours & fatigue",
    "hazard": "Fatigued crew operating kit, vehicles, or working at height",
    "likelihood": "Likely after 12h days, early calls, or 6+ consecutive days",
    "consequence": "Error on a hazardous task; vehicle incident on the drive home",
    "controls": [
        "Turnaround hours enforced; rest day inside 48h if flagged",
        "Safety buddy on heavy equipment — no solo operation",
        "Hotel or unit transport when commute is long after wrap",
    ],
}


def _likelihood_from_score(score: float) -> str:
    if score >= 8:
        return "Likely"
    if score >= 6:
        return "Possible"
    if score >= 4:
        return "Unlikely but credible"
    return "Rare"


def build_risk_register(
    scenes: list[dict],
    crew: list[dict],
    location: dict,
    extras: list[dict] | None = None,
) -> list[dict]:
    """Return categorized, editable rows. extras = user-added hazards from the UI."""
    ids = count(1)
    rows: list[dict] = []
    seen: set[str] = set()

    for scene in scenes:
        for flag in scene.get("hazard_flags", []):
            if flag in seen:
                # attach scene ref to the existing row
                for row in rows:
                    if row.get("source_flag") == flag:
                        refs = row.setdefault("scene_refs", [])
                        if scene.get("scene_number") not in refs:
                            refs.append(scene.get("scene_number"))
                        notes = row.setdefault("interaction_notes", [])
                        for n in scene.get("interaction_notes", []):
                            if n not in notes:
                                notes.append(n)
                continue
            seen.add(flag)
            lib = LIBRARY.get(flag)
            if not lib:
                continue
            row = dict(lib)
            row["id"] = f"h{next(ids)}"
            row["source_flag"] = flag
            row["scene_refs"] = [scene.get("scene_number")]
            row["interaction_notes"] = list(scene.get("interaction_notes", []))
            row["likelihood"] = f"{_likelihood_from_score(scene.get('adjusted_risk_score', scene.get('base_risk_score', 0)))}. {row['likelihood']}"
            rows.append(row)

    tired = [c for c in crew if c.get("fatigue_score", 0) >= 60]
    if tired:
        row = dict(FATIGUE_ROW)
        row["id"] = f"h{next(ids)}"
        row["source_flag"] = "fatigue"
        row["scene_refs"] = []
        names = ", ".join(f"{c['crew_role']} ({c['fatigue_score']})" for c in tired[:4])
        row["risk_detail"] = names
        row["interaction_notes"] = [
            c["crew_role"] + ": " + ", ".join(c.get("top_contributing_factors", [])) for c in tired
        ]
        rows.append(row)

    ems = location.get("emergency_services", {})
    if ems.get("estimated_response_time_minutes", 0) > 20 or location.get("location_type") == "remote":
        rows.append(
            {
                "id": f"h{next(ids)}",
                "source_flag": "ems",
                "category": "Medical",
                "subsection": "Emergency response",
                "hazard": "Delayed trauma care on a remote or slow-EMS lot",
                "likelihood": f"Response estimated {ems.get('estimated_response_time_minutes', '?')} min",
                "consequence": "A survivable injury becomes critical while waiting for an ambulance",
                "controls": [
                    f"Nearest trauma: {ems.get('nearest_trauma_center', 'confirm with dispatch')}",
                    "On-set medic mandatory; confirm helicopter LZ",
                    ems.get("recommendation", "Confirm EMS with local dispatch"),
                    "Satellite comms if cell coverage is none or partial",
                ],
                "scene_refs": [],
                "interaction_notes": [ems.get("response_flag", "")],
            }
        )

    for hazard in location.get("terrain_hazards", [])[:4]:
        rows.append(
            {
                "id": f"h{next(ids)}",
                "source_flag": "terrain",
                "category": "Environment",
                "subsection": "Inherent location hazards",
                "hazard": hazard,
                "likelihood": "Present on this lot before the unit arrives",
                "consequence": "Production-introduced kit and hours make the existing hazard worse",
                "controls": [
                    "Tech scout with safety supervisor before the company move",
                    "Brief the unit on this specific lot hazard at call",
                    "Mark or isolate the feature; do not treat it as set dressing",
                ],
                "scene_refs": [],
                "interaction_notes": [],
            }
        )

    elev = location.get("elevation_m", 0) or 0
    if elev > 1800:
        rows.append(
            {
                "id": f"h{next(ids)}",
                "source_flag": "altitude",
                "category": "Medical",
                "subsection": "Altitude",
                "hazard": f"Working at {elev}m without acclimatisation",
                "likelihood": "Likely for sea-level crew on day one",
                "consequence": "AMS, poor judgement, collapse on exertion",
                "controls": [
                    "48h at elevation before high-exertion scenes",
                    "Medic briefed on AMS; supplemental O2 if >2500m",
                ],
                "scene_refs": [],
                "interaction_notes": [],
            }
        )

    commute = [c for c in crew if (c.get("factor_breakdown") or {}).get("commute", 0) >= 10]
    if commute:
        rows.append(
            {
                "id": f"h{next(ids)}",
                "source_flag": "commute",
                "category": "Accommodation & Transport",
                "subsection": "Unit travel",
                "hazard": "Long drive to set after a heavy day",
                "likelihood": "Likely for crew travelling 80km+",
                "consequence": "Drive-home fatigue collision",
                "controls": [
                    "Production hotel or unit transport for flagged crew",
                    "No self-drive after 14h on set",
                ],
                "scene_refs": [],
                "interaction_notes": [c["crew_role"] for c in commute],
            }
        )

    permit = (location.get("regulatory") or {}).get("permit_notes")
    if permit:
        rows.append(
            {
                "id": f"h{next(ids)}",
                "source_flag": "permit",
                "category": "Legal, Insurance & PR",
                "subsection": "Permits & insurance",
                "hazard": "Filming without the right permit, fire officer, or carrier notice",
                "likelihood": "Possible when the lot is parks, NPS, or a public highway",
                "consequence": "Shut down, fine, or claim declined after an incident",
                "controls": [
                    permit,
                    "Notify production insurance if any crew scores critical fatigue",
                    "Keep the signed RA with the 1st AD on the day",
                ],
                "scene_refs": [],
                "interaction_notes": [],
            }
        )

    for extra in extras or []:
        row = dict(extra)
        row.setdefault("id", f"h{next(ids)}")
        row.setdefault("category", extra.get("category", "Activity Specific"))
        row.setdefault("controls", [])
        row.setdefault("scene_refs", [])
        rows.append(row)

    return rows


def group_register(rows: list[dict]) -> list[dict]:
    grouped = {cat: [] for cat in CATEGORIES}
    other = []
    for row in rows:
        cat = row.get("category", "Activity Specific")
        if cat in grouped:
            grouped[cat].append(row)
        else:
            other.append(row)
    sections = [{"category": cat, "rows": grouped[cat]} for cat in CATEGORIES if grouped[cat]]
    if other:
        sections.append({"category": "Other", "rows": other})
    return sections
