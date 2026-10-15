# Remotion video composition

This folder contains an editable 9:16 Remotion composition for cinematic editorial-style Shorts.

## Run locally

Install Node.js (LTS), then from this directory install the dependencies used by your Remotion project and run the Remotion Studio entrypoint configured by your project. The repository currently tracks the composition source, but does not track a package.json/lockfile, so the project manifest must be created or restored before it can be rendered from a clean checkout.

The composition uses only React and Remotion core APIs. It does not require narration.wav or external stock assets.

## Dynamic content

Pass `title`, `scenes`, `accentColor` and `backgroundColor` props to `MyComponent`. Each scene has `kicker`, `headline`, `highlight`, `subtitle`, `accent` and `layout` fields. Supported layouts are `hero`, `steps`, `quote` and `stat`.

## Important

The main daily automation currently renders the production video through the Python/FFmpeg pipeline in `scripts/create_short.py`. This Remotion composition is not automatically used by that pipeline yet. Switching daily uploads to Remotion requires adding a renderer/Node manifest and wiring generated topic, narration and caption data into a Remotion render step, followed by the existing video validation and uploader.
