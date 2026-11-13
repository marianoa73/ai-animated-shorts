# Decisiones de diseño

- Separar texto visible de pronunciación (`say`), sin reemplazos de nombres ni dependencia de una serie.
- Dos fichas neutras reemplazables; la geometría se comparte y la paleta/proporciones/rasgos se configuran.
- No copiar el rig específico de las referencias: necesitaba texturas y proporciones ligadas a una persona.
- Conservar la corrección de partición: extraer con `pop()` la última frase corta antes de concatenar a la anterior. Tiene prueba de regresión.
- Controlar el audio con tempo ya aplicado; no modificar silencios silenciosamente después de aprobarlo.
- Semillas y hashes por línea: repetir texto no pisa otra toma. Hasta cinco reintentos, luego intervención humana.
- Fallback Piper visible y no aprobable; es diagnóstico, no un cambio silencioso de identidad vocal.
- Subtítulos impresos opt-in; las plataformas pueden agregar sus propias traducciones.
- Compartir sólo salidas; contenedores de producción sin red. Descargar modelos en un paso aislado sin muestras.
- Mantener el sitio estático: cambios de estado mediante CLI local, sin API de escritura ni publicación.
- Mantener tests de lógica sin dependencias pesadas; modelos y capturas se prueban en capas separadas.
- La regla >30 s es del proyecto; los tiempos del caso original son referencia, no benchmark de esta entrega.
