# AI Animated Shorts

> *Local, configurable 3D dialogue production — from script to human review.*

**Two characters, your own voices and a reproducible procedure to produce animated shorts without cloud inference.**

[Versión en español](README.es.md) · Author: Mariano Araujo · MIT License

## In one minute

1. **Problem:** a synthetic voice can skip words, rush the ending or leave silences; rendering before checking it wastes time.
2. **Decision:** separate script, voice, per-line check, render and approval. Only the failed lines are regenerated.
3. **What it includes:** configurable block-style characters, Chatterbox voices, Whisper checks, three.js rendering, mixing, a local review page and an installation skill.
4. **How to verify the logic without models or internet:**
   ```bash
   python3 -m unittest discover -s tests -v
   bash tests/test_preflight.sh
   ```

![From script to review](docs/assets/01-flujo.svg)

[High-resolution PNG](docs/assets/01-flujo.png) · Diagrams are in Spanish; each one is described in the text around it.

## What it looks like

**Silent** frames and animation from the author's own series produced with this procedure: block-style characters,
vertical 720x1280 framing, burned-in subtitles off (social platforms add their own). The series characters have their
own design; the ones in this repository are neutral examples that everyone replaces with their own.

![Silent animation: a dialogue between the human and the AI](docs/screenshots/demo.gif)

| Human | Medium shot | AI | Closing |
|---|---|---|---|
| ![Close-up of the human](docs/screenshots/01-humano.png) | ![Medium shot of the human](docs/screenshots/02-humano-plano-medio.png) | ![Close-up of the AI](docs/screenshots/03-ia.png) | ![Closing shot from behind the characters](docs/screenshots/04-cierre.png) |

## First: provide your own materials

This repository **does not include photos, voice samples or cloned voices**. You need:

- Your own voice, or a voice with written consent: mono PCM16 WAV, 24 or 44.1 kHz, 10–30 seconds, no music or echo. Save it as `voices/samples/<character>.wav`.
- Images you own or have a license for: front and three-quarter views, plain background, at least 1024 px per side, in `characters/refs/`.
- Two profiles in `voices/` and two in `characters/`; the examples are neutral designs, not real people.

Voice samples are biometric data: **do not upload them to repositories, clouds or external services**. Those folders are ignored by Git. Read [how to record, convert, test and tune](docs/feeding.en.md) before generating anything.

## Minimal walkthrough

From the repository root, after [installing and downloading the models](docs/install.en.md):

```bash
bash src/preflight.sh
docker compose run --rm voice python src/check_inputs.py episodes/example
docker compose run --rm render node src/render/render.js episodes/example --preview
# Check output/example-preview.png and confirm the long render before continuing.
python3 src/pipeline.py episodes/example --confirm-render
docker compose up -d web
```

Open `http://localhost:8080`. It is an example port bound to loopback only, not a public service. The pipeline stops if a line still fails after five retries; change `say` and run it again. It never publishes to social platforms.

## What happens at each stage

| Stage | Implementation | Result |
|---|---|---|
| Script | `episodes/<name>/script.json` | Text, optional pronunciation, shots and gestures |
| Voices | `src/voice.py` | One WAV per hash + a per-line index, not per repeated text |
| Check | `src/qa_audio.py`, `src/pipeline.py` | Words, last word, signal, silences and seeds |
| Characters | `src/character_from_image.py`, `characters/` | Adjustable palette proposal, proportions and features |
| Render | `src/render/` | 720×1280 by default, 30 fps, mouth driven by volume |
| Mix | `src/music.py` and render | Procedural music, ducking, whoosh, −15 LUFS |
| Final check | `src/qa_audio.py video` | Alignment, gaps, duration, volume and four frames |
| Review | `web/`, `src/status.py` | Review / Tests / Approved / Production |

Burned-in subtitles are **off by default**. `"subtitles": true` turns them on; otherwise the video stays clean for the chosen platform's own captions.

## Hardware and timing

Intel i5 mini PC with four cores and 32 GB, Ubuntu 24.04, Docker, no GPU. A Raspberry Pi 4B with 8 GB and Debian can serve **only the review output**; it does not synthesize or render.

Measurements from the reference project on an **i5-10210U, eight threads, 32 GB**: a 66 s video ≈ 19–31 min of rendering; a 40 s video ≈ 19 min; voice ≈ 20–35 s per line; MP4 ≈ 250 MB. They are not benchmarks of this implementation nor guarantees of size or performance.

![Hardware and privacy](docs/assets/03-hardware-red.svg)

## Assisted installation

Copy `skill/ai-animated-shorts/` to `~/.claude/skills/ai-animated-shorts/` and ask Claude Code to use it, pointing to the repository root. The skill asks for your own samples and for confirmation before each long render. It never sends samples to any service. [Full installation guide](docs/install.en.md).

## Scope and limits

The code works for any pair of characters and any script that fits its schema. The profiles produce a basic block rig; the image proposes colors and **does not automatically rebuild a faithful 3D model**. There are three scenes (`studio`, `night`, `garden`) and five shots; new scenes are added by extending `scene.js`.

Chatterbox and Whisper must support the chosen language. Character rates and word segmentation need tuning for languages without spaces; the check does not certify intelligibility or human pronunciation. Voices, images and music require your own rights.

Installation downloads packages and weights once; production runs with networking disabled in the `voice`, `qa` and `render` containers. Do not confuse local production with an offline installation. No weights are shipped. A final human review is still required.

Guides in English: [Installation](docs/install.en.md) · [Feeding your materials](docs/feeding.en.md)

Reference documents (Spanish): [Architecture](docs/architecture.md) · [Script format](docs/script-format.md) · [Quality control](docs/quality-control.md) · [Hardware](docs/hardware.md) · [Decisions](docs/decisions.md) · [Limits and validation](docs/limitations.md) · [Third-party licenses](NOTICE.md)
