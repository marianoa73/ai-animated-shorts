# Installation and first run

[Versión en español](install.md)

## Prerequisites

Linux x86_64 host, Docker and Compose v2 with an accessible daemon, ≥ 25 GiB of free disk and ≥ 16 GiB of RAM recommended (32 GiB preferred). `src/preflight.sh` only checks; it does not install or modify services. Models, Docker images and cache can exceed that minimum. Python 3.11 runs inside voice/qa; the Noble render image uses the distribution's Python for helpers. On the host, the coordinator needs Python 3.11 or later.

```bash
bash src/preflight.sh
mkdir -p cache/tmp cache/models/chatterbox cache/models/whisper output
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose build voice qa render
```

You can also copy `.env.example` to `.env` and adjust those two numbers. It holds no tokens or credentials. Do not commit `.env`.

## Download weights before providing samples

Images are built with internet access. Download the models in a separate step that **mounts only the cache**, without scripts, images or private voices. No samples are sent: they have not been provided yet. These commands initialize the models and can take a while and use several GB.

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HF_HOME=/models/chatterbox -e HF_HUB_DISABLE_TELEMETRY=1 -v "$PWD/cache/models:/models" ai-animated-shorts-voice:0.1.0 python -c 'from chatterbox.mtl_tts import ChatterboxMultilingualTTS; ChatterboxMultilingualTTS.from_pretrained(device="cpu")'
docker run --rm --user "$(id -u):$(id -g)" -e HF_HUB_DISABLE_TELEMETRY=1 -v "$PWD/cache/models:/models" ai-animated-shorts-qa:0.1.0 python -c 'from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8", download_root="/models/whisper")'
```

From then on, Compose enforces `network_mode: none` on voice, qa and render, plus Hugging Face offline mode. If weights are missing it will fail: do not enable networking with samples mounted to fix it; repeat the isolated download. The script language and both voices must match and be supported by both models.

Piper is only a diagnostic fallback. It ships no voices: download a compatibly licensed ONNX model and its `.onnx.json` into `cache/piper/` and point `piper_model` to the `.onnx`. Without a clone or a fallback model the render fails with an explanation. With Piper you can produce a diagnostic video, but **never approve it**.

## Materials and episode

Follow [feeding.en.md](feeding.en.md). Without your own validated samples and images, the pipeline does not continue.

```bash
docker compose run --rm voice python src/check_inputs.py episodes/example
docker compose run --rm voice python src/voice_test.py example-a --other example-b
docker compose run --rm render node src/render/render.js episodes/example --preview
# After checking the frame and confirming the render time:
python3 src/pipeline.py episodes/example --confirm-render
```

The coordinator runs voice → QA → up to five retries per failed line → render → final QA. Do not run it in parallel on the same episode. It stops when retries run out: fix `say`, listen and repeat. Good lines keep their cache. Do not copy a QA report between episodes.

### Running stages separately

```bash
docker compose run --rm voice python src/voice.py episodes/example
docker compose run --rm qa python src/qa_audio.py lines episodes/example
docker compose run --rm render node src/render/render.js episodes/example
docker compose run --rm qa python src/qa_audio.py video episodes/example
```

Before a separate long render, also ask the operator for confirmation. The renderer checks hashes and the current per-line QA; rendering does not imply approval.

## Review and change status

```bash
docker compose up -d web
# Browser: http://localhost:8080
python3 src/status.py example pruebas
# Only after listening and reviewing the four frames:
python3 src/status.py example aprobados --visual-reviewed
python3 src/status.py example produccion --visual-reviewed
```

The status keys are Spanish: `revision` (Review), `pruebas` (Tests), `aprobados` (Approved), `produccion` (Production). `output/status.json` stores states tied to the video hash. A new render goes back to Review. The web page is read-only; there is no backend to edit files from the browser. Do not expose the port directly to the internet. Remote access and the optional HTTPS proxy are configured separately with authentication; only `output/` is shared, never the repository root.

## Skill

```bash
mkdir -p ~/.claude/skills
cp -R skill/ai-animated-shorts ~/.claude/skills/
```

Tell Claude Code the repository root when invoking it. The skill references the documents inside the repository: do not copy only the SKILL.md into another project without the pipeline. It needs no cloud keys to synthesize, although the assistant used to guide the installation may have its own service: never attach samples or photos to it.

## Updates

Direct versions are pinned; base images and transitive dependencies have no full lock. Rebuild and run the tests before updating. Keep `docker image inspect` and `pip freeze` output if you need reproducibility for a specific deployment. No containers were built during this delivery; see [validation](limitations.md) (Spanish).
