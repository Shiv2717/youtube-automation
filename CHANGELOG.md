# Changelog

## 2026-10-09

- Added a toggleable `cinematic` configuration layer without removing the
  existing Pillow, Edge TTS, FFmpeg, or YouTube upload flow.
- Added modular motion, transition, look, caption, audio, and extras modules.
- Added `--topic` and `--preview` CLI options.
- Added varied FFmpeg transitions, Ken Burns/parallax motion, teal-orange
  grading, letterbox bars, grain, normalization, SRT export, and three
  thumbnail variants.
- Added `assets_log.csv` entries for generated assets and voiceover.
- Kept `daily_run.py` on the weekday topic rotation by passing its topic
  explicitly.

## 2026-10-10

- Added the `painterly_warm`, `rainy_night`, and `snowy_dusk` style presets.
- Added original Pillow-generated painterly backgrounds, ambient loop overlays,
  and a configurable cream skeleton character animated on twos at 12 fps.
- Added `--format 9:16|16:9`, `--style`, and a 10-second 480px preview mode.
- Changed the painterly preset to slow crossfades, minimal hook/payoff text,
  gentle motion, -16 LUFS normalization, SRT export, and warm thumbnails.

## 2026-10-15

- Added stricter FFmpeg decode, duration, audio, aspect-ratio, and metadata
  validation before a video can be uploaded.
- Added duplicate-publication protection keyed by date and topic.
- Added one retry for transient scheduled-upload failures.
- Added focused pipeline tests for dimensions, metadata, and Python compilation.
- Added atomic Edge TTS output with a retry and upgraded the minimum Edge TTS
  version to 7.3.1 after the service returned HTTP 403 during validation.
## Reference-style animation pass

- Matched the supplied reference's 9:16 painterly skeleton language with dark
  painted scene bases, original shelf/loaf details, cream articulated bones,
  scene-pose animation, and a 12 fps output cadence.
- Removed procedural scene-prompt text from generated artwork.
- Kept the reference treatment original: no frames, characters, or artwork from
  the supplied video are reused.
