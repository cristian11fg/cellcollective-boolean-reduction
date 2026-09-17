# cellcollective-boolean-reduction
Reproducible analysis of Boolean network reduction on biological models from Cell Collective, with structural characterization and fixed-point analysis.

# Reducción de redes booleanas de Cell Collective

Primera versión experimental en Python de los pasos S/R de Veliz-Cuba,
con caracterización antes/después y reconstrucción de puntos fijos.
El algoritmo de eliminación está implementado aquí, sin utilizar BNReduction.
El motor del piloto usa tablas de verdad sin dependencias; el motor del censo usa
`dd` para representar funciones y `z3-solver` para comprobar la conservación de puntos fijos.

## Censo y ejemplos para el artículo

- [Catálogo público directo de Cell Collective](docs/censo_live.md).
- [78 instancias archivadas en BBM](docs/censo_catalogue.md).
- [Definiciones, fuentes y límites del censo](docs/metodo_censo.md).
- [Funciones de los dos candidatos iniciales](docs/candidatos.md).

Cada informe enlaza la tabla completa, la clasificación local de cada función,
los conflictos de signo, las funciones reducidas y la traza de reconstrucción.

Para reproducir el censo (Python 3.11 o superior):

```powershell
python -m pip install -e ".[research]"
python scripts/fetch_catalogue.py
python scripts/probe_cellcollective.py
python scripts/fetch_live.py
python experiments/run_catalogue.py --dataset cellcollective --timeout 240
python experiments/run_catalogue.py --dataset live --timeout 240
python experiments/report_catalogue.py --dataset cellcollective
python experiments/report_catalogue.py --dataset live
python -m unittest discover -s tests -v
```

Los archivos ya descargados se reutilizan. Los resultados completos también se
reutilizan al reanudar; para un experimento nuevo con cambios del algoritmo hay
que guardar los resultados anteriores en otra carpeta antes de ejecutar de nuevo.

**Si es tu primera vez en este proyecto:** empieza por
[la guía de inicio y resumen](docs/INICIO.md). Explica qué hay hecho, dónde está
cada cosa y cómo trabajar desde Codex y GitHub.

## Ejecutar

Python 3.11 o superior; probado con Python 3.14 en Windows.
Desde esta carpeta, sin instalación de paquetes:

```powershell
python -m unittest discover -s tests -v
python experiments/run_pilot.py
```

Los cinco modelos del piloto ya están en `data/raw`. Para volver a descargarlos
desde la misma revisión y comprobar sus huellas:

```powershell
python scripts/fetch_pilot.py
```

## Qué contiene

- `src/ccreduce/boolean.py`: funciones booleanas exactas y dependencias esenciales.
- `src/ccreduce/parser.py`: lectura estricta de BNET, sin ejecutar expresiones arbitrarias.
- `src/ccreduce/reduction.py`: sustitución, simplificación y traza inversa.
- `src/ccreduce/metrics.py`: grafo funcional y clasificación lógica.
- `src/ccreduce/fixed_points.py`: enumeración exhaustiva y validación de la biyección.
- `experiments/run_pilot.py`: cuatro políticas y resultados reproducibles.
- `results/pilot/summary.csv`: comparación de los 20 experimentos.
- `results/pilot/*.json`: funciones, eliminaciones, puntos fijos originales,
  reducidos y reconstruidos, incluidos recuentos por asignación de entradas.
- `results/pilot/*.bnet`: reglas reducidas exportadas en DNF canónica.
- `docs/protocolo.md`: definiciones, límites e itinerario de investigación.

## Primeros resultados

Nodos totales **incluyen las entradas**, que se mantienen como parámetros libres.
Los puntos fijos se cuentan sobre todas las asignaciones de esas entradas.
La columna final muestra la reducción con `min_degree`.

| Modelo | Entradas | Nodos antes → después | Puntos fijos antes = después |
|---|---:|---:|---:|
| Cortical Area Development | 0 | 5 → 1 | 2 |
| Metabolic Interactions in Gut Microbiome | 4 | 12 → 8 | 40 |
| Mammalian Cell Cycle 2006 | 1 | 10 → 6 | 1 |
| Toll Pathway of Drosophila | 2 | 11 → 2 | 4 |
| Cell Cycle Transcription | 0 | 9 → 0 | 1 |

En Cell Cycle Transcription, `first` deja tres nodos; las otras tres políticas
ensayadas dejan cero. La traza permite reconstruir el único punto fijo también
desde la red vacía. Es una observación del piloto, no un resultado general.

## Procedencia y alcance

Los modelos se descargaron de **BBM**, filtrando sus metadatos por procedencia
Cell Collective. Se conservan las reglas BNET, SBML, metadatos, publicaciones y
notas de modificación de BBM. El manifiesto fija revisión, URL y SHA-256.
La selección toma los cinco primeros por el número de variables internas
declarado por BBM (no por el total con entradas), con desempate por directorio.
Es una muestra de conveniencia para validación, no una muestra representativa.

Esta versión procesa **BNET**. Los SBML se archivan, pero su importador y la
comprobación de equivalencia entre formatos quedan para la siguiente fase.
No se ha comprobado la equivalencia con una exportación actual directa de
Cell Collective. Tres modelos del piloto tienen modificaciones declaradas por BBM.

El motor de referencia utiliza tablas de verdad locales con máximo de 16
variables por operación; la enumeración de puntos fijos admite hasta 20 nodos.
Superar un límite genera un error, nunca un resultado de «cero puntos fijos»
ni de «red irreducible». No es todavía un motor para el catálogo completo.

## Fuentes

- Veliz-Cuba (2011), *Reduction of Boolean network models*, J. Theor. Biol.
  289:167–172, [DOI](https://doi.org/10.1016/j.jtbi.2011.08.042).
- [Preprint del autor](https://arxiv.org/abs/0907.0285), consultado para los
  algoritmos S/R, ejemplos 2.1–2.2 y correspondencia de estados estacionarios.
  Conviene cotejar la versión editorial antes de cerrar la metodología del artículo.
- [BBM](https://github.com/sybila/biodivine-boolean-models), colección curada
  y notas de normalización de entradas; cada carpeta conserva su cita biológica.
- [ccapi](https://github.com/cellcollective/ccapi), referencia para estudiar la
  futura adquisición directa. No forma parte del motor actual.

## Validación

Diez pruebas: ejemplos del preprint, constantes, red vacía, autorregulación,
entradas, dependencias aparentes, clasificación, componentes del grafo y límites.
Se comprueba la biyección en las 256 redes booleanas posibles de dos nodos,
100 redes aleatorias de cuatro nodos y los cinco modelos reales, con las cuatro
políticas. Se compara el conjunto completo reconstruido, no solo su cardinalidad.

Las métricas lógicas se refieren a la **función**, no al texto de la regla.
No se interpreta una reducción como preservación de ciclos, cuencas de atracción
o tiempos de respuesta. La garantía implementada se refiere a puntos fijos.

## Licencia

El código propio se distribuye bajo la [licencia MIT](LICENSE). Los modelos
importados de terceros conservan sus condiciones y atribuciones de origen;
la licencia del código no modifica las de esos datos.
