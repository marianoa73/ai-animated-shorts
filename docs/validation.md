# Validación de entrega 0.1.0

| Prueba | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -v` | 56 pruebas, OK; también con `python3 -S` sin site-packages, modelos ni internet |
| `python3 -m compileall -q src tests docs/assets/gen_diagrams.py` | OK, sin errores |
| `bash -n src/preflight.sh src/new_episode.sh tests/test_preflight.sh` | OK |
| `bash tests/test_preflight.sh` | 4 casos simulados, OK |
| `tests/render_smoke.cjs` con Bun y Chromium local | 8 controles, OK; cinco planos y subtítulos off/on |
| `tests/browser_review.cjs` con Bun y Chromium local | 20 controles, OK; móvil/PC, estados, texto literal y diagramas claro/oscuro |
| `tests/media_smoke.py` con Bun, Chromium y FFmpeg locales | OK; render sintético completo, 999 cuadros, 30 fps, H.264/AAC, >30 s, mezcla con ducking y whooshes |
| `python3 tests/audit_repo.py` | OK; privacidad, enlaces Markdown, JSON, SVG y entregables |
| Validación de la skill con quick_validate | `Skill is valid!` |
| Lectura YAML de Compose | OK; cuatro servicios, producción sin red y web sin entradas privadas |

Se revisaron visualmente capturas de los cinco planos, la web móvil y los diagramas sobre blanco y grafito. Las capturas y grabaciones sintéticas eran temporales y se retiraron; `docs/screenshots/` contiene cuatro cuadros y un GIF sin sonido agregados por el autor desde su serie.

No se ejecutó `docker compose config` ni build/arranque de imágenes: Docker no está disponible. No se instaló Node; se usó Bun para pruebas locales, sin afirmar equivalencia completa con la imagen objetivo. No se descargaron pesos ni se usaron grabaciones reales. El render sintético usa un informe de QA ficticio exclusivamente para comprobar los medios; no valida Chatterbox, Whisper ni identidad vocal.

El grep final solicitado sobre el repo completo no produjo coincidencias (salida vacía, código 1 de grep).

Los resultados no constituyen aprobación de un video real. Ver [limitaciones](limitations.md) y completar la integración x86_64 con muestras autorizadas.
