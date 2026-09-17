# Especificación normativa de clasificación de redes booleanas

Este documento fija las convenciones que deben utilizarse en el censo de Cell
Collective/BBM y en la comparación entre una red original y sus reducciones de
Veliz-Cuba. Las etiquetas son semánticas, inclusivas y reproducibles: las clases
se solapan y una función puede pertenecer a varias a la vez.

## 1. Red, entradas y estados condicionados

Una red es `F=(f_1,...,f_n):{0,1}^n -> {0,1}^n`. Se distinguen las variables
dinámicas de los inputs externos `u_1,...,u_m`. Un input no se convierte en un
nodo dinámico con regla identidad para declarar propiedades de la red: al fijar
`u=u*` se analiza la red autónoma condicionada `F_{u*}`. Los informes deben
distinguir `original_unconditioned`, `input_conditioned`, `reduced` e
`input_conditioned_reduced`. En los artefactos del proyecto las identidades de
entrada se conservan para reconstrucción, pero se excluyen del censo biológico
de signos; el alcance incluyendo identidades se guarda por separado.

## 2. Funciones esenciales y grafo firmado

`x_j` es esencial para `f_i` si existe un contexto de las demás variables donde
`f_i(x_j=0,z) != f_i(x_j=1,z)`. El grafo tiene `x_j -> x_i` exactamente cuando
`x_j` es esencial para `f_i`.

La interacción es positiva si `f_i(0,z) <= f_i(1,z)` para todo `z`, negativa si
`f_i(0,z) >= f_i(1,z)` para todo `z`, y `non_unate` si ambos sentidos aparecen
en contextos distintos. Una red es `unate` si todas sus interacciones esenciales
tienen signo definido.

`out_uniform` significa que todas las aristas que salen de una variable tienen
el mismo signo. Es la definición operativa de «uniforme respecto de NOT»: existe
una polaridad global por variable cada vez que esa variable actúa como regulador.
Una dependencia `non_unate` invalida `out_uniform`. `out_uniform` es una
propiedad del grafo firmado; `signed_operator_homogeneous` añade una condición
sobre la familia de las funciones y, por tanto, es más fuerte.

Cada resultado debe conservar witnesses: para un conflicto, la variable fuente,
los destinos positivos y negativos; para una familia falsa, una función que la
viola y su forma legible/BDD equivalente.

## 3. Clases locales inclusivas

Para cada función se calculan todas estas clases sobre la función equivalente y
su soporte esencial, nunca sobre strings o variables redundantes:

| Clase | Condición semántica |
|---|---|
| `CONSTANT` | `0` o `1` |
| `COPY` | `x_j` |
| `NOT` | `!x_j` |
| `AND` | conjunción de todos los literales positivos |
| `OR` | disyunción de todos los literales positivos |
| `NAND` | `!(AND(x_j))`, equivalente a disyunción de literales negativos |
| `NOR` | `!(OR(x_j))`, equivalente a conjunción de literales negativos |
| `AND_NOT` / `MINTERM` | conjunción de literales, positivos o negativos |
| `OR_NOT` / `MAXTERM` | disyunción de literales, positivos o negativos |
| `XOR` | `x_1 xor ... xor x_k` |
| `XNOR` | `1 xor x_1 xor ... xor x_k` |
| `AFFINE` | `c xor (xor de un subconjunto de variables)` sobre `F_2` |
| `OTHER` | no pertenece a las anteriores |

Las clases son inclusivas. `x` puede ser simultáneamente `COPY`, `AND` y `OR`;
`!x` puede ser `NOT`, `NAND` y `NOR`. Las constantes se registran explícitamente
y no se convierten en AND/OR vacíos salvo que un teorema lo exija.

`AND_OR_NOT` significa exactamente `AND_NOT ∪ OR_NOT` por función local. No
significa una expresión arbitraria construida recursivamente con puertas AND, OR
y NOT. `AND_OR_NAND_NOR` significa exactamente que cada regla pertenece a
`{AND, OR, NAND, NOR}`. Por tanto `x & !y` es `AND_NOT`, pero no `AND` ni
`AND_OR_NAND_NOR`.

## 4. Familias de redes y homogeneidad

Se guardan flags independientes:

`is_conjunctive` (todas AND positivas), `is_disjunctive` (todas OR positivas),
`is_AND_NOT`, `is_OR_NOT`, `is_AND_OR_NOT`, `is_AND_OR`,
`is_AND_OR_NAND_NOR`, `is_affine`, `is_monotone` y `is_unate`.

Una red es `signed_operator_homogeneous=AND` si todas sus reglas no constantes
son `AND_NOT` y cada variable tiene una polaridad global fija. Análogamente para
`OR`. Es más fuerte que `is_AND_NOT` o `is_OR_NOT`. `operator_homogeneous` se
reserva para una misma puerta positiva o negada en todas las reglas.

Una red es `monotone`/cooperative si todas las interacciones esenciales son
positivas. Para una red unate se comprueba además `switchable_to_monotone`:
existen etiquetas `s_i` en `{+1,-1}` que satisfacen
`sign(j -> i)=s_j*s_i` en cada arista. Se guarda ese vector como witness.

La propiedad `all_self_loop` solo se marca si cada variable dinámica pertenece
semánticamente a su propia función. Las entradas no cuentan para este campo.

## 5. Álgebras y topología

Para cada regla se guarda su ANF, `anf_degree`, `anf_monomial_count`,
`is_linear` e `is_affine`; para la red, máximos y medias. Se pueden añadir
`is_canalizing`, `is_nested_canalizing` y `canalizing_depth` cuando el cálculo
sea razonable, sin inferir de ellos un número de puntos fijos.

El grafo semántico debe guardar nodos/aristas por signo, distribuciones de grado,
fuentes, sumideros, componentes débiles, SCCs, SCCs cíclicas, aciclicidad,
ciclos positivos/negativos, simetría dirigida, `all_self_loop` y FVS. Una
heurística de FVS se etiqueta como cota, nunca como óptimo exacto.

`acyclic` solo implica un único punto fijo cuando los inputs están fijados. La
propiedad `is_symmetric_interaction_graph` requiere `j -> i` si y solo si `i -> j`
para nodos distintos; no se debe aplicar un teorema de grafo no dirigido a una
red dirigida por pertenecer a la familia lógica adecuada.

## 6. Reducción de Veliz-Cuba

Puede eliminarse `x_k` si `x_k` no es esencial para `f_k`. Se sustituye `f_k` en
todas las reglas restantes, se simplifica semánticamente y se recalculan soporte,
signos, self-loops y topología tras cada paso. Las entradas están protegidas.
La traza debe guardar secuencia, funciones vigentes, supervivientes y funciones
de reconstrucción. `canonical_reduction` usa un orden determinista;
`theorem_targeted_reduction` explora secuencias alternativas y nunca se presenta
como una salida canónica única.

El método está orientado a preservar puntos fijos, no automáticamente todos los
atractores periódicos ni la dinámica transitoria. Para redes pequeñas se enumera
el espacio completo; para redes grandes se usa equivalencia SMT entre las
ecuaciones originales y las reducidas más la traza triangular de reconstrucción.

## 7. Aplicabilidad de teoremas

La pertenencia a una familia y la aplicabilidad de un teorema son campos distintos.
Cada teorema debe tener `applicable`, condiciones satisfechas, condiciones fallidas,
predicción y verificación. Entre las condiciones posibles están grafo no dirigido,
connectedness, loop-less, `all_self_loop`, normalidad, inputs fijados y ausencia
de constantes. Nunca se marca aplicabilidad solo por el nombre de una familia.

Familias prioritarias: conjunctive/disjunctive, `AND_NOT` (incluida normal
AND-NOT), `OR_NOT`, `AND_OR_NOT`, `AND_OR_NAND_NOR`, monotone y affine. Para
affine, los puntos fijos se resuelven como `(A-I)x=b` sobre `F_2`. Para otras
familias se citarán y comprobarán las hipótesis de los resultados de Veliz-Cuba
(2011), Jarrah–Laubenbacher–Veliz-Cuba (2010), Aracena–Richard–Salinas (2014),
Aledo et al. (2020, 2022, 2025) y los trabajos indicados en
[`protocolo.md`](protocolo.md).

## 8. Salidas obligatorias y pruebas

Cada modelo produce clasificación original, reducida y, cuando corresponda,
condicionada por inputs. Los campos mínimos incluyen dimensiones dinámicas,
inputs, tipos locales, familias, homogeneidad, topología, puntos fijos, método de
cálculo, reducción y aplicabilidad teórica. Las funciones falsas incluyen
counterexamples. Los resultados de puntos fijos indican `exact`, cota inferior o
timeout; «pendiente» nunca significa cero.

Las pruebas semánticas cubren redundancias (`(x&y)| (x&!y)=x`), De Morgan,
duplicados, XOR/XNOR, affine, AND-NOT frente a AND, soporte esencial, inputs sin
self-loop artificial y reconstrucción exacta. Los informes por instancia y el
censo deben conservar manifiesto, versión de la fuente, SHA-256, entorno y
secuencia completa de eliminación.

El documento es normativo para el código y para la redacción posterior del
artículo; las afirmaciones específicas del borrador adjunto se citarán como
borrador hasta verificarlas en la literatura publicada.
