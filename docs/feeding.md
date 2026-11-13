# Alimentar el sistema con materiales propios

[English version](feeding.en.md)

## 1. Voces: origen y consentimiento

Sólo usá tu voz o la de alguien que dio **consentimiento por escrito** para clonarla y utilizar el resultado en estos videos. Nunca clones a terceros sin permiso ni a figuras públicas. Guardá el permiso fuera del repositorio público; acordá alcance, duración y posible revocación.

La muestra y los embeddings derivados son datos biométricos. No subirlos a repositorios, nubes, formularios ni asistentes externos. La voz generada también puede identificar al hablante: el permiso debe cubrir su difusión. `.gitignore` ayuda, pero no elimina archivos que ya estaban versionados.

### Grabación

- Una persona, 10–30 segundos de habla continua, tono natural del personaje.
- Ambiente silencioso, sin música, eco ni voces de fondo; micrófono a 15–20 cm.
- WAV mono PCM de 16 bits a 24 kHz o 44,1 kHz; pico objetivo ≈ −6 dBFS, sin saturar.
- Pronunciá frases variadas; evitá susurros extremos, efectos y compresión agresiva.
- Colocá también la grabación cruda dentro de `voices/samples/`, nunca entre archivos públicos.

```bash
mkdir -p voices/samples characters/refs
# Recortar 20 s desde el segundo 2; convertir sin inventar una voz.
ffmpeg -i voices/samples/raw.wav -ss 2 -t 20 -ac 1 -ar 24000 -c:a pcm_s16le voices/samples/cut.wav
# Medir el máximo; leer max_volume en la salida.
ffmpeg -i voices/samples/cut.wav -af volumedetect -f null -
# EJEMPLO: si max_volume es -12 dB, sumar 6 dB para obtener -6 dB.
ffmpeg -i voices/samples/cut.wav -af volume=6dB -ac 1 -ar 24000 -c:a pcm_s16le voices/samples/example-a.wav
```

Calculá la ganancia según la medición: no apliques 6 dB a cualquier muestra. Repetí para `example-b.wav`, escuchá ambas y ajustá `voices/<personaje>.json`: `sample`, `language`, `exaggeration`, `cfg`, `temperature`, `tempo`, `phrase_pause`. El validador admite picos entre −12 y −3 dBFS; eso no demuestra ausencia de ruido o eco.

### Tres frases de prueba

Después de descargar los modelos y aportar las imágenes:

```bash
docker compose run --rm voice python src/check_inputs.py episodes/example
docker compose run --rm voice python src/voice_test.py example-a --other example-b --language es
# Invertir el orden para dar dos frases al segundo personaje.
docker compose run --rm voice python src/voice_test.py example-b --other example-a --language es
```

Cada ejecución crea tres frases alternadas, sintetiza y controla con Whisper local; sale con error si falla. Para otro idioma, pasá `--phrases "Primera frase traducida" "Segunda frase traducida" "Tercera frase traducida"` y el código de idioma correspondiente. `episodes/voice-test/` es privado e ignorado. Los WAV están en `cache/audio/`; el índice permite localizar cada uno. Escuchalos antes de seguir. El control corto no exige los 30 s del episodio final.

## 2. Imágenes y personaje

Usá imágenes propias o con licencia suficiente; nada de personajes con marca registrada. Frente y tres cuartos del personaje completo, centrado, fondo liso y buena luz. PNG/JPG, **ambos lados ≥ 1024 px**. Ponelas en:

```text
characters/refs/example-a-front.png
characters/refs/example-a-three-quarter.png
characters/refs/example-b-front.png
characters/refs/example-b-three-quarter.png
```

La referencia de frente debe tener margen pequeño y uniforme. El script muestrea zonas proporcionales: cabello arriba, rostro, torso, piernas y zapatos; un encuadre distinto produce colores incorrectos. Tres cuartos sirve para la comparación humana, no como entrada de reconstrucción geométrica.

```bash
docker compose run --rm render python3 src/character_from_image.py characters/refs/example-a-front.png characters/example-a-proposal.json --base characters/example-a.json
```

Abrí la propuesta, corregí colores hexadecimales, `headSize`, `torsoWidth`, `torsoHeight`, `legHeight` y rasgos `hair`, `beard`, `glasses`. Actualizá ambos paths de referencias. Reemplazá la ficha activa sólo después de revisarla; el helper no sobrescribe archivos existentes.

```bash
docker compose run --rm render node src/render/render.js episodes/example --preview
```

Inspeccioná `output/example-preview.png`: silueta, tamaños, cara y encuadre. Esa previsualización no sintetiza voz ni renderiza el video entero. Los rigs son básicos; no prometen fidelidad anatómica ni un estilo específico a partir de cualquier fotografía.

## 3. Música

`src/music.py` sintetiza una base instrumental local determinista. No usa muestras ajenas ni API. Alternativamente, poné tu archivo con licencia en `cache/music/` y fijá `music` a su ruta relativa. `music: false` desactiva música y whooshes; la normalización final se mantiene. Conservá la licencia del material externo fuera del material público cuando contenga datos privados.

## 4. Guion

```bash
bash src/new_episode.sh mi-episodio
```

Editá `episodes/mi-episodio/script.json` siguiendo la [plantilla explicada](script-format.md). Líneas cortas alternadas, una idea por línea y plano final `closing`. `text` es el subtítulo; `say` sólo cambia pronunciación. Estimación de planificación: 13–15 caracteres por segundo hablado; el WAV y el video real deciden la duración. El ejemplo supera la estimación de 30 s.

## Checklist antes de publicar manualmente

- Control por línea y final aprobados, sin fallback Piper ni informes viejos.
- Escucha completa y revisión de los cuatro cuadros; sin texto ilegible, cortes o errores de animación.
- Consentimientos de voz y derechos de imagen/música confirmados para el uso previsto.
- Sin datos personales o secretos en guion, pantalla, nombres de archivos o metadatos.
- Duración final medida, encuadre correcto y subtítulos elegidos conscientemente.
- Revisar el contenido antes de exportarlo; marcar Producción no lo publica.
