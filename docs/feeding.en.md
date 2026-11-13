# Feeding the system with your own materials

[Versión en español](feeding.md)

## 1. Voices: origin and consent

Only use your own voice or the voice of someone who gave **written consent** to clone it and to use the result in these videos. Never clone third parties without permission, or public figures. Keep the permission outside the public repository; agree on scope, duration and possible revocation.

The sample and the embeddings derived from it are biometric data. Do not upload them to repositories, clouds, forms or external assistants. The generated voice can also identify the speaker: the permission must cover its distribution. `.gitignore` helps, but it does not remove files that were already committed.

### Recording

- One person, 10–30 seconds of continuous speech, in the character's natural tone.
- Quiet room, no music, echo or background voices; microphone at 15–20 cm.
- Mono 16-bit PCM WAV at 24 kHz or 44.1 kHz; target peak ≈ −6 dBFS, without clipping.
- Say varied sentences; avoid extreme whispering, effects and aggressive compression.
- Keep the raw recording inside `voices/samples/` too, never among public files.

```bash
mkdir -p voices/samples characters/refs
# Trim 20 s starting at second 2; convert without inventing a voice.
ffmpeg -i voices/samples/raw.wav -ss 2 -t 20 -ac 1 -ar 24000 -c:a pcm_s16le voices/samples/cut.wav
# Measure the peak; read max_volume in the output.
ffmpeg -i voices/samples/cut.wav -af volumedetect -f null -
# EXAMPLE: if max_volume is -12 dB, add 6 dB to reach -6 dB.
ffmpeg -i voices/samples/cut.wav -af volume=6dB -ac 1 -ar 24000 -c:a pcm_s16le voices/samples/example-a.wav
```

Compute the gain from your own measurement: do not apply 6 dB to every sample. Repeat for `example-b.wav`, listen to both and tune `voices/<character>.json`: `sample`, `language`, `exaggeration`, `cfg`, `temperature`, `tempo`, `phrase_pause`. The validator accepts peaks between −12 and −3 dBFS; that does not prove the absence of noise or echo.

### Three test sentences

After downloading the models and providing the images:

```bash
docker compose run --rm voice python src/check_inputs.py episodes/example
docker compose run --rm voice python src/voice_test.py example-a --other example-b --language es
# Swap the order to give two sentences to the second character.
docker compose run --rm voice python src/voice_test.py example-b --other example-a --language es
```

Each run creates three alternating sentences, synthesizes them and checks them with local Whisper; it exits with an error if anything fails. For another language, pass `--phrases "First translated sentence" "Second translated sentence" "Third translated sentence"` and the matching language code (for English, `--language en`). `episodes/voice-test/` is private and ignored. The WAV files are in `cache/audio/`; the index lets you find each one. Listen to them before moving on. This short check does not require the 30 s of a final episode.

## 2. Images and characters

Use images you own or have a sufficient license for; no trademarked characters. Front and three-quarter views of the full character, centered, plain background and good light. PNG/JPG, **both sides ≥ 1024 px**. Put them in:

```text
characters/refs/example-a-front.png
characters/refs/example-a-three-quarter.png
characters/refs/example-b-front.png
characters/refs/example-b-three-quarter.png
```

The front reference needs a small, even margin. The script samples proportional zones: hair at the top, face, torso, legs and shoes; a different framing produces wrong colors. The three-quarter view is for human comparison, not an input for geometric reconstruction.

```bash
docker compose run --rm render python3 src/character_from_image.py characters/refs/example-a-front.png characters/example-a-proposal.json --base characters/example-a.json
```

Open the proposal and fix the hex colors, `headSize`, `torsoWidth`, `torsoHeight`, `legHeight` and the `hair`, `beard`, `glasses` features. Update both reference paths. Replace the active profile only after reviewing it; the helper never overwrites existing files.

```bash
docker compose run --rm render node src/render/render.js episodes/example --preview
```

Inspect `output/example-preview.png`: silhouette, sizes, face and framing. This preview does not synthesize voice or render the whole video. The rigs are basic; they do not promise anatomical fidelity or a specific style from any photograph.

## 3. Music

`src/music.py` synthesizes a deterministic local instrumental track. It uses no third-party samples or APIs. Alternatively, put your own licensed file in `cache/music/` and set `music` to its relative path. `music: false` turns off music and whooshes; the final loudness normalization stays. Keep the license of external material outside the public files when it contains private data.

## 4. Script

```bash
bash src/new_episode.sh my-episode
```

Edit `episodes/my-episode/script.json` following the [annotated template](script-format.md) (Spanish). Short alternating lines, one idea per line and a final `closing` shot. `text` is the subtitle; `say` only changes pronunciation. Planning estimate: 13–15 characters per spoken second; the actual WAV and video decide the duration. The example exceeds the 30 s estimate.

## Checklist before publishing manually

- Per-line and final checks approved, with no Piper fallback or stale reports.
- Full listen and review of the four frames; no unreadable text, cuts or animation errors.
- Voice consent and image/music rights confirmed for the intended use.
- No personal data or secrets in the script, on screen, in file names or metadata.
- Final duration measured, correct framing and subtitles chosen on purpose.
- Review the content before exporting it; marking it as Production does not publish it.
