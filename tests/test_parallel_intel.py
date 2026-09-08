from matrix.tools.location_enricher import enrich_location_context
from matrix.tools.parallel_intel import extract_signals, merge_live_intel


def test_unknown_lot_stays_default_without_parallel():
    loc = enrich_location_context("Some ranch in Montana", "2026-09-20", live=False)
    assert loc["data_confidence"] == "default_estimates"
    assert loc["live_intel"]["used"] is False
    assert loc["citations"] == []


def test_vasquez_baseline_without_live():
    loc = enrich_location_context("Vasquez Rocks, Agua Dulce, CA", "2026-09-20", live=False)
    assert loc["data_confidence"] == "database_match"
    assert loc["live_intel"]["used"] is False


def test_extract_fire_and_heat_signals():
    blob = "NWS red flag warning and excessive heat for Agua Dulce. FilmLA permit required."
    signals = extract_signals(blob)
    assert "wildfire / fire-weather" in signals
    assert "extreme heat" in signals
    assert "permit / land-use notes" in signals


def test_merge_live_intel_adds_citations_and_fire_season():
    base = enrich_location_context("Vasquez Rocks", "2026-09-20", live=False)
    results = [
        {
            "title": "Red flag warning — NWS",
            "url": "https://example.com/red-flag",
            "publish_date": "2026-09-18",
            "excerpts": ["A red flag warning is in effect. Extreme fire danger."],
        }
    ]
    merged = merge_live_intel(base, results)
    assert merged["data_confidence"] == "database_match+live"
    assert merged["citations"][0]["url"] == "https://example.com/red-flag"
    assert "wildfire / fire-weather" in merged["live_signals"]
    assert any("fire" in r.lower() for r in merged["weather"]["seasonal_risks"])
