"""Split a script excerpt into scenes so risk can attach to a shot list."""

from __future__ import annotations

import re

# SCENE 12 — EXT. CANYON RIDGE — NIGHT
# 12. EXT. CANYON RIDGE - NIGHT
# INT. SALOON - DAY
_HEADING = re.compile(
    r"(?im)^(?:scene\s+)?(\d+[A-Z]?)[.\s—–-]*\s*"
    r"(INT\.?|EXT\.?|INT\/EXT\.?|I\/E\.?)\s*[.\s—–-]+\s*(.+?)$"
)
_SLUG_ONLY = re.compile(
    r"(?im)^(INT\.?|EXT\.?|INT\/EXT\.?|I\/E\.?)\s*[.\s—–-]+\s*(.+?)$"
)


def parse_script_scenes(script_text: str) -> list[dict]:
    """Return ordered scenes with slug, INT/EXT, time of day, and action text."""
    if not script_text or not script_text.strip():
        return []

    lines = script_text.replace("\r\n", "\n").split("\n")
    headings: list[tuple[int, dict]] = []

    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        m = _HEADING.match(line)
        if m:
            number, int_ext, rest = m.group(1), m.group(2).upper().rstrip("."), m.group(3)
            loc, tod = _split_location_tod(rest)
            headings.append(
                (
                    i,
                    {
                        "scene_number": _scene_int(number),
                        "scene_id": number,
                        "int_ext": "INT" if int_ext.startswith("INT") and "EXT" not in int_ext else "EXT",
                        "slug_line": f"{int_ext}. {loc} — {tod}",
                        "location_name": loc,
                        "time_of_day": tod,
                    },
                )
            )
            continue
        m = _SLUG_ONLY.match(line)
        if m and line == line.upper() or (m and len(line) < 80):
            if m and (line.upper().startswith("INT") or line.upper().startswith("EXT")):
                int_ext, rest = m.group(1).upper().rstrip("."), m.group(2)
                loc, tod = _split_location_tod(rest)
                headings.append(
                    (
                        i,
                        {
                            "scene_number": len(headings) + 1,
                            "scene_id": str(len(headings) + 1),
                            "int_ext": "INT" if int_ext.startswith("INT") and "EXT" not in int_ext else "EXT",
                            "slug_line": f"{int_ext}. {loc} — {tod}",
                            "location_name": loc,
                            "time_of_day": tod,
                        },
                    )
                )

    if not headings:
        return [
            {
                "scene_number": 1,
                "scene_id": "1",
                "int_ext": "EXT",
                "slug_line": "UNDATED EXCERPT",
                "location_name": "unspecified",
                "time_of_day": "DAY",
                "description": script_text.strip(),
            }
        ]

    scenes = []
    for idx, (line_no, meta) in enumerate(headings):
        end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        body = "\n".join(lines[line_no + 1 : end]).strip()
        scene = dict(meta)
        scene["description"] = body or meta["slug_line"]
        scenes.append(scene)
    return scenes


def _split_location_tod(rest: str) -> tuple[str, str]:
    cleaned = re.sub(r"[—–]+", "-", rest).strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", cleaned) if p.strip()]
    tod_tokens = {"DAY", "NIGHT", "DUSK", "DAWN", "MORNING", "EVENING", "CONTINUOUS", "LATER"}
    if len(parts) >= 2 and parts[-1].upper().split()[0] in tod_tokens:
        tod = parts[-1].upper().split()[0]
        return "-".join(parts[:-1]).strip(" .-"), tod
    words = cleaned.upper().split()
    if words and words[-1] in tod_tokens:
        return cleaned[: -len(words[-1])].strip(" .-"), words[-1]
    return cleaned.strip(" .-"), "DAY"


def _scene_int(token: str) -> int:
    digits = re.match(r"(\d+)", token)
    return int(digits.group(1)) if digits else 0
