import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
today = date.today().isoformat()
video = ROOT / "output" / f"{today}.mp4"
metadata = ROOT / "output" / f"{today}_metadata.json"
log = ROOT / "logs" / f"{today}.log"


def run(script: str, *args: str) -> None:
    result = subprocess.run([PYTHON, str(ROOT / "scripts" / script), *args], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)


if not video.exists() or not metadata.exists():
    weekday_topics = {
        0: "Why does the Moon always show us the same face?",
        1: "A simple way to get better AI answers",
        2: "The two-minute start that beats procrastination",
        3: "Quick quiz: which planet has the fastest winds?",
        4: "Why neural networks use layers",
        5: "The ancient computer found in a shipwreck",
        6: "Why do we see lightning before hearing thunder?",
    }
    run("create_short.py", "--topic", weekday_topics[date.today().weekday()])
if not video.exists() or not metadata.exists():
    raise SystemExit("Render did not produce today's video and metadata")
for attempt in range(2):
    result = subprocess.run([PYTHON, str(ROOT / "scripts" / "upload_youtube.py")], cwd=ROOT)
    if result.returncode == 0:
        break
    if attempt == 1:
        raise SystemExit(result.returncode)
    time.sleep(10)
