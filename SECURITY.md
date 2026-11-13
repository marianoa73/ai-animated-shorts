# Seguridad y privacidad

No agregues al repo muestras de voz, fotografías, modelos, claves, tokens ni archivos de entorno reales. Los ejemplos usan nombres ficticios. Revisá `git status` y el contenido a publicar: `.gitignore` no elimina material ya versionado.

Los permisos de voz deben ser escritos; no se clona a terceros ni figuras públicas. Tratar muestras y embeddings como datos biométricos. Mantener también la caché, las copias de seguridad y el resultado generado bajo control del operador.

El renderer sirve sólo sus módulos desde loopback y nginx sólo monta salidas. Los contenedores de inferencia usan red deshabilitada. Los pesos se descargan sin montar muestras. No deshabilites estas barreras para resolver un error de instalación.

La interfaz no tiene autenticación: por defecto sólo escucha en localhost. Si se hace accesible desde la LAN, agregar control de acceso en un proxy y revisar qué videos se comparten. Nunca montar el repositorio completo en el servidor web.

Los guiones y configuraciones son archivos locales de confianza, no entradas de un servicio público. No ejecutar archivos obtenidos de terceros sin revisarlos. Evitar renders concurrentes sobre el mismo episodio.

Reportar vulnerabilidades por un canal privado acordado con el mantenedor. No adjuntar muestras, credenciales, datos biométricos ni logs con rutas privadas en issues públicos. Este repo no define un contacto ficticio ni hace reportes automáticos.
