# Instalación y primera ejecución

## Prerrequisitos

Host Linux x86_64, Docker y Compose v2 con daemon accesible, ≥25 GiB de disco libre y ≥16 GiB de RAM recomendados (32 GiB preferibles). `src/preflight.sh` sólo consulta, no instala ni modifica servicios. Modelos, imágenes de Docker y caché pueden superar ese mínimo. Python 3.11 corre dentro de voice/qa; el render Noble usa el Python de la distribución para helpers. En el host, el coordinador necesita Python 3.11 o posterior.

```bash
bash src/preflight.sh
mkdir -p cache/tmp cache/models/chatterbox cache/models/whisper output
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose build voice qa render
```

También podés copiar `.env.example` a `.env` y ajustar esos dos números. No contiene tokens ni credenciales. No hagas commits de `.env`.

## Descargar pesos antes de aportar muestras

Las imágenes se construyen con internet. Descargá los modelos en una operación separada que **sólo monta la caché**, sin guiones, imágenes ni voces privadas. No se envían muestras: todavía no se aportaron. Estos comandos inicializan los modelos y pueden tardar y ocupar varios GB.

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HF_HOME=/models/chatterbox -e HF_HUB_DISABLE_TELEMETRY=1 -v "$PWD/cache/models:/models" ai-animated-shorts-voice:0.1.0 python -c 'from chatterbox.mtl_tts import ChatterboxMultilingualTTS; ChatterboxMultilingualTTS.from_pretrained(device="cpu")'
docker run --rm --user "$(id -u):$(id -g)" -e HF_HUB_DISABLE_TELEMETRY=1 -v "$PWD/cache/models:/models" ai-animated-shorts-qa:0.1.0 python -c 'from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8", download_root="/models/whisper")'
```

Después, Compose impone `network_mode: none` en voice, qa y render, más el modo offline de Hugging Face. Si faltan pesos, fallará: no habilites la red con muestras montadas para resolverlo; repetí la descarga aislada. El idioma del guion y de las dos voces debe coincidir y estar soportado por ambos modelos.

Piper es sólo un respaldo diagnóstico. No trae voces: descargá por separado un modelo ONNX con licencia compatible y su `.onnx.json` a `cache/piper/`; indicá el `.onnx` en `piper_model`. Sin clon ni modelo de respaldo el render falla con explicación. Con Piper se puede producir un diagnóstico, pero **no aprobarlo**.

## Materiales y episodio

Seguí [feeding.md](feeding.md). Sin muestras e imágenes propias validadas, el pipeline no sigue.

```bash
docker compose run --rm voice python src/check_inputs.py episodes/example
docker compose run --rm voice python src/voice_test.py example-a --other example-b
docker compose run --rm render node src/render/render.js episodes/example --preview
# Tras revisar el cuadro y confirmar el tiempo de render:
python3 src/pipeline.py episodes/example --confirm-render
```

El coordinador ejecuta voz → QA → hasta cinco reintentos por línea fallida → render → QA final. No ejecutarlo en paralelo sobre el mismo episodio. Detiene el proceso al agotar intentos: corregí `say`, escuchá y repetí. Las líneas buenas mantienen su caché. No copies un informe de QA entre episodios.

### Ejecutar etapas por separado

```bash
docker compose run --rm voice python src/voice.py episodes/example
docker compose run --rm qa python src/qa_audio.py lines episodes/example
docker compose run --rm render node src/render/render.js episodes/example
docker compose run --rm qa python src/qa_audio.py video episodes/example
```

Antes del render largo separado también pedí confirmación a quien opera. El renderer verifica hashes y el control por línea vigente; el render no implica aprobación.

## Revisar y cambiar estado

```bash
docker compose up -d web
# Navegador: http://localhost:8080
python3 src/status.py example pruebas
# Sólo después de escuchar y revisar los cuatro cuadros:
python3 src/status.py example aprobados --visual-reviewed
python3 src/status.py example produccion --visual-reviewed
```

`output/status.json` persiste estados asociados al hash del video. Un nuevo render vuelve a Revisión. La web es de sólo lectura; sin backend para editar archivos desde el navegador. No expongas el puerto directamente a internet. El acceso remoto y el proxy HTTPS opcional se configuran por separado con autenticación; sólo se comparte `output/`, nunca la raíz del repo.

## Skill

```bash
mkdir -p ~/.claude/skills
cp -R skill/ai-animated-shorts ~/.claude/skills/
```

Indicá a Claude Code la raíz del repositorio al invocarla. La skill referencia los documentos dentro del repo: no copies únicamente el SKILL.md a otro proyecto sin el pipeline. No requiere claves cloud para sintetizar, aunque el asistente utilizado para guiar la instalación puede tener su propio servicio: no le adjuntes muestras ni fotos.

## Actualizaciones

Las versiones directas están fijadas; las bases y dependencias transitivas no tienen un lock completo. Reconstruí y corré las pruebas antes de actualizar. Guardá `docker image inspect` y `pip freeze` si necesitás reproducibilidad de un despliegue concreto. No se hizo build de contenedores durante esta entrega; ver [validación](limitations.md).
