---
name: ai-animated-shorts
description: Instalar y operar el pipeline CPU local de cortos 3D de dos personajes de este repositorio, desde materiales propios hasta revisión humana. Usar para preparar voces, personajes, guiones, controles y renders; no publica en redes.
---

# AI Animated Shorts

Pedí la raíz del repositorio si no está identificada. Trabajá desde ella; los paths siguientes son relativos al repo, no a la carpeta donde se instaló esta skill. Leé `docs/install.md` y `docs/feeding.md` antes de operar. No hace falta otra skill.

1. Ejecutá `bash src/preflight.sh`: Docker, Compose, daemon, x86_64 y ≥25 GiB libres; recomendación ≥16 GiB RAM. Si falla, explicá el requisito faltante. No instales paquetes globales ni modifiques servicios sin autorización.
2. Construí voice, qa y render siguiendo `docs/install.md`. Descargá modelos únicamente con los comandos de preparación que montan la caché, sin muestras. La producción mantiene los tres servicios sin red. Si faltan pesos, no habilites red con datos privados montados.
3. **Pedile a la persona sus propias muestras de voz y referencias de personajes.** No inventes que ya existen ni continúes con muestras ajenas. Voz propia o consentimiento escrito, nunca terceros sin permiso ni figuras públicas: 10–30 s, WAV mono PCM16, 24/44,1 kHz, pico ≈−6 dBFS, sin música/eco. Referencias propias o con licencia: frente y tres cuartos, PNG/JPG ≥1024 px por lado, fondo liso. Indicá que las coloque localmente en `voices/samples/` y `characters/refs/`, no que las adjunte al chat ni las suba a ningún sitio. Son datos biométricos privados; no leerlos ni enviarlos mediante herramientas remotas.
4. Configurá las dos fichas; ejecutá `docker compose run --rm voice python src/check_inputs.py episodes/example`. Si falta una muestra o referencia, **detenete y pedila**; no sustituyas ese paso con Piper. Para recortar/normalizar y generar tres frases controladas, usá los comandos de `docs/feeding.md`. La persona escucha las voces antes de continuar.
5. Proponé la paleta con `character_from_image.py` si se solicita, ajustá proporciones y previsualizá un cuadro. La extracción sólo propone colores; no representa una reconstrucción 3D fiel. Creá el episodio con `src/new_episode.sh`, validá el guion y el plano de cierre. Subtítulos impresos apagados salvo pedido explícito o `subtitles: true` existente.
6. **Pedí confirmación antes de cada render largo**, indicando episodio, duración estimada y tiempo CPU orientativo. Sólo después usá `python3 src/pipeline.py episodes/<nombre> --confirm-render`. La autorización para instalar no equivale a la autorización para renders posteriores.
7. No ignores fallas: QA exige texto y última palabra, cola, pico, silencios y ritmo. El coordinador permite cinco reintentos por línea; agotados, proponé ajustar `say` sin alterar el subtítulo. Piper siempre impide aprobar. No fuerces un resultado exitoso ni edites el reporte para pasar.
8. Revisá QA final, escuchá el video y pedí inspección humana de los cuatro cuadros. `src/status.py ... aprobados --visual-reviewed` sólo tras esa revisión y con QA vigente. Iniciá la página local con `docker compose up -d web`; `http://localhost:8080` es el ejemplo local. Estados Revisión / Pruebas / Aprobados / Producción, sin publicación automática.

Antes de cualquier publicación manual ajena a esta skill: confirmar derechos de voz, imagen y música, ausencia de datos personales y control vigente. Nunca hacer push, subir muestras, publicar ni exponer servicios por inferencia a partir del pedido de producir un corto.

Para instalar esta skill: copiar su carpeta a `~/.claude/skills/ai-animated-shorts/`; conservar el repositorio con su documentación y scripts en una ubicación local indicada por la persona.
