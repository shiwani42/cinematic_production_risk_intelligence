#!/usr/bin/env python3
"""Record MATRIX dashboard walkthrough (live Cloud Run) — no Dev UI segment."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

DASH = "https://matrix-632958340118.us-central1.run.app/dashboard/"
OUT_DIR = Path(__file__).resolve().parent / "raw"
VIEWPORT = {"width": 1280, "height": 720}


async def pause(page, ms: int) -> None:
    await page.wait_for_timeout(ms)


async def smooth_scroll(page, y: int, steps: int = 10) -> None:
    for i in range(1, steps + 1):
        await page.evaluate(f"window.scrollTo(0, {int(y * i / steps)})")
        await pause(page, 100)


async def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(OUT_DIR),
            record_video_size=VIEWPORT,
            color_scheme="light",
        )
        page = await context.new_page()

        await page.goto(DASH, wait_until="networkidle", timeout=120_000)
        await pause(page, 3500)

        demo_btn = page.get_by_role("button", name="Try the sample western")
        await demo_btn.scroll_into_view_if_needed()
        await pause(page, 2800)
        await demo_btn.click()

        await page.get_by_text("Your first draft", exact=False).wait_for(timeout=90_000)
        await pause(page, 4500)

        crit = page.get_by_text("CRITICAL", exact=False).first
        if await crit.count():
            await crit.scroll_into_view_if_needed()
            await pause(page, 2500)

        await page.get_by_text("The location already", exact=False).scroll_into_view_if_needed()
        await pause(page, 5500)

        await page.get_by_text("The unit brings", exact=False).scroll_into_view_if_needed()
        await pause(page, 4500)

        await page.get_by_text("Review this first", exact=False).scroll_into_view_if_needed()
        await pause(page, 6000)

        trace = page.get_by_text("How this draft was built", exact=False)
        await trace.scroll_into_view_if_needed()
        await pause(page, 7000)

        for agent in (
            "hazard_scanner",
            "fatigue_forecaster",
            "location_enricher",
            "risk_synthesizer",
        ):
            row = page.get_by_text(agent, exact=False).first
            if await row.count():
                await row.scroll_into_view_if_needed()
                await pause(page, 1200)

        await pause(page, 2500)
        await smooth_scroll(page, 1300)
        await pause(page, 5000)

        hazard_hdr = page.get_by_text("Production Activities", exact=False).first
        if await hazard_hdr.count():
            await hazard_hdr.scroll_into_view_if_needed()
            await pause(page, 5500)

        await smooth_scroll(page, 1800)
        await pause(page, 4000)

        see_details = page.get_by_role("button", name="See details")
        await see_details.scroll_into_view_if_needed()
        await pause(page, 1500)
        await see_details.click()

        await page.get_by_text("Shot list", exact=False).wait_for(timeout=30_000)
        await pause(page, 3000)

        scene12 = page.get_by_text("Scene 12", exact=False).first
        await scene12.scroll_into_view_if_needed()
        await pause(page, 7500)

        await smooth_scroll(page, 1400)
        await pause(page, 5000)

        key_grip = page.get_by_text("Key Grip", exact=False).first
        if await key_grip.count():
            await key_grip.scroll_into_view_if_needed()
            await pause(page, 6500)

        loc_hdr = page.get_by_role("heading", name="Location")
        if await loc_hdr.count():
            await loc_hdr.scroll_into_view_if_needed()
            await pause(page, 4500)

        await page.get_by_role("button", name="Back to assessment").click()
        await pause(page, 2000)

        dl = page.get_by_role("button", name="Download JSON")
        await dl.scroll_into_view_if_needed()
        await pause(page, 4500)
        print_btn = page.get_by_role("button", name="Print")
        await print_btn.scroll_into_view_if_needed()
        await pause(page, 4000)

        video_path = await page.video.path()
        await context.close()
        await browser.close()

        if not video_path:
            print("No video captured", file=sys.stderr)
            return 1
        dest = OUT_DIR / "walkthrough.webm"
        Path(video_path).rename(dest)
        print(f"Saved {dest}")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
