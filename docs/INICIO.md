# Empieza aquí

## Qué estamos construyendo

Un proyecto de investigación para aplicar la reducción de Veliz-Cuba a redes
booleanas biológicas y estudiar cómo cambia su estructura. Queremos saber tanto
cuánto se reducen como qué clases de funciones quedan y qué podemos deducir sobre
sus puntos fijos.

## Qué hemos hecho hasta ahora

1. **Revisión inicial del método.** Consultamos la referencia de 2011 y el preprint
   del autor. Implementamos la eliminación de nodos sin autorregulación mediante
   sustitución de su función en las restantes y simplificación exacta.
2. **Implementación propia en Python.** Separamos representación de funciones,
   importación, reducción, métricas y cálculo de puntos fijos en módulos pequeños.
   No usamos el programa BNReduction del autor como motor.
3. **Cinco redes reales.** Descargamos cinco modelos de origen Cell Collective a
   través de la colección curada BBM. Guardamos reglas, SBML, metadatos, referencias,
   modificaciones declaradas y huellas digitales para identificar los archivos.
4. **Tratamiento explícito de entradas.** Se conservan como parámetros constantes
   libres. Los resultados cuentan todas sus asignaciones, con desglose en los JSON.
5. **Cuatro políticas de eliminación.** Primer candidato, mínimo grado, mínimo
   tamaño tabular tras eliminar y selección aleatoria con semilla fija.
6. **Caracterización antes/después.** Nodos, aristas funcionales, autorregulaciones,
   componentes conexas, grado máximo y clases lógicas. También medimos el tamaño
   de las tablas y de una forma lógica canónica, y los tiempos de ejecución.
7. **Reconstrucción.** Guardamos la función de cada nodo eliminado para recuperar
   los puntos fijos de la red original desde los de la red reducida.
8. **Validación.** Diez pruebas que incluyen todas las 256 redes posibles de dos
   nodos, 100 redes aleatorias de cuatro nodos y el piloto real. Comparamos los
   conjuntos completos de puntos fijos, no únicamente su número.
9. **Resultados reproducibles.** El piloto genera 20 experimentos: cinco modelos
   por cuatro estrategias. Se conservan tablas resumen, reglas reducidas y trazas.
10. **Protocolo escrito.** Documentamos las definiciones, las limitaciones y las
    próximas fases para evitar confundir resultados preliminares con conclusiones.

## Primer resultado del piloto

Esta tabla usa mínimo grado. Los nodos incluyen las entradas protegidas.

| Modelo | Entradas | Nodos antes → después | Puntos fijos conservados |
|---|---:|---:|---:|
| Cortical Area Development | 0 | 5 → 1 | 2 |
| Gut Microbiome | 4 | 12 → 8 | 40 |
| Mammalian Cell Cycle 2006 | 1 | 10 → 6 | 1 |
| Toll Pathway of Drosophila | 2 | 11 → 2 | 4 |
| Cell Cycle Transcription | 0 | 9 → 0 | 1 |

En la última red, elegir siempre el primer candidato deja tres nodos; las otras
estrategias ensayadas llegan a cero. Todas conservan el mismo punto fijo.
Una red reducida vacía tiene un único estado y permite reconstruir ese punto fijo.

## Qué falta

- Comprobar exportaciones directas de Cell Collective e importar SBML-qual.
- Escalar a todo el corpus. El motor actual es una referencia exacta para redes
  pequeñas: admite hasta 16 variables por tabla local y 20 nodos para enumeración.
- Más experimentos, semillas y análisis estadístico.
- Formalizar las clases y los teoremas que queremos aplicar al trabajo científico.

Todavía no tenemos una aplicación gráfica ni un notebook de análisis. Tenemos
un paquete de código, datos y experimentos ejecutables. El catálogo completo no
está descargado ni analizado. La garantía comprobada es sobre puntos fijos;
no garantiza conservar todos los ciclos o las trayectorias temporales.

## Dónde mirar

Todos estos enlaces funcionan al navegar por el repositorio en GitHub:

| Quiero… | Abrir |
|---|---|
| Ver la descripción general y los comandos | [README](../README.md) |
| Entender la metodología | [Protocolo](protocolo.md) |
| Ver el algoritmo de reducción | [reduction.py](../src/ccreduce/reduction.py) |
| Entender cómo se guardan las funciones | [boolean.py](../src/ccreduce/boolean.py) |
| Ver la clasificación y las métricas | [metrics.py](../src/ccreduce/metrics.py) |
| Ver la comprobación de puntos fijos | [fixed_points.py](../src/ccreduce/fixed_points.py) |
| Ver los resultados en tabla | [summary.csv](../results/pilot/summary.csv) |
| Ver las fuentes exactas de los modelos | [manifest.json](../data/raw/manifest.json) |
| Ver las pruebas | [test_reduction.py](../tests/test_reduction.py) |

## Codex, Git y GitHub: tres piezas

- **La carpeta local** contiene los archivos reales del proyecto en tu ordenador.
  Esta conversación trabaja sobre esa carpeta. Un archivo editado queda guardado
  aunque aún no lo hayamos enviado a GitHub.
- **Git** guarda versiones identificables. Un *commit* es una instantánea de
  cambios con un mensaje y un identificador; permite consultar la evolución.
- **GitHub** aloja una copia del repositorio y de su historial en tu cuenta.
  Un *push* envía allí los commits locales. No se sincroniza cada edición por sí sola.
- **Codex** nos permite conversar sobre el proyecto, abrir archivos, modificarlos,
  ejecutar pruebas y revisar diferencias entre versiones.

## Cómo abrirlo desde aquí

Puedes pulsar los enlaces a archivos que te doy en la conversación. También puedes
pedirme «abre el algoritmo de reducción» o «muéstrame el resumen de resultados»
para que lo abra en un panel. Para revisar cambios, Codex dispone de un panel de
revisión y del comando `/review` en proyectos Git.

En GitHub, entra en el repositorio: el README aparece en la página principal.
Pulsa `src`, después `ccreduce` y el archivo que quieras leer. La carpeta `docs`
contiene estas guías; `results/pilot` contiene las salidas del experimento.

La [documentación oficial de revisión](https://learn.chatgpt.com/docs/code-review?surface=app)
explica los paneles de cambios, preparación y commits.

## Cómo ejecutarlo

Podemos hacerlo desde esta conversación: «ejecuta las pruebas» o «repite el piloto».
Si quieres hacerlo tú, abre un terminal en la carpeta del proyecto y ejecuta:

```powershell
python -m unittest discover -s tests -v
python experiments/run_pilot.py
```

El primer comando comprueba el programa. El segundo vuelve a generar las salidas
de `results/pilot`; sus tiempos cambiarán ligeramente en cada ejecución.

## Forma de trabajar a partir de ahora

1. Decidimos una mejora concreta y sus criterios científicos.
2. Modificamos los archivos y ejecutamos las comprobaciones relevantes.
3. Revisamos el cambio y sus resultados.
4. Guardamos una versión con un commit y la enviamos a GitHub cuando corresponda.

La taxonomía normativa está en [`taxonomia.md`](taxonomia.md), y el método y la
procedencia del censo en [`metodo_censo.md`](metodo_censo.md).

No necesitas aprender todos los comandos para empezar. Puedes pedir las acciones
con lenguaje normal; conviene distinguir «guardar los archivos», «guardar una
versión» y «subir esa versión a GitHub».
