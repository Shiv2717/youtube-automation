import asyncio
import json
import math
import os
import shutil
import subprocess
import argparse
import csv
import sys
from datetime import date
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinematic.audio import voice_filter
from cinematic.captions import write_srt
from cinematic.character import make_frames
from cinematic.config import load_config
from cinematic.extras import make_thumbnails
from cinematic.look import filters as look_filters
from cinematic.motion import position_expression, zoom_expression
from cinematic.painterly import make_ambient_frames, make_painterly_scenes
from cinematic.transitions import transition_sequence

TODAY = date.today().isoformat()
LOG = ROOT / "logs" / f"{TODAY}.log"
OUT = ROOT / "output" / f"{TODAY}.mp4"
AUDIO = ROOT / "output" / f"{TODAY}.mp3"
WORDS = ROOT / "output" / f"{TODAY}_words.json"
SCENES = ROOT / "output" / f"{TODAY}_scenes"
WIDTH, HEIGHT, FPS = 1080, 1920, 30
OUTPUT_WIDTH, OUTPUT_HEIGHT = WIDTH, HEIGHT
CONFIG = load_config(ROOT)
FPS = int(CONFIG.get("cinematic", {}).get("output_fps", FPS))
PREVIEW = False
ACTIVE_TOPIC = None
OUTPUT_SUFFIX = ""
SCENE_COUNT = 8
REMOTION_ROOT = ROOT / "remotion-video"

CONTENT = {
    0: ("Science/space facts", "Why does the Moon always show us the same face?",
        "The Moon always shows nearly the same face to Earth, but it is not standing still. "
        "The Moon rotates once on its axis in about the same time it takes to orbit Earth: about 27 days. "
        "This timing is called synchronous rotation. As the Moon travels around us, it turns just enough to keep the same side facing Earth. "
        "The far side is not the dark side; it gets sunlight too, just at different times. "
        "Look up tonight, and remember: the Moon is spinning. Follow for more quick space facts.",
        "Moon's SAME FACE", "SYNCHRONOUS ROTATION", "ABOUT 27 DAYS", "ORBIT = ROTATION",
        "THE FAR SIDE", "FOLLOW FOR MORE", "Moon Has a Secret Rhythm! #Shorts",
        "The Moon rotates once for every orbit around Earth.\n#Shorts #Space #Astronomy", ["Moon", "space facts", "astronomy"]),
    1: ("Tech and AI tips", "A simple way to get better AI answers",
        "Want more useful answers from an AI assistant? Give it a clear role, the exact task, and the format you want back. "
        "For example, ask it to act as a study coach, explain one concept for a beginner, and finish with three quiz questions. "
        "Adding constraints removes guesswork and makes the result easier to check. "
        "You can also ask for assumptions to be listed before the answer. "
        "Clear instructions usually beat longer instructions. Follow for more practical AI tips.",
        "BETTER AI ANSWERS", "ROLE + TASK", "ADD A FORMAT", "STATE CONSTRAINTS",
        "CHECK ASSUMPTIONS", "FOLLOW FOR MORE", "The AI Prompt Trick That Works #Shorts",
        "Use a role, task, format, and constraints for clearer AI results.\n#Shorts #AI #Tech", ["AI tips", "prompting", "technology"]),
    2: ("Motivation and productivity", "The two-minute start that beats procrastination",
        "When a task feels too big, shrink the starting line to two minutes. "
        "Open the document, write one rough sentence, or put the first item on your desk. "
        "The goal is not to finish in two minutes; it is to replace hesitation with a visible first action. "
        "Once you begin, continuing often feels easier because the task is no longer abstract. "
        "Make the first step tiny, specific, and immediate. Follow for more productivity ideas.",
        "CAN'T START?", "MAKE IT 2 MINUTES", "ONE TINY ACTION", "REMOVE FRICTION",
        "BUILD MOMENTUM", "FOLLOW FOR MORE", "The 2-Minute Start Rule #Shorts",
        "Make the first action tiny and specific to overcome procrastination.\n#Shorts #Productivity #Motivation", ["productivity", "motivation", "habits"]),
    3: ("Quiz with a countdown timer", "Quick quiz: which planet has the fastest winds?",
        "Quick space quiz! Which planet has the fastest winds in the Solar System? "
        "Is it A, Earth? B, Jupiter? Or C, Neptune? "
        "Three, two, one… the answer is Neptune. Winds there can reach more than 2,000 kilometers per hour, according to NASA. "
        "That is far faster than a hurricane on Earth. Neptune is an ice giant, and its atmosphere is mostly hydrogen, helium, and methane. "
        "Did you get it right? Follow for another quick quiz.",
        "SPACE QUIZ", "FASTEST WINDS?", "A: EARTH", "B: JUPITER", "C: NEPTUNE", "ANSWER: NEPTUNE",
        "Which Planet Has the Fastest Winds? #Shorts",
        "Neptune has the fastest winds measured on any planet in our Solar System.\n#Shorts #Quiz #Space", ["quiz", "Neptune", "space trivia"]),
    4: ("Electronics / coding / AI-ML tip", "Why neural networks use layers",
        "Why do neural networks use layers instead of one giant calculation? "
        "Each layer can transform the incoming data into a more useful representation. "
        "In an image system, early layers may respond to simple edges, while later layers combine those patterns into shapes and objects. "
        "A training process adjusts the network's numerical weights so its output becomes more accurate on examples. "
        "The layers do not understand images like people do; they learn mathematical patterns from data. "
        "That layered design is why deep learning is called deep. Follow for more AI and coding tips.",
        "WHY LAYERS?", "PATTERNS BUILD", "EDGES → SHAPES", "WEIGHTS ADJUST",
        "DEEP LEARNING", "FOLLOW FOR MORE", "The Secret Behind Neural Networks #Shorts",
        "Neural-network layers transform data into increasingly useful mathematical patterns.\n#Shorts #AI #MachineLearning", ["AI", "neural networks", "machine learning"]),
    5: ("Short story or history", "The ancient computer found in a shipwreck",
        "In 1901, divers found a mysterious mechanism in a Roman shipwreck near the Greek island of Antikythera. "
        "It contained interlocking gears and was built more than 2,000 years ago. "
        "Researchers now call it the Antikythera mechanism. "
        "Its dials could track astronomical cycles, including the positions of celestial bodies and eclipses. "
        "Only fragments survive, so some details remain debated, but it is widely described as the earliest known analog computer. "
        "Ancient technology can still surprise us. Follow for more short history stories.",
        "FOUND IN 1901", "A GEAR-DRIVEN DEVICE", "OVER 2,000 YEARS OLD", "TRACKED THE SKY",
        "ANTIKYTHERA", "FOLLOW FOR MORE", "The Ancient Computer from a Shipwreck #Shorts",
        "The Antikythera mechanism is an ancient Greek gear-driven astronomical device.\n#Shorts #History #Science", ["history", "Antikythera", "ancient technology"]),
    6: ("60-second popular-topic explainer", "Why do we see lightning before hearing thunder?",
        "Lightning and thunder happen at almost the same time, but we see the flash before we hear the boom. "
        "That is because light travels much faster through air than sound does. "
        "Light reaches your eyes almost instantly across a storm, while sound takes longer to cross the same distance. "
        "A rough rule is that every five seconds between the flash and the thunder represents about one mile of distance. "
        "Never use that estimate to ignore storm safety: if you hear thunder, lightning is close enough to be dangerous. Follow for more explainers.",
        "LIGHTNING FIRST", "THUNDER LATER", "LIGHT IS FASTER", "COUNT THE DELAY",
        "STAY WEATHER-SAFE", "FOLLOW FOR MORE", "Why Lightning Comes Before Thunder #Shorts",
        "Light travels faster than sound, so the flash reaches you before the thunder.\n#Shorts #Science #Weather", ["lightning", "thunder", "science"]),
}
weekday = date.today().weekday()
config = CONTENT[weekday]
CATEGORY, TOPIC, SCRIPT, *rest = config
cards = rest[:6]
TITLE, DESCRIPTION, TAGS = rest[6:]
PALETTES = [
    ((12, 18, 54), (92, 28, 122)),
    ((3, 42, 60), (12, 115, 122)),
    ((30, 16, 70), (173, 39, 90)),
    ((8, 54, 44), (104, 134, 35)),
    ((48, 24, 15), (180, 76, 20)),
    ((20, 28, 64), (35, 100, 180)),
]


def topic_content(topic: str) -> tuple:
    if topic.lower() == "what happens if you fall into a black hole":
        return (
            "Science/space facts", topic,
            "What would happen if you fell into a black hole? First, the view would become distorted as gravity bent the light around you. "
            "Then, to a distant observer, your motion would appear to slow near the event horizon. "
            "For you, the fall would continue, but tidal forces would stretch you along the direction of gravity. "
            "The deeper you went, the more extreme the difference in gravity between your head and feet could become. "
            "And beyond the event horizon, every possible future path would lead inward. "
            "That is the part scientists still cannot observe directly. Follow for more cosmic mysteries.",
            "FALLING INTO A BLACK HOLE", "LIGHT BENDS", "TIME LOOKS SLOW", "TIDAL FORCES", "NO WAY BACK",
            "THE UNANSWERED PART", "What Falling Into a Black Hole Really Means #Shorts",
            "Gravity bends light, slows the distant view, and creates extreme tidal forces.\n#Shorts #Space #Astronomy",
            ["black holes", "space", "astronomy"],
        )
    words = topic.strip().rstrip("?") + ". "
    return (
        "Custom explainer", topic,
        f"{topic}? Here is the first clue. {words}"
        "Next, the key idea is that the system follows physical rules rather than intuition. "
        "Finally, one consequence changes how you see the topic. "
        "The surprising part is what happens after that. Follow for more clear explainers.",
        topic.upper()[:28], "THE FIRST CLUE", "THE KEY IDEA", "THE CONSEQUENCE", "THE SURPRISE",
        "FOLLOW FOR MORE", f"{topic[:48]} #Shorts",
        f"A concise three-act explainer about {topic}.\n#Shorts #Explainer",
        [topic.split()[0], "explainer", "science"],
    )


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
    print(message)


def ffmpeg_path() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError("ffmpeg is not available") from exc


async def make_voiceover() -> None:
    import edge_tts
    import asyncio

    rate = "-35%" if CONFIG["cinematic"].get("style") in {
        "painterly_warm", "rainy_night", "snowy_dusk"
    } else "+0%"
    temp_audio = AUDIO.with_suffix(".tmp.mp3")
    last_error = None
    for attempt in range(2):
        try:
            if temp_audio.exists():
                temp_audio.unlink()
            await edge_tts.Communicate(SCRIPT, "en-US-GuyNeural", rate=rate).save(str(temp_audio))
            if temp_audio.stat().st_size < 1000:
                raise RuntimeError("Edge TTS returned an empty audio file")
            temp_audio.replace(AUDIO)
            return
        except Exception as exc:
            last_error = exc
            log(f"VOICEOVER RETRY {attempt + 1}/2: {type(exc).__name__}: {exc}")
            if attempt == 0:
                await asyncio.sleep(3)
    raise RuntimeError(f"Voiceover generation failed after retry: {last_error}") from last_error


def make_cards() -> None:
    if CONFIG["cinematic"].get("style") in {"painterly_warm", "rainy_night", "snowy_dusk"}:
        make_painterly_scenes(SCENES, WIDTH, HEIGHT, CONFIG["cinematic"]["style"])
        return
    SCENES.mkdir(parents=True, exist_ok=True)
    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    editorial = CONFIG["cinematic"].get("style") == "pinterest_editorial"
    title_font = ImageFont.truetype(font_path, 88 if not editorial else 82)
    body_font = ImageFont.truetype(font_path, 58 if not editorial else 48)
    labels = [(card, "") for card in cards]
    for index, (headline, subhead) in enumerate(labels):
        if editorial:
            paper = [(244, 234, 211), (236, 225, 202), (248, 240, 224),
                     (225, 226, 213), (242, 220, 193), (232, 217, 196)][index % 6]
            first, second = paper, tuple(max(0, value - 18) for value in paper)
        else:
            first, second = PALETTES[index % len(PALETTES)]
        image = Image.new("RGB", (WIDTH, HEIGHT), first)
        pixels = image.load()
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            color = tuple(int(first[i] * (1 - ratio) + second[i] * ratio) for i in range(3))
            for x in range(WIDTH):
                pixels[x, y] = color
        draw = ImageDraw.Draw(image, "RGBA")
        if editorial:
            ink = (31, 28, 24, 235)
            draw.rounded_rectangle((56, 170, WIDTH - 56, HEIGHT - 170), radius=34,
                                   outline=(ink[0], ink[1], ink[2], 150), width=5)
            draw.ellipse((WIDTH - 300, 260, WIDTH - 115, 445), fill=(193, 102, 63, 180))
            draw.arc((120, 520, 430, 830), 200, 345, fill=(31, 28, 24, 120), width=12)
            for y in range(850, 1200, 110):
                draw.line((115, y, WIDTH - 115, y + 20), fill=(31, 28, 24, 32), width=3)
            text_fill, accent = ink, (173, 76, 52)
        else:
            for radius, alpha in [(760, 38), (520, 32), (300, 28)]:
                draw.ellipse((WIDTH - radius, -radius // 2, WIDTH + radius, radius), fill=(255, 180, 80, alpha))
            draw.ellipse((70, 240, 260, 430), fill=(255, 210, 90, 220), outline=(255, 255, 255, 180), width=5)
            draw.arc((670, 550, 1030, 910), 190, 350, fill=(255, 255, 255, 120), width=7)
            for y in range(770, 1120, 95):
                draw.line((110, y, 970, y - 65), fill=(255, 255, 255, 45), width=3)
            text_fill, accent = "white", (255, 232, 150)
        bbox = draw.multiline_textbbox((0, 0), headline, font=title_font, spacing=12, align="center")
        draw.multiline_text(((WIDTH - (bbox[2] - bbox[0])) / 2, 1040), headline, font=title_font,
                            fill=text_fill, spacing=12, align="center",
                            stroke_width=0 if editorial else 3, stroke_fill=(0, 0, 0, 100))
        bbox2 = draw.multiline_textbbox((0, 0), subhead, font=body_font, spacing=8, align="center")
        draw.multiline_text(((WIDTH - (bbox2[2] - bbox2[0])) / 2, 1330), subhead, font=body_font,
                            fill=accent, spacing=8, align="center",
                            stroke_width=0 if editorial else 2, stroke_fill=(0, 0, 0, 120))
        image.save(SCENES / f"scene_{index:02d}.png", optimize=True)


def make_character_frames() -> None:
    character_dir = ROOT / "output" / f"{TODAY}_character"
    character_dir.mkdir(parents=True, exist_ok=True)
    suit = (225, 239, 255, 255)
    glass = (45, 211, 255, 245)
    shadow = (5, 12, 30, 150)
    for frame in range(30):
        image = Image.new("RGBA", (420, 620), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        phase = frame / 30 * math.tau
        bob = int(10 * math.sin(phase))
        sway = int(12 * math.sin(phase + 0.7))
        draw.ellipse((55, 550, 365, 605), fill=shadow)
        draw.ellipse((115 + sway, 55 + bob, 305 + sway, 245 + bob), fill=suit,
                     outline=(255, 255, 255, 240), width=8)
        draw.ellipse((140 + sway, 82 + bob, 280 + sway, 190 + bob), fill=glass,
                     outline=(180, 255, 255, 220), width=5)
        draw.arc((155 + sway, 104 + bob, 250 + sway, 158 + bob), 190, 330,
                 fill=(255, 255, 255, 220), width=6)
        draw.rounded_rectangle((105 + sway, 220 + bob, 315 + sway, 475 + bob),
                               radius=55, fill=suit, outline=(255, 255, 255, 240), width=8)
        draw.rounded_rectangle((155 + sway, 275 + bob, 265 + sway, 370 + bob),
                               radius=18, fill=(22, 55, 105, 255), outline=(70, 238, 255, 220), width=5)
        draw.ellipse((181 + sway, 302 + bob, 203 + sway, 324 + bob), fill=(80, 255, 190, 255))
        draw.ellipse((218 + sway, 302 + bob, 240 + sway, 324 + bob), fill=(255, 210, 80, 255))
        arm = int(20 * math.sin(phase + 1.2))
        draw.line((115 + sway, 260 + bob, 45 + arm, 360 + bob), fill=suit, width=34)
        draw.line((305 + sway, 260 + bob, 370 - arm, 350 + bob), fill=suit, width=34)
        draw.ellipse((27 + arm, 345 + bob, 67 + arm, 385 + bob), fill=glass)
        draw.ellipse((350 - arm, 335 + bob, 390 - arm, 375 + bob), fill=glass)
        draw.line((155 + sway, 470 + bob, 135 + sway, 555 + bob), fill=suit, width=42)
        draw.line((265 + sway, 470 + bob, 285 + sway, 555 + bob), fill=suit, width=42)
        image.save(character_dir / f"char_{frame:03d}.png", optimize=True)
    return character_dir


def get_audio_duration() -> float:
    result = subprocess.run([ffmpeg_path(), "-i", str(AUDIO)], capture_output=True, text=True)
    marker = "Duration: "
    line = next((line for line in result.stderr.splitlines() if marker in line), "")
    value = line.split(marker, 1)[1].split(",", 1)[0]
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def caption_words(duration: float) -> list[dict]:
    words = SCRIPT.split()
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(AUDIO), word_timestamps=True)
        found = [{"word": w.word.strip(), "start": w.start, "end": w.end}
                 for seg in segments for w in (seg.words or []) if w.word.strip()]
        if found:
            return found
    except Exception as exc:
        log(f"CAPTION TRANSCRIPTION FALLBACK: {exc}")
    step = duration / max(len(words), 1)
    return [{"word": word, "start": i * step, "end": (i + 1) * step} for i, word in enumerate(words)]


def render_remotion(duration: float, words: list[dict]) -> None:
    """Render the editorial motion-design composition and preserve the existing output path."""
    effective_duration = min(duration, 10.0) if PREVIEW else min(duration, 58.5)
    fps = 30
    frames = max(1, int(round(effective_duration * fps)))
    public_dir = REMOTION_ROOT / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    audio_name = f"narration-{TODAY}{OUTPUT_SUFFIX}{'_preview' if PREVIEW else ''}.mp3"
    public_audio = public_dir / audio_name
    shutil.copy2(AUDIO, public_audio)

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\\s+", SCRIPT) if part.strip()]
    subtitles = [sentences[min(i, len(sentences) - 1)] if sentences else TOPIC for i in range(5)]
    accents = ["#f06a43", "#f0a35b", "#e76f51", "#c96d4c", "#e9b45e"]
    layouts = ["hero", "steps", "quote", "stat", "hero"]
    dynamic_scenes = []
    available_cards = cards if cards else [
        TOPIC, "THE KEY IDEA", "WHY IT MATTERS", "ONE TAKEAWAY", "REMEMBER THIS", "FOLLOW FOR MORE"
    ]
    for i in range(5):
        dynamic_scenes.append({
            "kicker": f"{CATEGORY} / {i + 1:02d}",
            "headline": str(available_cards[i % len(available_cards)]),
            "highlight": str(available_cards[(i + 1) % len(available_cards)]),
            "subtitle": subtitles[i],
            "accent": accents[i],
            "layout": layouts[i],
        })

    props = {
        "title": TITLE,
        "scenes": dynamic_scenes,
        "accentColor": "#e45b35",
        "backgroundColor": "#f4efe5",
        "audioFile": audio_name,
        "captions": words,
    }
    props_path = public_dir / f"props-{TODAY}{OUTPUT_SUFFIX}{'_preview' if PREVIEW else ''}.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")

    npx = "npx.cmd" if os.name == "nt" else "npx"
    target_width = 480 if PREVIEW else OUTPUT_WIDTH
    target_height = int(target_width * OUTPUT_HEIGHT / OUTPUT_WIDTH) // 2 * 2
    command = [
        npx, "remotion", "render", "src/index.ts", "MyComp", str(OUT),
        f"--props={props_path.as_posix()}",
        f"--duration={frames}",
        f"--fps={fps}",
        f"--width={target_width}",
        f"--height={target_height}",
        "--codec=h264", "--pixel-format=yuv420p",
    ]
    try:
        log("REMOTION RENDER " + " ".join(command))
        result = subprocess.run(command, cwd=REMOTION_ROOT, check=False)
        if result.returncode:
            raise RuntimeError(f"Remotion render failed with exit code {result.returncode}")
    finally:
        for path in (public_audio, props_path):
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                log(f"REMOTION CLEANUP WARNING: {exc}")


def render(duration: float, words: list[dict], character_dir: Path) -> None:
    if CONFIG.get("cinematic", {}).get("renderer", "remotion") == "remotion":
        render_remotion(duration, words)
        return

    ffmpeg = ffmpeg_path()
    effective_duration = min(duration, 10.0) if PREVIEW else min(duration, 58.5)
    scene_duration = effective_duration / SCENE_COUNT
    subtitles = ROOT / "output" / f"{TODAY}.ass"
    with subtitles.open("w", encoding="utf-8") as handle:
        handle.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
        handle.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
                     "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                     "Alignment, MarginL, MarginR, MarginV, Encoding\n")
        handle.write("Style: Default,Arial,64,&H00FFFFFF,&H0000D7FF,&H00101010,&H80000000,1,0,0,0,100,100,0,0,1,3,1,5,80,80,500,1\n\n")
        handle.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        visible_words = words if CONFIG["cinematic"].get("style") not in {
            "painterly_warm", "rainy_night", "snowy_dusk"
        } else words[:4] + [word for word in words if word["start"] >= max(0, duration - 2.5)]
        for word in visible_words:
            start = max(0, word["start"])
            end = max(start + 0.08, word["end"])
            text = word["word"].replace("{", "(").replace("}", ")")
            handle.write(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{text}\n")
    subtitle_path = subtitles.as_posix().replace(":", r"\:")
    target_width = 480 if PREVIEW else OUTPUT_WIDTH
    target_height = int(target_width * OUTPUT_HEIGHT / OUTPUT_WIDTH) // 2 * 2
    inputs = []
    filters = []
    motion = CONFIG["cinematic"]["motion"]
    for index in range(SCENE_COUNT):
        inputs.extend(["-loop", "1", "-t", f"{scene_duration + 0.6:.3f}", "-i",
                       str(SCENES / f"scene_{index:02d}.png")])
        zoom = zoom_expression(index, motion.get("ken_burns", True))
        x, y = position_expression(index, motion.get("parallax", True))
        filters.append(
            f"[{index}:v]scale={target_width + 120}:{target_height + 120},zoompan=z='{zoom}':x='{x}':"
            f"y='{y}':d={max(1, int(scene_duration * FPS))}:s={target_width}x{target_height}:fps={FPS},"
            f"setsar=1,format=yuv420p[v{index}]"
        )
    last = "v0"
    transitions = transition_sequence(CONFIG, SCENE_COUNT)
    transition_duration = CONFIG["cinematic"]["transitions"].get("duration", 0.28)
    for index in range(1, SCENE_COUNT):
        out = f"mix{index}"
        offset = index * scene_duration - (transition_duration * index)
        transition = transitions[index - 1] if CONFIG["cinematic"]["transitions"].get("enabled", True) else "fade"
        filters.append(f"[{last}][v{index}]xfade=transition={transition}:duration={transition_duration}:offset={offset:.3f}[{out}]")
        last = out
    visual_chain = ["eq=contrast=1.08:saturation=1.16:gamma=0.98"]
    visual_chain.extend(look_filters(CONFIG))
    if CONFIG["cinematic"]["look"].get("letterbox"):
        visual_chain.append("drawbox=x=0:y=0:w=iw:h=ih*0.035:color=black:t=fill")
        visual_chain.append("drawbox=x=0:y=ih-ih*0.035:w=iw:h=ih*0.035:color=black:t=fill")
    if CONFIG["cinematic"]["text"].get("enabled", True):
        visual_chain.append(f"subtitles=filename='{subtitle_path}'")
    filters.append(f"[{last}]{','.join(visual_chain)}[base]")
    if CONFIG["cinematic"].get("character", {}).get("enabled", True):
        filters.append("[8:v]format=rgba,colorchannelmixer=aa=0.94[astronaut]")
        filters.append("[base][astronaut]overlay=x='W-w-95+18*sin(t*2)':y='H-h-300+22*sin(t*3)':"
                       "format=auto:shortest=1[vout]")
    else:
        filters.append("[base]copy[vout]")
    char_input = ["-framerate", str(CONFIG["cinematic"].get("character", {}).get("fps", 12)),
                  "-stream_loop", "-1", "-i", str(character_dir / "character_%03d.png")]
    render_suffix = OUTPUT_SUFFIX + ("_preview" if PREVIEW else "")
    ambient_dir = ROOT / "output" / f"{TODAY}{render_suffix}_ambient"
    ambient_input = ["-framerate", "12", "-stream_loop", "-1", "-i",
                     str(ambient_dir / "ambient_%03d.png")]
    music_dir = ROOT / CONFIG["assets"]["music_dir"]
    music_files = sorted(
        path for path in music_dir.glob("*")
        if path.suffix.lower() in {".mp3", ".wav", ".m4a", ".aac"}
    ) if music_dir.exists() else []
    filters.append("[9:v]format=rgba,colorchannelmixer=aa=0.45[ambient]")
    filters.append("[vout][ambient]overlay=0:0:format=auto:shortest=1[vfinal]")
    audio_index = 10
    audio_filters = f"[{audio_index}:a]{voice_filter(CONFIG)}[voice]"
    if music_files and CONFIG["cinematic"]["audio"].get("duck_music", True):
        filters.append(audio_filters)
        filters.append(f"[11:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        audio_input = ["-i", str(AUDIO), "-stream_loop", "-1", "-i", str(music_files[0])]
        log(f"MUSIC MIX {music_files[0]}")
    else:
        filters.append(f"[{audio_index}:a]{voice_filter(CONFIG)}[aout]")
        audio_input = ["-i", str(AUDIO)]
    cmd = [ffmpeg, "-y", *inputs, *char_input, *ambient_input, *audio_input, "-filter_complex", ";".join(filters),
           "-map", "[vfinal]", "-map", "[aout]", "-t", f"{effective_duration:.3f}",
           "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
           "-b:a", "128k", "-shortest", str(OUT)]
    subprocess.run(cmd, check=True)


def ass_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"0:{minutes:02d}:{remainder:05.2f}"


def quality_check() -> dict:
    ffmpeg = ffmpeg_path()
    result = subprocess.run([ffmpeg, "-i", str(OUT)], capture_output=True, text=True)
    line = next((x for x in result.stderr.splitlines() if "Video:" in x), "")
    duration_line = next((x for x in result.stderr.splitlines() if "Duration:" in x), "")
    expected = f"{480 if PREVIEW else OUTPUT_WIDTH}x{(
        int((480 if PREVIEW else OUTPUT_WIDTH) * OUTPUT_HEIGHT / OUTPUT_WIDTH) // 2 * 2
    ) if PREVIEW else OUTPUT_HEIGHT}"
    duration_text = duration_line.split("Duration:", 1)[-1].split(",", 1)[0].strip()
    hours, minutes, seconds = duration_text.split(":") if duration_text else ("0", "0", "0")
    actual_duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(OUT), "-map", "0:v:0", "-f", "null", "-"],
        capture_output=True, text=True
    )
    max_duration = 10.5 if PREVIEW else 59.0
    ok = (
        OUT.exists() and expected in line and "Audio:" in result.stderr
        and 0 < actual_duration <= max_duration
        and decode.returncode == 0 and not decode.stderr.strip()
    )
    return {
        "ok": ok, "video": line.strip(), "duration": duration_line.strip(),
        "seconds": actual_duration, "decode_errors": decode.stderr.strip(),
    }


def main() -> None:
    global CONFIG, PREVIEW, ACTIVE_TOPIC, OUT, AUDIO, WORDS, SCENES
    global OUTPUT_SUFFIX, OUTPUT_WIDTH, OUTPUT_HEIGHT, TODAY
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="What happens if you fall into a black hole")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--format", choices=("9:16", "16:9"), default="9:16")
    parser.add_argument("--style", choices=("painterly_warm", "rainy_night", "snowy_dusk"),
                        default=None)
    args = parser.parse_args()
    PREVIEW = args.preview
    OUTPUT_WIDTH, OUTPUT_HEIGHT = (1920, 1080) if args.format == "16:9" else (1080, 1920)
    OUTPUT_SUFFIX = "_169" if args.format == "16:9" else ""
    ACTIVE_TOPIC = args.topic
    CONFIG = load_config(ROOT)
    if args.style:
        CONFIG["cinematic"]["style"] = args.style
    if args.topic == "What happens if you fall into a black hole":
        selected = topic_content(args.topic)
    else:
        selected = topic_content(args.topic)
    global CATEGORY, TOPIC, SCRIPT, cards, TITLE, DESCRIPTION, TAGS
    CATEGORY, TOPIC, SCRIPT, *rest = selected
    cards = rest[:6]
    TITLE, DESCRIPTION, TAGS = rest[6:]
    suffix = OUTPUT_SUFFIX + ("_preview" if PREVIEW else "")
    OUT = ROOT / "output" / f"{TODAY}{suffix}.mp4"
    AUDIO = ROOT / "output" / f"{TODAY}{suffix}.mp3"
    WORDS = ROOT / "output" / f"{TODAY}{suffix}_words.json"
    SCENES = ROOT / "output" / f"{TODAY}{suffix}_scenes"
    history_path = ROOT / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8-sig"))
    if any(item.get("topic") == TOPIC for item in history) and os.environ.get("SHORTS_ALLOW_REPEAT") != "1":
        raise RuntimeError(f"Topic already used: {TOPIC}")
    log(f"START {TODAY} category={CATEGORY} topic={TOPIC}")
    asyncio.run(make_voiceover())
    duration = get_audio_duration()
    words = caption_words(duration)
    WORDS.write_text(json.dumps(words, indent=2), encoding="utf-8")
    character_dir = ROOT / "output" / f"{TODAY}{suffix}_character"
    if CONFIG.get("cinematic", {}).get("renderer", "remotion") == "remotion":
        # Remotion supplies its own animated backgrounds and graphics.
        render(duration, words, character_dir)
    else:
        make_cards()
        character_cfg = CONFIG["cinematic"].get("character", {})
        if character_cfg.get("enabled", True):
            color = tuple(int(character_cfg.get("color", "#EDE6D0")[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
            make_frames(character_dir, character_cfg.get("pose", "sitting"), color,
                        fps=character_cfg.get("fps", 12))
        else:
            make_character_frames()
        ambient_dir = ROOT / "output" / f"{TODAY}{suffix}_ambient"
        if CONFIG["cinematic"].get("ambient", {}).get("enabled", True):
            make_ambient_frames(ambient_dir, WIDTH, HEIGHT, CONFIG["cinematic"]["style"])
        render(duration, words, character_dir)
    if CONFIG["cinematic"]["extras"].get("srt"):
        write_srt(ROOT / "output" / f"{TODAY}{suffix}.srt", words)
    if CONFIG["cinematic"]["extras"].get("thumbnails"):
        make_thumbnails(SCENES, ROOT / "output" / f"{TODAY}{suffix}_thumbnails", TITLE)
    assets_log = ROOT / "assets_log.csv"
    new_file = not assets_log.exists()
    with assets_log.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["date", "asset", "source", "license"])
        writer.writerow([TODAY, f"painterly backgrounds ({CONFIG['cinematic']['style']})",
                         "Pillow procedural artwork", "original/local"])
        writer.writerow([TODAY, "ambient particle overlays", "Pillow procedural artwork", "original/local"])
        writer.writerow([TODAY, f"character ({CONFIG['cinematic']['character'].get('type', 'skeleton')})",
                         "Pillow procedural artwork", "original/local"])
        writer.writerow([TODAY, "voiceover", "Microsoft Edge TTS", "service terms; no external media"])
    check = quality_check()
    log(f"QUALITY {json.dumps(check)}")
    if not check["ok"]:
        raise RuntimeError("Quality check failed")
    (ROOT / "output" / f"{TODAY}{suffix}_metadata.json").write_text(json.dumps({
        "date": TODAY, "category": CATEGORY, "topic": TOPIC, "title": TITLE,
        "description": DESCRIPTION, "tags": TAGS, "script": SCRIPT
    }, indent=2), encoding="utf-8")
    log(f"READY {OUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log(f"ERROR {type(exc).__name__}: {exc}")
        raise
