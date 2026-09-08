"""Optional Parallel Search layer for live lot intel. Analyze still works with no key."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

SEARCH_URL = "https://api.parallel.ai/v1/search"
TIMEOUT_SEC = 8

FIRE_MARKERS = (
    "wildfire",
    "red flag",
    "red-flag",
    "fire weather",
    "fire restriction",
    "burn ban",
    "fire danger",
)
HEAT_MARKERS = ("excessive heat", "heat advisory", "extreme heat", "heat warning")
PERMIT_MARKERS = ("film permit", "filming permit", "filmla", "nps permit", "usfs")
EMS_MARKERS = ("trauma", "emergency department", "level i", "level 1")
CLOSURE_MARKERS = ("road closed", "evacuation", "lot closed", "park closure")


def parallel_configured() -> bool:
    return bool(os.environ.get("PARALLEL_API_KEY"))


def extract_signals(blob: str) -> list[str]:
    low = blob.lower()
    found: list[str] = []
    if any(m in low for m in FIRE_MARKERS):
        found.append("wildfire / fire-weather")
    if any(m in low for m in HEAT_MARKERS):
        found.append("extreme heat")
    if any(m in low for m in PERMIT_MARKERS):
        found.append("permit / land-use notes")
    if any(m in low for m in EMS_MARKERS):
        found.append("trauma / EMS mention")
    if any(m in low for m in CLOSURE_MARKERS):
        found.append("access / closure")
    return found


def citations_from_results(results: list[dict], limit: int = 5) -> list[dict]:
    out: list[dict] = []
    for row in results:
        excerpts = row.get("excerpts") or []
        excerpt = excerpts[0] if excerpts else ""
        if isinstance(excerpt, str):
            excerpt = excerpt[:280]
        out.append(
            {
                "title": row.get("title") or row.get("url") or "Source",
                "url": row.get("url") or "",
                "publish_date": row.get("publish_date"),
                "excerpt": excerpt,
            }
        )
        if len(out) >= limit:
            break
    return out


def merge_live_intel(base: dict, results: list[dict]) -> dict:
    """Fold cited Parallel excerpts into the lot record. Never blanks the baseline."""
    merged = dict(base)
    citations = citations_from_results(results)
    blob = " ".join(
        f"{c.get('title', '')} {c.get('excerpt', '')}" for c in citations
    )
    signals = extract_signals(blob)
    weather = dict(merged.get("weather") or {})
    seasonal = list(weather.get("seasonal_risks") or [])
    terrain = list(merged.get("terrain_hazards") or [])
    for signal in signals:
        note = f"Live web: {signal}"
        if "fire" in signal or "heat" in signal:
            if signal not in seasonal:
                seasonal.append(signal)
        if note not in terrain:
            terrain.append(note)
    weather["seasonal_risks"] = seasonal
    if signals:
        weather["live_summary"] = "Current web mentions: " + ", ".join(signals)
    merged["weather"] = weather
    merged["terrain_hazards"] = terrain
    merged["citations"] = citations
    merged["live_signals"] = signals
    merged["live_intel"] = {
        "used": True,
        "source": "parallel",
        "signal_count": len(signals),
    }
    confidence = merged.get("data_confidence", "default_estimates")
    if citations:
        merged["data_confidence"] = (
            "database_match+live" if confidence == "database_match" else "live_search"
        )
    return merged


def fetch_location_results(location_name: str, shoot_date: str) -> list[dict]:
    key = os.environ.get("PARALLEL_API_KEY", "")
    if not key:
        return []
    payload = {
        "objective": (
            f"Current filming hazards, fire restrictions, weather, nearest trauma hospital, "
            f"and permit notes for {location_name} around {shoot_date}."
        ),
        "search_queries": [
            f"{location_name} film permit requirements",
            f"{location_name} wildfire red flag weather {shoot_date[:4]}",
            f"{location_name} nearest trauma hospital",
        ],
        "mode": "fast",
        "advanced_settings": {"max_results": 6, "location": "us"},
    }
    try:
        from parallel import Parallel

        client = Parallel(api_key=key)
        search = client.search(**{k: v for k, v in payload.items() if k != "advanced_settings"})
        rows = []
        for result in getattr(search, "results", []) or []:
            rows.append(
                {
                    "title": getattr(result, "title", None),
                    "url": getattr(result, "url", None),
                    "publish_date": getattr(result, "publish_date", None),
                    "excerpts": list(getattr(result, "excerpts", None) or []),
                }
            )
        return rows
    except Exception:
        return _search_http(key, payload)


def _search_http(key: str, payload: dict) -> list[dict]:
    req = urllib.request.Request(
        SEARCH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-api-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return list(body.get("results") or [])


def live_location_intel(location_name: str, shoot_date: str) -> dict:
    """Returns {ok, results, error}. Never raises to the caller."""
    if not parallel_configured():
        return {"ok": False, "results": [], "error": "no_key"}
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fetch_location_results, location_name, shoot_date)
            results = future.result(timeout=TIMEOUT_SEC)
        return {"ok": True, "results": results, "error": None}
    except (FuturesTimeout, TimeoutError, urllib.error.URLError, OSError, Exception) as exc:
        return {"ok": False, "results": [], "error": str(exc)[:240]}
