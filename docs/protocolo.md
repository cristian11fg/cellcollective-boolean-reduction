# Protocolo experimental — versión 0.1

## Pregunta y objetivos

¿Qué estructura funcional conservan las redes biológicas después de eliminar
variables sin autorregulación? ¿Qué fracción queda en clases de redes con
resultados analíticos aplicables a sus puntos fijos?

Separar tres objetivos: validar la implementación matemática, caracterizar el
corpus y contrastar hipótesis sobre clases tratables. El piloto cubre el primero
y empieza el segundo. La aplicación de teoremas específicos requiere fijar sus
hipótesis y definiciones con los trabajos concretos del grupo.

## Red y reducción

Una red contiene una función booleana por nodo. El soporte esencial de una
función contiene exactamente las variables para las que sus cofactores en 0 y 1
difieren. Las aristas se extraen de este soporte, nunca de simples apariciones
de nombres en el texto.

Si i no pertenece al soporte de f_i, para cada j distinto de i:

    g_j = f_j[x_i ← f_i].

Se elimina i y se simplifican las funciones. Se repite hasta que todos los
nodos no protegidos tengan autorregulación funcional. Para reconstruir un punto
fijo, se recorre la traza en sentido inverso y se asigna x_i = f_i al estado ya
reconstruido. Esta sustitución proporciona una extensión única.

Una red vacía tiene un estado, la tupla vacía, y un punto fijo. No significa
que desaparezca el punto fijo original.

### Entradas

Se toman explícitamente de `input-names`; no se infieren desde reglas constantes
ni desde nodos sin reguladores. Se codifican con f_u = u, se protegen y se
interpretan como parámetros constantes. Así se estudian todas sus asignaciones
posibles. No se reproduce el muestreo probabilístico de entradas de la plataforma.
Los JSON incluyen también asignaciones de entradas sin puntos fijos (recuento 0).

### Estrategias

- `first`: primer identificador en orden lexicográfico.
- `min_degree`: mínimo grado entrante + saliente funcional; desempate lexicográfico.
- `min_growth`: mínima suma de tamaños de tablas tras probar una eliminación;
  desempate lexicográfico. Es crecimiento de la representación tabular, no de AST.
- `random`: elección uniforme entre candidatos con generador local y semilla 42.

El preprint establece independencia para reordenaciones admisibles de las mismas
eliminaciones. Esto no obliga a que estrategias voraces elijan el mismo conjunto
de nodos: una sustitución puede crear una autorregulación y bloquear un candidato.
Registrar tanto el orden como el conjunto superviviente. Una única semilla no
caracteriza la variabilidad de la política aleatoria.

## Caracterización disponible

- Nodos totales, nodos internos, entradas; fracción eliminada total e interna.
- Aristas funcionales, autorregulaciones, grado entrante máximo.
- Componentes fuertemente conexas (SCC) y débilmente conexas.
- Aristas con y sin las identidades añadidas para las entradas. Sus bucles explican
  diferencias con los recuentos publicados por BBM.
- Clases de funciones, clase de red, número de entradas de tablas de verdad.
- Literales en DNF canónica sobre soporte esencial. **No** equivale al tamaño de
  una expresión mínima ni al número de literales de la regla importada.
- Puntos fijos, tiempo de enumeración antes/después, tiempo de reducción.

Los tiempos son de una ejecución sin repeticiones; no constituyen todavía una
comparación estadística de rendimiento. El tiempo de reducción incluye las
pruebas de candidatos de `min_growth` y excluye importación y verificación.

### Clases lógicas

Clasificación semántica, mutuamente exclusiva, aplicada al soporte esencial:

| Clase | Definición |
|---|---|
| CONST_0 / CONST_1 | Función constante |
| COPY / NOT | Identidad o negación unaria |
| AND / OR | Conjunción/disyunción de variables positivas, aridad ≥ 2 |
| NAND / NOR | Negación de AND/OR, aridad ≥ 2 |
| SIGNED_AND | Un único minterm verdadero, con signos mixtos |
| SIGNED_OR | Una única asignación falsa, con signos mixtos |
| XOR / XNOR | Paridad o su negación, aridad ≥ 2 |
| GENERAL | Ninguna de las clases anteriores |

Para las clases de red se excluyen las entradas protegidas. COPY_ONLY se separa
porque cumple simultáneamente las convenciones AND y OR de aridad uno.
HOMOGENEOUS_AND admite AND y COPY; HOMOGENEOUS_OR admite OR y COPY; AND_OR admite
ambas. Constantes y negaciones se mantienen explícitas; MIXED_OR_OTHER no implica
que la red sea intratable. NO_INTERNAL_NODES incluye redes de solo entradas o
vacías: no deben presentarse como un hallazgo de homogeneidad AND/OR.

MAX/minterm queda pendiente de una definición matemática explícita: no se
presupone equivalencia con las convenciones del proyecto a partir del nombre.
Las clases con signos mixtos se distinguen de las AND/OR monótonas.

## Procedencia y reproducibilidad

`data/raw/manifest.json` fija commit y huellas del espejo BBM. Los metadatos
preservan ID, enlace Cell Collective, publicación y reparaciones. El piloto se
ordena por `var-N` de BBM: sus entradas se contabilizan aparte y las salidas
pueden aparecer en `output-names`; el inventario usa la unión de las tres listas.

Las tablas JSON ordenan el soporte lexicográficamente; la primera variable es
el bit más significativo del índice. La tabla y su soporte son una representación
exacta independiente de la DNF exportada. `environment.json` registra Python,
plataforma, límites y SHA-256 del código del núcleo.

Los formatos BNET y SBML son exportaciones de BBM; archivar ambos no verifica
su equivalencia. Tampoco garantiza identidad con la versión viva de Cell Collective.
Conservar las condiciones y atribuciones de origen al ampliar o redistribuir el corpus.

## Próximas fases

1. **Adquisición y SBML-qual.** Comprobar acceso directo, versiones y exportaciones;
   implementar lectura de especies, transiciones, MathML y términos por defecto.
   Rechazar modelos multinivel y construcciones no admitidas de forma explícita.
   Comparar semánticamente BNET/SBML por función y auditar entradas y reparaciones.
2. **Escala.** Añadir backend BDD o equivalente exacto manteniendo la interfaz de
   soporte/sustitución; conservar este motor como oráculo de referencia. Añadir
   presupuestos de memoria/tiempo y estados de resultado incompleto.
3. **Corpus completo.** Inventario, exclusiones documentadas, deduplicación por
   ID/versión y comparación de reglas. Separar modelos reparados y originales.
4. **Experimentos.** Más semillas, métricas por paso, picos de memoria, tamaños de
   AST/BDD, grados completos, signos funcionales, SCC y cambio de clase por modelo.
   Condicionar por entradas y emparejar siempre antes/después del mismo modelo.
5. **Puntos fijos grandes.** Solver SAT/BDD, recuento o enumeración con límites;
   contraste con el oráculo exhaustivo y reconstrucción verificada.
6. **Teoremas.** Formalizar las clases del grupo y verificar todas sus hipótesis
   antes de usar fórmulas analíticas. No etiquetar «tratable» por semejanza textual.

## Referencias de base

- [Veliz-Cuba, 2011](https://doi.org/10.1016/j.jtbi.2011.08.042).
- [Preprint consultado, algoritmos y ejemplos](https://arxiv.org/abs/0907.0285).
- [Repositorio BBM y normalización de modelos](https://github.com/sybila/biodivine-boolean-models).
- [Implementación posterior del autor](https://github.com/alanavc/BNReduction):
  corresponde al trabajo de 2014 y referencias adicionales; no asumir que todas
  sus reglas son exactamente el algoritmo de 2011. No se ha copiado su código.
