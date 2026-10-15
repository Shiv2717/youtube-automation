# Remotion cinematic renderer

This project renders the visual composition used by the daily Shorts automation.

## One-time setup

Install Node.js LTS, then run:

```bash
cd remotion-video
npm install
npm run studio
```

The Studio preview uses example data. The automation passes the real title, scene cards, narration audio and word timestamps to each render.

## Daily pipeline

From the repository root, the existing scheduled workflow remains:

```powershell
python scripts\daily_run.py
```

The default `config.yaml` renderer is `remotion`. To use the legacy FFmpeg renderer, set `cinematic.renderer: ffmpeg`.

Remotion output keeps the expected date-based output filename so the existing validation and YouTube uploader continue to work. The pipeline copies the generated narration into Remotion's public directory for the render and deletes that temporary copy afterwards.

## Dynamic scene schema

Pass `title`, `scenes`, `accentColor`, `backgroundColor`, `audioFile` and `captions` as input props. Each scene has `kicker`, `headline`, `highlight`, `subtitle`, `accent` and `layout`. Supported layouts are `hero`, `steps`, `quote` and `stat`.

The component is designed for portrait 9:16 Shorts and can also be rendered in 16:9 through the existing CLI flag. First render may take longer while Remotion bundles the React project.
