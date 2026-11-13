# Alcance de validación y límites

[Comandos y resultados de entrega](validation.md)

## Pruebas realizadas en esta entrega

- Núcleo Python probado con Python 3.13: partición y regresión de última frase corta, hash de caché, selección de reintentos, señal sintética, LCS, timestamps, validación de entradas y esquema.
- Preflight probado con comandos simulados: camino exitoso y fallas de CPU, disco y Docker/Compose. No instala nada.
- Escena ejecutada con three.js 0.170 y Playwright 1.49 en Chromium local: cinco planos, ausencia de errores de página y subtítulos apagados/encendidos.
- Página revisada en 390 y 1280 px con respuestas HTTP simuladas: estado inicial, filtro de Aprobados, texto literal y ausencia de desborde horizontal.
- Cinco diagramas SVG y PNG generados y revisados sobre blanco y grafito; capturas de evidencia temporales no forman parte del material público. `docs/screenshots/` trae cuadros y un GIF sin sonido de la serie del autor; no incluye audio.
- Smoke de medios opt-in: tono sintético, render pequeño completo, mezcla y codificación reales; no valida identidad de voz ni inteligibilidad.

El ambiente de revisión tiene CPU ARM, Bun como runtime JS y Chromium del sistema. **No tiene Docker ni Node instalado**, y no es el equipo x86_64 objetivo. No se construyeron ni arrancaron las imágenes de Compose. La versión exacta de Chromium difiere de la fijada en la imagen de Playwright. Los tests de navegador son evidencia parcial, no sustituyen la integración en destino.

## Pendiente antes de uso real

Construir las imágenes en x86_64, comprobar dependencias transitivas, descargar los modelos, aportar muestras autorizadas, validar el idioma, escuchar voces, renderizar un episodio y medir el control final. Fijar digest de imágenes y revisiones de pesos para reproducibilidad estricta. No se garantiza que una reconstrucción futura resuelva las mismas dependencias transitivas.

No se incluyeron muestras reales; Chatterbox y Whisper se simularon en las pruebas unitarias. No se ejecutó síntesis clonada ni transcripción con pesos reales durante la entrega. Las mediciones del README provienen del caso de referencia, no de este código.

## Limitaciones funcionales

- Rig simple de bloques, cinco planos y expresiones básicas. La imagen propone colores por zonas, no geometría ni semejanza garantizada. Tres cuartos se usa para revisión humana.
- La duración estimada por caracteres es orientativa; diferentes idiomas, voces y tempos cambian el resultado.
- La comparación difusa puede confundir palabras parecidas; números escritos de forma distinta requieren `say`. Los caracteres ideográficos/kana se comparan individualmente, sin segmentación lingüística completa.
- El validador de imágenes verifica cabecera y dimensiones; la extracción de paleta decodifica con Pillow. La calidad de encuadre, iluminación, consentimiento y parecido se verifica manualmente.
- El control extrae cuatro cuadros, pero no evalúa automáticamente su contenido ni detecta todas las fallas de animación.
- Loudnorm es de un paso; el control posterior decide si la medición quedó dentro del margen. Puede ser necesario ajustar mezcla y repetir.
- No hay base de datos, autenticación web, múltiples operadores ni exclusión de tareas concurrentes. Ejecutar un episodio a la vez.
- Los estados son decisiones locales. «Producción» no implica publicación ni cumplimiento de requisitos de una plataforma.
- Piper requiere modelo y licencia aportados por el operador; una toma Piper nunca aprueba QA.

Para repetir pruebas de navegador en un entorno con Node y dependencias instaladas: `node tests/render_smoke.cjs` y `node tests/browser_review.cjs`. Usar `CHROMIUM_PATH` sólo si se elige explícitamente un Chromium del sistema. `python3 tests/media_smoke.py` crea y elimina un episodio sintético; ejecutarlo únicamente sin otro trabajo concurrente. Es una prueba de integración de medios, no una aprobación de producción.
