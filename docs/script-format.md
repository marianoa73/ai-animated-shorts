# Formato del guion

`episodes/<identificador>/script.json` es JSON estricto, sin comentarios. Creá un episodio con `bash src/new_episode.sh nombre`. El siguiente bloque es **JSONC explicativo**, no un archivo listo para ejecutar; el ejemplo completo del repo sí es JSON válido y tiene suficiente texto.

```jsonc
{
  "title": "Título propio",             // metadatos de revisión
  "scenario": "studio",                 // studio, night o garden
  "language": "es",                     // soportado por Chatterbox y Whisper
  "characters": ["example-a", "example-b"], // nombres de fichas, exactamente dos
  "width": 720, "height": 1280, "fps": 30,
  "subtitles": false,                   // true imprime text en el cuadro
  "music": true,                        // false o ruta relativa de audio propio
  "pause": 0.15,                        // segundos, máximo 0.3 entre líneas
  "lines": [
    {"who": "example-a", "text": "Texto que se ve.", "say": "Texto que se pronuncia.",
     "shot": "medium", "face": "neutral", "transition": "cut", "seed": 1},
    {"who": "example-b", "text": "Texto de cierre.", "shot": "closing"}
  ]
}
```

Los dos nombres deben tener fichas de voz y personaje. Identificadores: letras minúsculas ASCII, números y guiones. Las líneas alternan hablantes; usar una idea por línea y evitar monólogos largos. El validador admite hasta 500 caracteres por intervención y 200 líneas por episodio para acotar errores y memoria.

`shot`: `close` primer plano, `medium` plano medio, `orbit` órbita, `pan` paneo, `closing` conjunto final. La última línea siempre `closing`. `face`: `neutral`, `happy`, `sad`, `surprised`, `serious`. `transition`: `cut` o fundido breve `fade`. La expresividad es limitada por el rig simple.

`seed`: entero de 0 a 2147483647 (el reintento suma hasta 5; conviene no usar el extremo). `say` puede incluir `|` para separar frases: el sintetizador une fragmentos de menos de tres palabras para evitar tomas inestables. Esas barras no llegan a Whisper ni al subtítulo. Si no hay `say`, se usa `text` sin reemplazos de nombres particulares.

Planificá 13–15 caracteres por segundo hablado y más de 30 segundos. El validador usa 15 car/s como estimación, pero la duración real se mide después. Esta regla es propia del proyecto, no una condición general que asegure monetización o aceptación en redes.

El caché incluye texto pronunciado, semilla, configuración, versión de procesamiento y hash completo de la muestra. El índice mantiene una entrada **por número de línea**, de modo que dos textos iguales con semillas diferentes no se pisan. Cambiar subtítulos invalida el informe del guion, pero no obliga a sintetizar de nuevo audio idéntico.
