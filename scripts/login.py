import asyncio
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
DEBUG_PORT = 9222

async def main():
    executable = CHROME if CHROME.exists() else EDGE
    if not executable.exists():
        raise FileNotFoundError("Neither Google Chrome nor Microsoft Edge was found")
    profile = ROOT / "browser-profile"
    subprocess.Popen([
        str(executable),
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={profile}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://studio.youtube.com",
    ])
    time.sleep(2)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://studio.youtube.com")
        print("Complete Google sign-in in the browser. Waiting for Studio to load...")
        for _ in range(180):
            if "studio.youtube.com" in page.url and "accounts.google.com" not in page.url:
                print("Login detected. The saved browser profile is ready.")
                await asyncio.sleep(3)
                break
            await page.wait_for_timeout(1000)
        else:
            print("Login was not completed within 3 minutes.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
