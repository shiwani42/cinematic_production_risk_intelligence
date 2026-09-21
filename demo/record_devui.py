#!/usr/bin/env python3
"""Record Google ADK Dev UI — dismiss telemetry modal, show agent structure."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

DEV_UI = "https://matrix-632958340118.us-central1.run.app/dev-ui/?app=matrix"
OUT_DIR = Path(__file__).resolve().parent / "raw"
VIEWPORT = {"width": 1280, "height": 720}


async def pause(page, ms: int) -> None:
    await page.wait_for_timeout(ms)


async def dismiss_telemetry(page) -> None:
    no = page.get_by_role("button", name="No Thanks")
    try:
        if await no.is_visible(timeout=5000):
            await no.click()
            await pause(page, 600)
            return
    except Exception:
        pass
    await page.keyboard.press("Escape")
    await pause(page, 400)


async def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(OUT_DIR),
            record_video_size=VIEWPORT,
            color_scheme="dark",
        )
        page = await context.new_page()

        await page.goto(DEV_UI, wait_until="networkidle", timeout=120_000)
        await dismiss_telemetry(page)
        await page.get_by_text("Agent Development Kit", exact=False).wait_for(timeout=30_000)
        edit_btn = page.locator("button").nth(2)
        await edit_btn.click()
        await page.get_by_text("matrix_orchestrator", exact=False).first.wait_for(timeout=15_000)
        await pause(page, 16000)

        video_path = await page.video.path()
        await context.close()
        await browser.close()

        if not video_path:
            print("No video captured", file=sys.stderr)
            return 1
        dest = OUT_DIR / "devui.webm"
        Path(video_path).rename(dest)
        print(f"Saved {dest}")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
