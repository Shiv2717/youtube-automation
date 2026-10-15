import asyncio
import json
import subprocess
import time
import re
from datetime import date
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
LOG = ROOT / "logs" / f"{TODAY}.log"
VIDEO = ROOT / "output" / f"{TODAY}.mp4"
META = ROOT / "output" / f"{TODAY}_metadata.json"
PROFILE = ROOT / "browser-profile"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEBUG_PORT = 9222


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
    print(message)


async def main() -> None:
    if not VIDEO.exists():
        raise FileNotFoundError(f"Prepared video was not found at {VIDEO}")
    if not META.exists():
        raise FileNotFoundError(f"Video metadata was not found at {META}")
    metadata = json.loads(META.read_text(encoding="utf-8"))
    title = str(metadata.get("title", "")).strip()
    description = str(metadata.get("description", "")).strip()
    tags = metadata.get("tags", [])
    if not title or len(title) > 100:
        raise ValueError("Metadata title is missing or exceeds 100 characters")
    if not description:
        raise ValueError("Metadata description is empty")
    if not isinstance(tags, list) or not all(str(tag).strip() for tag in tags):
        raise ValueError("Metadata tags must be a non-empty list")
    history_path = ROOT / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8-sig")) if history_path.exists() else []
    existing = next(
        (item for item in history
         if item.get("date") == TODAY and item.get("topic") == metadata.get("topic")
         and item.get("url")),
        None,
    )
    if existing:
        log(f"SKIP DUPLICATE already published {existing['url']}")
        return 0
    if not CHROME.exists():
        raise FileNotFoundError(f"Chrome was not found at {CHROME}")
    subprocess.Popen([
        str(CHROME),
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
    ])
    time.sleep(2)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
        context = browser.contexts[0]
        page = next(
            (candidate for candidate in context.pages if "studio.youtube.com" in candidate.url),
            context.pages[0] if context.pages else await context.new_page(),
        )
        page.on("dialog", lambda dialog: dialog.accept())
        try:
            await page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            if "accounts.google.com" in page.url or await page.get_by_text("Sign in", exact=True).count():
                log("LOGIN REQUIRED")
                await page.screenshot(path=str(ROOT / "logs" / f"{TODAY}_login_required.png"), full_page=True)
                return 2
            create_button = page.locator('button[aria-label="Create"]').first
            await create_button.click(timeout=15000)
            await page.get_by_role("menuitem", name="Upload videos", exact=True).click(timeout=15000)
            file_input = page.locator('input[type="file"]').first
            await file_input.set_input_files(str(VIDEO))
            await page.get_by_role("heading", name="Details", exact=True).wait_for(timeout=60000)
            title_box = page.locator('input#textbox').first
            if await title_box.count() == 0:
                title_box = page.get_by_role("textbox", name=re.compile("Add a title")).first
            await title_box.fill(title)
            description = page.locator('textarea#textbox').first
            if await description.count() == 0:
                description = page.get_by_role("textbox", name=re.compile("Tell viewers about your video")).first
            await description.fill(description)
            made_for_kids = page.locator(
                'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MADE_FOR_KIDS"]'
            ).first
            if await made_for_kids.count() == 0:
                made_for_kids = page.get_by_role(
                    "radio", name=re.compile(r"No,.*Made for Kids", re.IGNORECASE)
                ).first
            await made_for_kids.click(timeout=15000)
            for _ in range(3):
                await page.locator('button[aria-label="Next"]').first.click(timeout=20000)
                await page.wait_for_timeout(2000)
            public = page.locator(
                'tp-yt-paper-radio-button[name="PUBLIC"]'
            ).first
            if await public.count() == 0:
                public = page.get_by_role("radio", name="Public", exact=True).first
            await public.click(timeout=15000)
            await page.locator('button[aria-label="Publish"]').first.click(timeout=20000)
            await page.wait_for_timeout(5000)
            link = page.locator('a[href*="youtu.be"], a[href*="youtube.com/watch"]').first
            url = await link.get_attribute("href") if await link.count() else page.url
            history.append({k: metadata[k] for k in ("date", "category", "topic", "title")})
            history[-1]["url"] = url
            history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
            log(f"PUBLISHED {url}")
            return 0
        except Exception as exc:
            if not page.is_closed():
                await page.screenshot(path=str(ROOT / "logs" / f"{TODAY}_upload_failure.png"), full_page=True)
            log(f"UPLOAD ERROR {type(exc).__name__}: {exc}")
            return 1
        finally:
            # Leave the normal Chrome process open; CDP disconnects when this
            # script exits and avoids closing the user's browser session.
            pass


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()) or 0)
