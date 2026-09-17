# Nuevos ejemplos y revisión de Aurora — 17 de septiembre de 2026

## Resultado y alcance

**IL-6 es el candidato nuevo prioritario por su reducción sin condiciones de
entrada; desarrollo cardíaco es el más sencillo para una exposición matemática.**
Aurora sigue siendo útil, pero sus estados estacionarios ya aparecen en el
artículo original y su número ha sido objeto de trabajos posteriores.

Esta exploración complementa el censo; **no lo sustituye ni proporciona una
estimación de prevalencia**. Se intentaron 1.650 reducciones en las 78 instancias
BBM vinculadas a Cell Collective:

- 12 órdenes aleatorios por instancia, semillas 10–21, sin condicionar inputs.
- Para modelos con entre 1 y 4 inputs: todas sus configuraciones, con órdenes
  `first`, `min_growth` y `random` con semilla 10.
- 24 intentos alcanzaron el límite de 200.000 nodos BDD: BBM004 (11), BBM018 (3)
  y BBM078 (10). Son resultados desconocidos, no negativos.
- Un fallo de escritura en BBM009 se resolvió repitiendo ese modelo; ambas
  incidencias se conservan en el registro de ejecución.
- Se conservaron 80 resultados distintos dentro de cada modelo y configuración,
  correspondientes a 19 instancias. Todos tienen certificado SMT de biyección.
  No son 80 modelos independientes, ni 19 descubrimientos nuevos.

El filtro exige entre 2 y 12 supervivientes dinámicos, al menos una función de
varios argumentos y una familia objetivo: AND-OR-NOT out-uniform, afín, monotone
o AND-OR-NOT transformable en monotone mediante cambio de variables. No explora
todos los órdenes posibles. BBM y las versiones vivas de Cell Collective no se
suman como observaciones independientes.

## Selección para el artículo

Los tamaños de esta tabla **excluyen inputs externos**. Las clases se refieren
a las funciones dinámicas con los parámetros indicados, no a identidades
artificiales de entrada.

| Modelo | Variables dinámicas | Condición sobre inputs | Núcleo | Puntos fijos |
|---|---:|---|---|---|
| BBM019, IL-6 Signalling | 71 → 3 | Ninguna; 15 inputs libres | AND-NOT, homogéneo respecto de NOT, out-uniform | 0 o 1 por configuración; condición exacta abajo |
| BBM010, Cardiac Development | 13 → 2 | exogen_BMP2_I=1, exogen_CanWnt_I=0 | OR homogéneo; simétrico, conexo y con todos los self-loops | 2 |
| BBM073, Lymphoid and Myeloid Cell Specification | 31 → 2 | Cebpa_ER=1, Csf1=0; Il7 libre | AND homogéneo, out-uniform; grafo dirigido | 3 por valor de Il7 |
| BBM070, MAPK Cancer Cell Fate | 49 → 3 | Los cuatro inputs a 0 | AND-NOT homogéneo respecto de NOT, out-uniform | 2 |
| BBM068, Aurora Kinase A | 19 → 2 | AJUBA=1, GSK3B=0; otros dos inputs libres | AND-NOT homogéneo respecto de NOT, out-uniform | 1 por configuración restante |

Todos los originales condicionados de los nuevos ejemplos seleccionados no
pertenecen a AND-OR-NOT según la convención estricta de constantes. Para IL-6
la comparación se hace sin condicionar. La reducción revela esa pertenencia.

## 1. IL-6: una caracterización para todos los inputs

Fuente: [Ryll et al., 2011, DOI 10.1039/C1MB05261F](https://doi.org/10.1039/C1MB05261F).
El trabajo estudia modelos lógicos de señalización de IL-1/IL-6, sus estructuras
de feedback y su comportamiento de entrada/salida. Debe compararse con sus
análisis de estados lógicos estacionarios antes de formular una afirmación de
novedad. No se ha completado esa revisión bibliográfica.

La reducción dirigida al teorema usa `random`, semilla 19. No es la reducción
canónica. Se ha comprobado equivalencia semántica de **todas las funciones y de
los inputs** entre BBM019 y la exportación viva Cell Collective `2314_1`.

Definimos las tres variables supervivientes y los parámetros:

\[
x=\mathrm{mek6},\quad y=\mathrm{shp2},\quad z=\mathrm{stat3\_ta},
\]
\[
a=\mathrm{gp130m}\land\mathrm{il6}\land\neg\mathrm{nfkb},\qquad
b=\neg\mathrm{ros}\land\neg\mathrm{sirp1a},\qquad
c=\neg\mathrm{cyt\_ptpe}\land\neg\mathrm{pias3}\land\neg\mathrm{slim}.
\]

La red reducida es exactamente:

\[
x'=a\land\neg x\land\neg y\land\neg z,
\]
\[
y'=a\land b\land\neg x\land\neg y\land\neg z,
\]
\[
z'=a\land c\land\neg x\land\neg y\land\neg z.
\]

En las expresiones anteriores, `a`, `b` y `c` son abreviaturas de expresiones de
inputs; no son variables dinámicas nuevas. Todas las funciones son conjunciones
de literales y cada regulador tiene polaridad global única. El grafo dinámico
sin condicionar es completo y simétrico, con nueve interacciones negativas,
incluidos los tres self-loops. No es monotone ni switchable a monotone, debido
a los self-loops negativos.

**Demostración directa del número de puntos fijos.** Si cualquiera de `x,y,z`
fuera 1 en un punto fijo, su propia ecuación tendría lado derecho 0. Por tanto,
el único candidato es `(0,0,0)`. Al sustituirlo, las imágenes son `(a,ab,ac)`.
Concluimos:

\[
|\operatorname{Fix}(F_u)|=
\begin{cases}
1,&\mathrm{gp130m}=0\ \text{o}\ \mathrm{il6}=0\ \text{o}\ \mathrm{nfkb}=1,\\
0,&\mathrm{gp130m}=1,\ \mathrm{il6}=1,\ \mathrm{nfkb}=0.
\end{cases}
\]

La condición vale para los 15 inputs, sin fijar los otros doce. Existen puntos
fijos en 28.672 de las 32.768 configuraciones de entrada, uno por configuración;
no existen en las otras 4.096. No interpretar 28.672 como el número de puntos
fijos de una única red autónoma con inputs fijados.

Validación: equivalencia BDD de la fórmula completa de puntos fijos con
`!a & !x & !y & !z`; enumeración independiente de los 262.144 estados del núcleo
con sus inputs; certificado SMT de equivalencia con las ecuaciones originales
y las funciones de reconstrucción. No se ha enumerado la red original de 71
variables. La demostración anterior es propia y elemental: no se atribuye a un
teorema concreto sin comprobar sus hipótesis.

## 2. Desarrollo cardíaco: OR sobre dos nodos

Fuente: [Herrmann et al., 2012](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0046798).
El original ya estudia atractores asociados a los campos cardíacos. Nuestra
contribución potencial sería explicar la estructura del caso condicionado,
no descubrir por primera vez sus atractores.

Fijando `exogen_BMP2_I=1` y `exogen_CanWnt_I=0`, la política `first` deja:

\[
x=\mathrm{Nkx2\_5},\quad y=\mathrm{Tbx5},\qquad
x'=x\lor y,\quad y'=x\lor y.
\]

Ambas funciones son OR positivas; el grafo es simétrico, fuertemente conexo,
con ambos self-loops. Sus puntos fijos son exactamente `(0,0)` y `(1,1)`:
las dos ecuaciones fuerzan `x=y` y ambos valores comunes satisfacen el sistema.
Los 8.192 estados originales condicionados fueron enumerados y se comprobó
la igualdad del conjunto reconstruido, no solo su cardinalidad.

BBM053, vinculado al [trabajo de 2015 sobre incertidumbre](https://doi.org/10.1371/journal.pone.0131832),
produce el mismo motivo en esta exploración. No debe venderse como un ejemplo
matemáticamente independiente. Queda pendiente comparar exhaustivamente las
versiones y los protocolos temporales de entrada del artículo con el caso
autónomo condicionado que analizamos aquí.

## 3. Especificación linfoide/mieloide: AND y tres puntos fijos

Fuente: [Collombet et al., 2017](https://doi.org/10.1073/pnas.1610622114).
Se analiza la versión booleana BBM073. El modelo publicado contiene un
componente multinivel Spi1; la interpretación de `Spi1_b1` debe respetar esa
codificación antes de asignar fenotipos a los estados reconstruidos.

Con `Cebpa_ER=1`, `Csf1=0` y **sin fijar Il7**, `min_growth` produce:

\[
x=\mathrm{Egr2},\quad y=\mathrm{Spi1\_b1},\qquad x'=x\land y,\quad y'=y.
\]

Es AND positiva, homogénea y out-uniform. Los puntos fijos son `(0,0)`, `(0,1)`
y `(1,1)`: basta resolver `x<=y`. Hay tres por cada valor de Il7, seis pares
estado/input en total. El grafo tiene self-loops y la arista `y -> x`, pero no
`x -> y`: **no es simétrico**. No aplicar resultados que exijan grafo no dirigido.

## 4. MAPK: reservar como alternativa

Fuente: [Grieco et al., 2013](https://doi.org/10.1371/journal.pcbi.1003286).
Con `DNA_damage=EGFR_stimulus=FGFR3_stimulus=TGFBR_stimulus=0`, el orden aleatorio
con semilla 10 da:

\[
x=\mathrm{CREB},\quad y=\mathrm{p53},\quad z=\mathrm{PI3K},\qquad
x'=\neg x\land y,\quad y'=\neg x\land y,\quad z'=z.
\]

Es AND-NOT homogénea respecto de NOT. En un punto fijo `x=y`; sustituirlo obliga
a `x=y=0`, mientras `z` es libre. Hay dos puntos fijos. La variable identidad
aislada reduce el interés matemático frente a IL-6. Certificación SMT y
enumeración del núcleo realizadas; revisión bibliográfica pendiente.

## 5. Aurora: qué aporta y qué ya se sabía

El PDF facilitado corresponde a [Dahlhaus et al., 2016](https://doi.org/10.1016/j.canlet.2015.11.025),
Cancer Letters 371, 79–89. En p. 80 describe simulaciones síncronas mediante
BoolNet; en pp. 81–83 presenta 50 atractores y distingue el grupo II de estados
estacionarios, con AURKA inactiva. Por tanto, recuperar su estado estacionario
no basta como argumento de novedad.

Además, [Kim, Hopper y Cho, 2023](https://www.nature.com/articles/s41598-023-33346-1)
utilizan expresamente esta red para estudiar control del número de atractores
puntuales, incluidos controles de PP2A y combinaciones con AURKA. Este antecedente
no demuestra que hayan obtenido nuestro mismo núcleo, pero impide presentar
el análisis de puntos fijos de Aurora como un problema nuevo.

Se ha reproducido **exactamente la secuencia propuesta por el usuario**, con
`AJUBA=1`, `GSK3B=0`, dejando `STMNCanAct` y `MTCanAct` libres:

\[
x=\mathrm{AURKAActive},\quad y=\mathrm{SpindleAssembly},\qquad
x'=x,\quad y'=x\land\neg y.
\]

Tiene un único punto fijo dinámico `(0,0)` por configuración de los dos inputs
restantes. La enumeración independiente de 2.097.152 estados originales
condicionados encuentra cuatro pares estado/input; la reconstrucción desde el
núcleo coincide exactamente. No se conservan por ello los atractores cíclicos,
sus períodos ni sus cuencas.

La aportación potencial sería la reducción certificada, su pertenencia a una
familia matemática y una explicación estructural de los puntos fijos ya
observados. La prioridad entre artículos posteriores permanece abierta.

## Aplicabilidad de teoremas

**Nunca se infiere aplicabilidad únicamente del nombre de una familia.**
Los artefactos de exploración guardan `theorem_applicability.status=not_assessed`.
Las demostraciones anteriores resuelven directamente estos núcleos.

- [Veliz-Cuba, 2011](https://doi.org/10.1016/j.jtbi.2011.08.042): cada eliminación
  comprueba ausencia de self-loop semántico y registra su sustitución; además
  se certifica la correspondencia de puntos fijos computacionalmente.
- [Veliz-Cuba y Laubenbacher, 2012](https://doi.org/10.1007/s12190-011-0517-9):
  pertenecer a AND-NOT no establece pertenencia a la subclase normal.
- [Aracena, Richard y Salinas, 2014](https://doi.org/10.1016/j.jcss.2014.04.025):
  estos núcleos tienen loops; comprobar el resultado concreto antes de aplicar
  una cota formulada para grafos sin loops.
- [Aledo, Llano y Valverde, 2025](https://doi.org/10.1016/j.chaos.2025.116182):
  desarrollo cardíaco reúne familia OR, simetría y todos los self-loops, pero
  queda pendiente identificar y verificar la proposición o teorema exacto.
  No extender automáticamente esa aplicabilidad a IL-6, Aurora o BBM073.

## Reproducibilidad y límites del software

```powershell
python experiments/search_examples.py --timeout 45
python experiments/verify_examples.py
```

Dependencias: extra `research` de `pyproject.toml`.

- [Ejecución y errores](../results/example_search/run.json).
- [Seis verificaciones detalladas](../results/example_search/verified_examples.json),
  con reglas, secuencia de eliminación, reconstrucción, certificados y estados.
- Resultados por instancia: por ejemplo [IL-6](../results/example_search/019.json),
  [cardíaco](../results/example_search/010.json) y [linfoide/mieloide](../results/example_search/073.json).

La nueva búsqueda calcula la topología solo sobre nodos dinámicos y usa flags
estrictos de familias que excluyen constantes como puertas vacías. Los informes
históricos del censo todavía incluyen campos heredados: algunos tamaños suman
inputs y algunas familias se calculan solo sobre reglas no constantes. No usar
esos campos como cifras finales del artículo sin migrarlos a la taxonomía.
ANF, canalización, FVS y un catálogo completo de hipótesis de teoremas siguen
pendientes de implementación; esta exploración no afirma haberlos completado.
