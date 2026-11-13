# Dependencias y licencias de terceros

MIT cubre el código propio de este repositorio, no convierte sus dependencias, modelos, voces o medios en MIT. No se redistribuyen aquí pesos, grabaciones, fotos ni binarios de terceros. Las instalaciones conservan sus avisos originales. Si se redistribuyen imágenes Docker o binarios, conservar licencias y cumplir las obligaciones correspondientes de código fuente.

| Componente / versión de referencia | Licencia y fuente oficial |
|---|---|
| three.js 0.170 | MIT — [LICENSE](https://github.com/mrdoob/three.js/blob/r170/LICENSE) |
| Playwright 1.49 | Apache-2.0 — [LICENSE](https://github.com/microsoft/playwright/blob/v1.49.1/LICENSE) |
| Chromium | BSD y múltiples componentes — [avisos](https://www.chromium.org/chromium-os/licenses/) |
| [Chatterbox 0.1.7](https://pypi.org/project/chatterbox-tts/0.1.7/) | MIT para el código — [LICENSE](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE); comprobar también [ficha de pesos](https://huggingface.co/ResembleAI/chatterbox) al descargarlos |
| faster-whisper 1.2 | MIT — [LICENSE](https://github.com/SYSTRAN/faster-whisper/blob/v1.2.0/LICENSE) |
| [CTranslate2 4.8](https://pypi.org/project/ctranslate2/4.8.0/) | MIT — [LICENSE](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE) |
| Whisper / pesos derivados | [licencia del proyecto](https://github.com/openai/whisper/blob/main/LICENSE), revisar ficha del checkpoint convertido |
| Piper 2023.11.14-2 | MIT para la implementación antigua usada — [release](https://github.com/rhasspy/piper/releases/tag/2023.11.14-2), [licencia](https://github.com/rhasspy/piper/blob/master/LICENSE.md). No extrapolar a forks/versiones nuevos |
| Voces Piper | Licencia por modelo y dataset: revisar `MODEL_CARD` — [catálogo](https://huggingface.co/rhasspy/piper-voices). No se incluye ninguna voz |
| FFmpeg 6.1 | LGPL-2.1+ o GPL según compilación; libx264 activa obligaciones GPL — [detalle oficial](https://ffmpeg.org/legal.html) |
| nginx 1.27 | BSD de dos cláusulas — [licencia](https://nginx.org/LICENSE) |
| PyTorch 2.6 y torchaudio | BSD-style y avisos de componentes — [PyTorch](https://github.com/pytorch/pytorch/blob/v2.6.0/LICENSE), [torchaudio](https://github.com/pytorch/audio/blob/v2.6.0/LICENSE) |
| Pillow | HPND — [licencia](https://github.com/python-pillow/Pillow/blob/main/LICENSE) |
| Node.js | MIT y componentes — [licencia](https://github.com/nodejs/node/blob/main/LICENSE) |

El binario Piper puede incorporar dependencias con obligaciones diferentes, entre ellas el motor fonético; revisar el paquete completo antes de redistribuir. Los derechos de una grabación o personaje son independientes de la licencia del software. No hay una autorización implícita para imitar identidades.

Las dependencias directas se fijan en Dockerfiles/package.json. Los parches de bases, pesos descargados y transitivas pueden cambiar: registrar versiones y avisos del despliegue concreto. [Requisitos de Chatterbox](https://github.com/resemble-ai/chatterbox/blob/master/pyproject.toml) y [faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/v1.2.0/requirements.txt) se consultaron como referencia; un branch móvil no es un lock.
