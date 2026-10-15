# Shorts Bot

The generator creates narrated Shorts locally, renders the visual layer with Remotion's animated editorial composition (or the legacy FFmpeg renderer), validates the final MP4, and uploads it through the existing YouTube Studio browser flow.

## One-time setup for the Remotion renderer

Install Node.js LTS, then run:

```powershell
cd remotion-video
npm install
npm run studio
cd ..
```

The default `cinematic.renderer` setting is `remotion`. Set it to `ffmpeg` in `config.yaml` to use the legacy renderer. The Remotion render consumes the same topic, generated narration, and word timestamps from the Python pipeline.

## Commands

From this folder:

```powershell
python scripts\create_short.py --topic "What happens if you fall into a black hole"
python scripts\create_short.py --topic "What happens if you fall into a black hole" --style painterly_warm
python scripts\create_short.py --topic "What happens if you fall into a black hole" --format 16:9
python scripts\create_short.py --topic "What happens if you fall into a black hole" --preview
python scripts\daily_run.py
```

`--preview` writes a fast 480px-wide, 10-second render as
`output\YYYY-MM-DD_preview.mp4`,
along with an SRT file, thumbnails, and metadata. The normal command preserves
the existing date-based output names and weekday rotation through `daily_run.py`.

Available styles are `painterly_warm`, `rainy_night`, and `snowy_dusk`.
The default character is an original cream skeleton animated on twos at 12 fps.
The default output is 9:16; `--format 16:9` writes a separate `_169` output.

## How to tune the look

Edit [config.yaml](config.yaml):

- `cinematic.renderer`: `remotion` (editorial motion design) or `ffmpeg` (legacy pipeline).
- `cinematic.style`: `painterly_warm`, `rainy_night`, or `snowy_dusk` (used by the legacy FFmpeg renderer).
- `cinematic.character.type`, `pose`, `color`, `fps`, `enabled`: character layer controls.
- `cinematic.ambient.enabled`, `rain`, `snow`, `dust`, `steam`, `embers`: loop overlays.
- `cinematic.motion.ken_burns` and `parallax`: gentle camera movement controls.
- `cinematic.transitions.sequence` and `duration`: keep the sequence at `fade`
  for slow dissolves; `duration` is normally 0.6-1.0 seconds.
- `cinematic.look.grade`: `painterly_warm` supplies golden highlights and teal shadows.
- `cinematic.look.vignette`, `film_grain`, `soft_bloom`: finish layers.
- `cinematic.text.font_size` and `keyword_highlight`: caption styling switches.
- `cinematic.audio.loudness`: target integrated loudness, default -16 LUFS.
- `cinematic.extras.thumbnails` and `srt`: optional deliverables.

All generated media is logged in `assets_log.csv`. Put only royalty-free music
or effects in `assets\music` and `assets\sfx`; the current render remains fully
self-generated when those folders are empty.

Before upload, the pipeline checks the encoded dimensions, audio stream,
duration, and FFmpeg decode result. The uploader also validates metadata and
skips a date/topic that already has a published URL in `history.json`. Scheduled
uploads retry once for transient browser failures. Run
`python -m unittest discover -s tests -v` after changes. The local repository
does not currently contain a GitHub Actions workflow; automation is configured
through Windows Task Scheduler.
### Reference-style painterly output

The Remotion renderer uses a cream editorial-paper palette, kinetic typography, scene-specific accent colors, animated visual motifs, word-timed captions, and the generated narration. The legacy `painterly_warm` renderer remains available if you prefer its dark hand-painted background and skeleton character. The supplied reference is used only as a style target: the
generated scenes and character remain original.
