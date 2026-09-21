#!/usr/bin/env python3
"""Record MATRIX live dashboard walkthrough for hackathon demo (Playwright)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BASE = "https://matrix-632958340118.us-central1.run.app"
DASH = f"{BASE}/dashboard/"
DEV_UI = f"{BASE}/dev-ui/?app=matrix"
OUT_DIR = Path(__file__).resolve().parent / "raw"
VIEWPORT = {"width": 1280, "height": 720}


async def pause(page, ms: int) -> None:
    """Hold frame so on-screen text is readable in the demo cut."""
    await page.wait_for_timeout(ms)


async def smooth_scroll(page, y: int, steps: int = 8) -> None:
    for i in range(1, steps + 1):
        await page.evaluate(f"window.scrollTo(0, {int(y * i / steps)})")
        await pause(page, 80)


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

        # Warm Cloud Run
        await page.goto(DASH, wait_until="networkidle", timeout=120_000)
        await pause(page, 4500)

        demo_btn = page.get_by_role("button", name="Try the sample western")
        await demo_btn.scroll_into_view_if_needed()
        await pause(page, 2200)
        await demo_btn.click()

        await page.get_by_text("Your first draft", exact=False).wait_for(timeout=90_000)
        await pause(page, 3500)

        oneliner = page.locator("main p").first
        await oneliner.scroll_into_view_if_needed()
        await pause(page, 4000)

        await page.get_by_text("The location already", exact=False).scroll_into_view_if_needed()
        await pause(page, 4500)

        unit = page.get_by_text("The unit brings", exact=False)
        await unit.scroll_into_view_if_needed()
        await pause(page, 3500)

        review = page.get_by_text("Review this first", exact=False)
        await review.scroll_into_view_if_needed()
        await pause(page, 5000)

        trace = page.get_by_text("How this draft was built", exact=False)
        await trace.scroll_into_view_if_needed()
        await pause(page, 5500)

        await smooth_scroll(page, 1100)
        await pause(page, 4000)

        hazard_hdr = page.get_by_text("Production Activities", exact=False).first
        if await hazard_hdr.count():
            await hazard_hdr.scroll_into_view_if_needed()
            await pause(page, 4500)

        see_details = page.get_by_role("button", name="See details")
        await see_details.scroll_into_view_if_needed()
        await pause(page, 1200)
        await see_details.click()

        await page.get_by_text("Shot list", exact=False).wait_for(timeout=30_000)
        await pause(page, 2500)

        scene12 = page.get_by_text("Scene 12", exact=False).first
        await scene12.scroll_into_view_if_needed()
        await pause(page, 6500)

        await smooth_scroll(page, 1200)
        await pause(page, 4500)

        key_grip = page.get_by_text("Key Grip", exact=False).first
        if await key_grip.count():
            await key_grip.scroll_into_view_if_needed()
            await pause(page, 5500)

        loc_hdr = page.get_by_role("heading", name="Location")
        if await loc_hdr.count():
            await loc_hdr.scroll_into_view_if_needed()
            await pause(page, 3500)

        await page.get_by_role("button", name="Back to assessment").click()
        await pause(page, 1500)

        dl = page.get_by_role("button", name="Download JSON")
        await dl.scroll_into_view_if_needed()
        await pause(page, 3500)
        print_btn = page.get_by_role("button", name="Print")
        await print_btn.scroll_into_view_if_needed()
        await pause(page, 3000)

        await page.goto(DEV_UI, wait_until="networkidle", timeout=120_000)
        await pause(page, 6000)

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
