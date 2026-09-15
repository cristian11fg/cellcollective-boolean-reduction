# Protocolo experimental — versión 0.2

## 1. Preguntas científicas

El punto de partida es el borrador de Aledo, Llano y Valverde, *Fixed points in
mixed max-min-BN Boolean networks*, de 3 de septiembre de 2026, especialmente
§§2–4 y §12. Es un manuscrito en preparación. Su idea central orienta el proyecto:
relacionar una red de funciones locales diversas con otra cuyos puntos fijos se
puedan describir mediante resultados anteriores. El PDF no se incorpora al
repositorio público.

Tenemos dos preguntas distintas:

1. **Caracterización.** ¿Cuántas redes de origen Cell Collective son uniformes
   respecto de NOT? ¿Cuáles tienen funciones MIN, MAX, mezclas de ambas u otras
   funciones? ¿Qué propiedades tienen sus grafos?
2. **Transferencia de resultados.** ¿Podemos partir de una red biológica con pocas
   restricciones iniciales y encontrar una reducción hasta una clase cuyos puntos
   fijos estén caracterizados, para reconstruir después los originales?

No buscamos necesariamente la red con menos nodos. Buscamos una red reducida
con **hipótesis teóricas verificadas** y una correspondencia explícita de puntos
fijos. La reducción y la aplicación de un teorema son dos pasos diferentes.

## 2. Red, funciones locales y dependencias

### 2.1. Estados y puntos fijos

Sea $V=\{1,\ldots,n\}$. Cada nodo tiene un estado $x_i\in\{0,1\}$ y una función
local $f_i:\{0,1\}^V\to\{0,1\}$. La red es

$$F=(f_i)_{i\in V}:\{0,1\}^V\longrightarrow\{0,1\}^V.$$

En actualización síncrona, todas las funciones leen el mismo estado y
$x(t+1)=F(x(t))$. Un punto fijo satisface simultáneamente

$$x_i=f_i(x)\qquad\text{para todo }i\in V.$$

Estas ecuaciones son el objeto del estudio. Un punto fijo no es una órbita
periódica de longitud mayor que uno ni una trayectoria transitoria.

### 2.2. Grafo funcional dirigido

Escribimos $x^{i\leftarrow b}$ para el estado que reemplaza $x_i$ por $b$.
La variable $i$ es una dependencia esencial de $f_j$ cuando

$$i\in\operatorname{supp}(f_j)
\iff\exists x:\ f_j(x^{i\leftarrow0})\ne f_j(x^{i\leftarrow1}).$$

El grafo $D_F$ tiene un arco $i\to j$ exactamente en ese caso. $N^-(j)$ son
los reguladores de $j$; $N^+(i)$, los nodos regulados por $i$. Un bucle $i\to i$
indica dependencia esencial de $f_i$ respecto de $x_i$.

Por ejemplo, $(x_i\land x_k)\lor(\neg x_i\land x_k)=x_k$. El texto contiene
$x_i$, pero no existe dependencia funcional respecto de esa variable. El grafo
se obtiene de las funciones simplificadas, no contando nombres en una fórmula.

**Para el corpus admitimos grafos dirigidos, desconectados y con bucles.** La
Definición 2.1 del borrador parte de un grafo no dirigido y conectado: esas son
hipótesis de una clase teórica, no propiedades que debamos imponer a todos los
modelos. Cuando un resultado requiera grafo no dirigido, comprobaremos
$i\to j\iff j\to i$ para $i\ne j$, además de sus condiciones sobre bucles y
conectividad. No añadiremos dependencias para simetrizar una red biológica.
La reciprocidad del soporte no exige igualdad de signos en los arcos opuestos.

### 2.3. Signo funcional y unateness

Definimos, con valores enteros,

$$\Delta_i f_j(x)=f_j(x^{i\leftarrow1})-f_j(x^{i\leftarrow0})\in\{-1,0,1\}.$$

- **Positivo:** todas las diferencias son no negativas y alguna vale 1.
- **Negativo:** todas son no positivas y alguna vale −1.
- **Mixto o dependiente del contexto:** aparecen tanto 1 como −1.
- **Sin dependencia:** todas son cero.

Una función es *unate* si cada variable esencial tiene un signo único en ella.
$a\land\neg b$ es unate; $a\mathbin{\mathrm{XOR}}b$ no lo es. El signo pertenece
a la función, no a su representación textual. El grafo de influencias funcionales
es el marco de los resultados sobre circuitos positivos y negativos [R6].

## 3. Qué queremos decir por out-uniform y por homogénea

### 3.1. Uniformidad respecto de NOT

El borrador define esta propiedad en la página 3, pero no introduce
«out-uniform» como una definición independiente. Adoptamos explícitamente
**out-uniform en signo**: todos los arcos que salen de una misma variable tienen
el mismo signo y ninguno es mixto. Si se pretende otra definición bibliográfica
de out-uniform, habrá que identificarla y registrar otro indicador.

Para cada fuente activa $i$, debe existir $s_i\in\{+,-\}$ tal que

$$\operatorname{sign}(i\to j)=s_i\qquad\forall j\in N^+(i).$$

Con esta convención, **out-uniform en signo y uniformidad global respecto de NOT
son la misma condición semántica**. No son dos filtros de distinta intensidad.
Las fuentes sin arcos salientes no imponen signo y se registran por separado.

La unateness local es más débil: $f_1=a$ y $f_2=\neg a$ son funciones unates,
pero la fuente $a$ tiene efectos opuestos. Tampoco exigimos que todas las fuentes
sean positivas: se admite una partición $W$ de fuentes positivas y $W'$ de
fuentes negativas, tal como en el borrador.

La condición permite expresar las funciones de forma monótona en los literales
$z_i=x_i$ para $i\in W$ y $z_i=\neg x_i$ para $i\in W'$. No exige que cada
función sea un único MIN/MAX. Tampoco establece una conjugación dinámica con
una red monótona: cambiar coordenadas del estado modifica también las salidas.

### 3.2. MIN y MAX admiten negaciones

Sobre el soporte esencial $I_j$ de una función no constante:

$$\mathrm{MIN}_j=\bigwedge_{i\in I_j}z_{ji},\qquad
\mathrm{MAX}_j=\bigvee_{i\in I_j}z_{ji},\qquad
z_{ji}\in\{x_i,\neg x_i\}.$$

En una clase general AND-NOT/OR-NOT los signos pueden depender del destino $j$.
La homogeneidad del borrador exige además que $z_{ji}=z_i$ en todas las funciones
donde aparezca $i$: deben ser restricciones del mismo minterm o maxterm global.

| Familia local | Ejemplo | Etiquetas antiguas del programa |
|---|---|---|
| MIN: conjunción de literales | $a\land\neg b\land c$ | AND, NOR, SIGNED_AND |
| MAX: disyunción de literales | $a\lor\neg b\lor c$ | OR, NAND, SIGNED_OR |
| Literal unario | $a$ o $\neg a$ | COPY, NOT; pertenece a MIN y MAX |
| Constante | 0 o 1 | CONST_0, CONST_1; categoría separada |
| Unate fuera de MIN/MAX | $a\lor(b\land c)$ | Puede aparecer como GENERAL |
| No unate | $a\mathbin{\mathrm{XOR}}b$ | XOR y otras funciones |

NOR es MIN porque $\neg(a\lor b)=\neg a\land\neg b$; NAND es MAX por dualidad.
Para aridad $k>0$, MIN equivale a una única fila verdadera en la tabla esencial;
MAX, a una única fila falsa. En aridad uno se cumplen ambas condiciones.

### 3.3. Dos ejes independientes de clasificación

Primero registramos si todas las funciones no constantes son MIN, todas MAX,
todas MIN/MAX o si algunas quedan fuera. Para una mezcla estricta exigimos al
menos un MIN y un MAX de aridad mayor que uno; los literales no deciden entre
ambas familias. Después registramos uniformidad NOT, constantes, entradas,
reciprocidad, bucles y componentes del grafo.

Una **min-BN homogénea en el sentido del borrador** cumple la condición MIN y
la uniformidad NOT; análogamente para max-BN. Las constantes se marcan aparte
y requieren resultados que las admitan. La homogeneidad de operaciones sola
no acredita la homogeneidad del manuscrito.

Las etiquetas antiguas `HOMOGENEOUS_AND` y `HOMOGENEOUS_OR` de `metrics.py`
solo describen AND/OR positivos. No son sustitutos de las clases del borrador.
La nueva caracterización está en `structure.py` y complementa esas métricas.

## 4. Reducción: definición, justificación y reconstrucción

### 4.1. Hipótesis mínima de un paso

Partimos de funciones booleanas deterministas arbitrarias. No exigimos MIN/MAX,
uniformidad NOT ni reciprocidad. Para eliminar $i$ mediante Veliz-Cuba se requiere
que, **en la red actual**, se cumpla

$$i\notin\operatorname{supp}(f_i).$$

Los pasos S/R del método simplifican dependencias y sustituyen la función del
nodo eliminado en las que lo usan [R1]. Las condiciones adicionales del borrador
permiten identificar una clase destino, pero no son necesarias para este paso.

### 4.2. Sustitución formal

Sea $U=V\setminus\{i\}$ y $y\in\{0,1\}^U$. Como $f_i$ no depende de $x_i$,
su valor queda determinado por $y$. Definimos la extensión

$$E_i(y)_k=\begin{cases}y_k,&k\ne i,\\ f_i(y),&k=i.\end{cases}$$

La red reducida $G=F^{[i]}$ está definida en $U$ por

$$g_j(y)=f_j(E_i(y)),\qquad j\in U.$$

Esto significa $f_j[x_i\leftarrow f_i]$. Si aparece $\neg x_i$, se reemplaza
por $\neg f_i$, no por $f_i$. Las funciones que no dependen de $i$ no cambian.
Después se simplifica y se recalcula el grafo. Una ruta $k\to i\to j$ puede
originar una nueva dependencia $k\to j$, pero esta también puede cancelarse.

### 4.3. Por qué hay una biyección de puntos fijos

Esta demostración directa explica el certificado que verifica el programa,
correspondiente al resultado de [R1] utilizado en §2.1 del borrador.

Si $x$ es fijo para $F$, satisface $x_i=f_i(x)$. Al proyectar $y=x|_U$,
obtenemos $x=E_i(y)$ y $g_j(y)=f_j(x)=x_j=y_j$ para cada superviviente. Así,
$y$ es fijo para $G$.

Recíprocamente, si $y$ es fijo para $G$, construimos $x=E_i(y)$. Las ecuaciones
de los supervivientes se cumplen por definición de $G$. La de $i$ se cumple
porque $f_i$ no depende de la coordenada añadida. Esta extensión es única:
cualquier punto fijo sobre $y$ tiene que satisfacer $x_i=f_i(y)$. Por tanto,

$$\operatorname{Fix}(F)\ \xleftrightarrow[\ E_i\ ]{\ \pi_i\ }
\operatorname{Fix}(F^{[i]}).$$

No afirmamos que $E_i$ relacione todas las trayectorias. La reducción puede
cambiar ciclos y transitorios. Preservar otros atractores requiere resultados
y condiciones adicionales [R7].

### 4.4. Secuencias y reconstrucción inversa

En una secuencia $i_1,\ldots,i_m$, cada nodo debe ser reducible en el momento de
eliminarlo. Guardamos la función vigente $h_{i_t}$, que puede haber cambiado
respecto de la original. Dado un punto fijo de la red final, reconstruimos

$$x_{i_m}=h_{i_m}(y),\quad x_{i_{m-1}}=h_{i_{m-1}}(y,x_{i_m}),\quad\ldots.$$

Si las variables eliminadas no dependen entre sí, se pueden usar directamente
las funciones originales, como explica el borrador. En general hace falta la
traza de funciones intermedias.

La red vacía tiene una única configuración, la tupla vacía, y un único punto
fijo. Este se extiende al original. No la contamos como un ejemplo no trivial
de homogeneidad.

### 4.5. Orden admisible y objetivo de parada

La conmutatividad se refiere a reordenaciones admisibles de las mismas
eliminaciones [R1]. No autoriza a eliminar todos los nodos inicialmente sin bucle.
Por ejemplo, si $f_1=x_2$ y $f_2=x_1$, ambos empiezan sin bucle; al eliminar 1
queda $g_2=x_2$, que ya no es reducible con esta regla.

Las estrategias pueden elegir conjuntos supervivientes diferentes. Evaluaremos
también redes intermedias y buscaremos detenernos cuando haya un teorema
aplicable. El motor actual termina cuando no quedan candidatos; la parada
automática por certificado está pendiente. Menos nodos no significa un mejor
ejemplo para el artículo.

## 5. Entradas y constantes: dos conceptos distintos

Sean $x$ los estados internos y $u$ las entradas. Para $u=a$ constante estudiamos
$F_a(x)=F(x;a)$. El piloto usa la red ampliada
$\widehat F(x,u)=(F(x;u),u)$, que conserva las entradas y reúne sus asignaciones:

$$|\operatorname{Fix}(\widehat F)|=\sum_{a\in\{0,1\}^{|u|}}
|\operatorname{Fix}(F_a)|.$$

Una entrada libre no es una constante 0 o 1 hasta fijar su valor. Un nodo con
función constante tampoco debe convertirse en entrada libre. No modelamos
entradas probabilísticas ni entradas variables en el tiempo.

Para el **censo biológico de signos** excluimos las identidades artificiales
$u'=u$, pero conservamos las influencias de las entradas sobre los nodos internos.
Así evitamos que una entrada inhibidora tenga un conflicto artificial con su
identidad positiva. El diagnóstico permite también incluirlas y registra el
alcance elegido. Para aplicar teoremas a una red autónoma, fijamos las entradas
o verificamos las hipótesis sobre toda la red ampliada; no trasladamos
automáticamente el indicador calculado sobre las reglas biológicas.

## 6. Un candidato real para ilustrar el artículo

### 6.1. Cell Cycle Transcription

El modelo BBM 031 está asociado a Orlando et al. (2008), *Global control of
cell-cycle transcription by coupled CDK and network oscillators*,
[DOI](https://doi.org/10.1038/nature06955). Los
[metadatos](../data/raw/031/metadata.json) enlazan a Cell Collective y GINsim;
BBM declara que presenta el modelo sin modificaciones. Antes de cerrar el
ejemplo se cotejará con su fuente original.

Tiene nueve nodos y ninguna entrada externa. No es una max-min-BN pura; por
ejemplo,

$$f_{\mathrm{SBF}}=(x_{\mathrm{MBF}}\lor x_{\mathrm{CLN3}})
\land\neg x_{\mathrm{YHP1}}\land\neg x_{\mathrm{YOX1}}$$

no es un único MIN ni MAX sobre su soporte esencial. Sí cumple uniformidad NOT.
Por tanto ilustra el paso desde funciones más generales que el núcleo MIN/MAX
del borrador.

### 6.2. Reducción de nueve a tres nodos

La estrategia `first` elimina en este orden:

$$\mathrm{ACE2},\ \mathrm{CLN3},\ \mathrm{HCM1},\ \mathrm{MBF},\
\mathrm{SBF},\ \mathrm{SWI5}.$$

Sean $a=x_{\mathrm{SFF}}$, $b=x_{\mathrm{YHP1}}$, $c=x_{\mathrm{YOX1}}$.
La [red reducida](../results/pilot/031_first.bnet) es

$$G(a,b,c)=(q,q,q),\qquad q=a\land\neg b\land\neg c.$$

La traza registra las sustituciones exactas. Para entenderlas en equilibrio,
sea $t=\neg x_{\mathrm{YHP1}}\land\neg x_{\mathrm{YOX1}}$. Las reglas implican
ACE2=SWI5=$a$, CLN3=MBF=$at$, SBF=$at$ y HCM1=$at$; al sustituirlas, las tres
ecuaciones supervivientes tienen lado derecho $at$.

La red reducida satisface las condiciones estructurales relevantes:

- Todas sus funciones son el mismo minterm $a\land\neg b\land\neg c$.
- Tiene signos globales $W=\{a\}$ y $W'=\{b,c\}$.
- Su soporte es recíproco, conectado y cada nodo tiene autorregulación.
- No tiene constantes ni entradas que obliguen a adaptar el resultado.

### 6.3. Resultado anterior y verificación independiente

La caracterización de MIN/MAX-PDS mediante conjuntos dominantes de Aledo et al.
(2020) conecta el ejemplo con teoría previa [R2]. En la versión dual MIN hay
una sola componente positiva, $\{a\}$, adyacente a ambas variables negativas.
El único subconjunto de componentes positivas que domina ambas es esa componente.
Se obtiene un único punto fijo.

Podemos comprobarlo directamente: un punto fijo satisface $a=b=c=q$. Si el valor
común fuera 1, $q=1\land0\land0$ valdría 0. El valor común 0 sí satisface las
ecuaciones. Luego

$$\operatorname{Fix}(G)=\{(0,0,0)\}.$$

La reconstrucción da cero en las nueve variables originales. Se verifica frente
a la enumeración exhaustiva de los $2^9$ estados. Otras estrategias llegan a una
red vacía; para explicar la aplicación de un resultado anterior es más útil
conservar esta min-BN de tres nodos. Es un candidato matemático preliminar,
no una nueva validación biológica.

## 7. Recuento disponible y diseño del censo completo

El diagnóstico se reproduce con:

```powershell
python experiments/analyze_structure.py
python -m unittest discover -s tests -v
```

Salida: [results/structure/pilot.json](../results/structure/pilot.json).
Omitiendo las identidades artificiales de las entradas:

| Modelo | Funciones localmente unates | Out-uniform en signo | Operaciones de las reglas internas |
|---|---|---|---|
| Cortical Area Development | Sí | No | MIN |
| Gut Microbiome | Sí | No | Incluye funciones fuera de MIN/MAX |
| Mammalian Cell Cycle 2006 | Sí | No | Incluye funciones fuera de MIN/MAX |
| Toll Pathway of Drosophila | Sí | Sí | MAX |
| Cell Cycle Transcription | Sí | Sí | Incluye funciones fuera de MIN/MAX |

**2/5 son out-uniform en signo; 5/5 son localmente unates.** No son estimaciones
de todo Cell Collective: el piloto de BBM se seleccionó por tamaño. El JSON
identifica fuentes con signos incompatibles y contextos testigo. `GENERAL` en
el clasificador anterior no equivale a no unate.

Para responder cuántas hay en el catálogo completo se fijará una instantánea y
se publicarán modelos encontrados, importados, excluidos y pendientes por límites
técnicos. La unidad será modelo-versión, con deduplicación y recuento adicional
por modelo cuando haya varias versiones. Se conservarán procedencia y reparaciones.

Los recuentos distinguirán antes/después, familia de operaciones, uniformidad,
hipótesis del grafo y tratamiento de entradas. Se indicarán denominadores y
números absolutos. Un error de importación o un límite de cálculo significa
«desconocido», no «la propiedad es falsa».

## 8. Desde una red arbitraria hasta una clase conocida

El esquema experimental es

$$F\longrightarrow F^{[i_1]}\longrightarrow\cdots\longrightarrow H
\xrightarrow{\text{teorema aplicable}}\operatorname{Fix}(H)
\xrightarrow{\text{reconstrucción}}\operatorname{Fix}(F).$$

No toda red tiene que alcanzar una clase favorable. Una red arbitraria puede
tener todos sus nodos autorregulados y ninguna eliminación admisible. Tampoco
el fracaso de una estrategia demuestra que ninguna otra funcione: una búsqueda
limitada concluye «no encontrado», no «no existe».

Cada candidato debe guardar funciones, secuencia, signos, clase lógica, condiciones
del grafo, referencia y resultado utilizado, más la reconstrucción verificable.

| Destino | Qué resultado interesa | Condiciones que comprobar |
|---|---|---|
| MIN/MAX homogénea, no dirigida y con todos los bucles | Recuento y estructura por dominación [R2] | Signos globales, reciprocidad, bucles y versión MIN/MAX correcta |
| MIN/MAX homogénea con nodos sin bucle | Resultados generalizados [R3] | Consultar el teorema completo; no reutilizar sin más la fórmula del caso con todos los bucles |
| AND u OR positivas sobre grafo dirigido | Descomposición por componentes fuertemente conexas [R4] | Ausencia de negaciones e hipótesis específicas del resultado |
| MIN/MAX con constantes | Resultados de §4 del borrador | Separar proposiciones en preparación de resultados publicados |
| Clase con garantía de existencia o una cota | Resultados de circuitos y signos [R5, R6] | Una cota o existencia no equivale al recuento exacto ni al conjunto de puntos fijos |

Convertir redes arbitrarias a representaciones AND-NOT **añadiendo variables
auxiliares** es otra vía [R8]. No es reducción por eliminación ni garantiza
uniformidad NOT por fuente o reciprocidad. Se estudiaría como experimento aparte.

## 9. Implementación y límites

Disponible: BNET, soporte esencial, sustitución exacta, traza inversa, métricas,
cuatro estrategias y diagnóstico de signos/MIN/MAX. `first` usa orden
lexicográfico; `min_degree` minimiza grado entrante más saliente; `min_growth`
minimiza entradas de tablas tras probar una eliminación, no longitud de expresión.
Los empates son lexicográficos; `random` usa semilla 42 en el piloto.

El manifiesto fija commit y SHA-256 de los datos. SBML está archivado, pero aún
no se importa ni se contrasta con BNET. Se admiten hasta 16 variables por tabla
local y 20 nodos para enumeración de puntos fijos. Los límites generan errores
explícitos. Los tiempos actuales son de una ejecución, no un estudio estadístico.

Las clases «con constantes» son verdaderas por vacuidad cuando no hay funciones
no constantes; `nonconstant_rules` permite separar redes vacías, solo constantes
o solo entradas. `reciprocal_support` no es por sí solo un certificado de un
teorema. Las fórmulas generales de dominación todavía no están implementadas.

Próximas fases: inventario completo; importación y entradas auditadas; motor
simbólico exacto para redes grandes; evaluación de redes intermedias; certificados
de teoremas; y redacción del ejemplo con grafo, secuencia y estados reconstruidos.

## 10. Bibliografía comentada

- **[R1]** A. Veliz-Cuba (2011), *Reduction of Boolean network models*, Journal of
  Theoretical Biology 289, 167–172. [DOI](https://doi.org/10.1016/j.jtbi.2011.08.042),
  [preprint consultado](https://arxiv.org/abs/0907.0285). Base de la reducción.
- **[R2]** J. A. Aledo, A. Barzanouni, G. Malekbala, L. Sharifan y J. C. Valverde
  (2020), *Counting Periodic Points in Parallel Graph Dynamical Systems*, Complexity,
  9708347. [Texto completo](https://onlinelibrary.wiley.com/doi/10.1155/2020/9708347).
  Conexión entre puntos fijos y conjuntos dominantes; aplicable al ejemplo reducido.
- **[R3]** Los mismos autores (2022), *Fixed points in generalized parallel and
  sequential dynamical systems induced by a minterm or maxterm Boolean functions*,
  Journal of Computational and Applied Mathematics 408, 114070.
  [DOI](https://doi.org/10.1016/j.cam.2021.114070). Referencia del borrador para
  sistemas sin todos los bucles. Su aplicación se cotejará con el texto completo;
  no hemos implementado sus fórmulas a partir del resumen del manuscrito.
- **[R4]** A. S. Jarrah, R. Laubenbacher y A. Veliz-Cuba (2010), *The Dynamics of
  Conjunctive and Disjunctive Boolean Network Models*, Bulletin of Mathematical
  Biology 72, 1425–1447. [DOI](https://doi.org/10.1007/s11538-010-9501-z),
  [preprint](https://arxiv.org/abs/0805.0275). Alternativa para AND/OR positivas
  sin imponer reciprocidad.
- **[R5]** J. Aracena, A. Richard y L. Salinas (2014), *Maximum number of fixed
  points in AND–OR–NOT networks*, Journal of Computer and System Sciences 80,
  1175–1190. [DOI](https://doi.org/10.1016/j.jcss.2014.04.025). Contexto para cotas,
  no una fórmula universal de recuento de cada red.
- **[R6]** A. Richard (2019), *Positive and negative cycles in Boolean networks*,
  Journal of Theoretical Biology 463, 67–76.
  [Texto del autor](https://webusers.i3s.unice.fr/~richard/PUBLICATIONS/JOURNALS/2019_Rene_Thomas.pdf).
  Signos, circuitos e hipótesis para resultados dinámicos.
- **[R7]** A. Saadatpour, R. Albert y T. C. Reluga (2013), *A Reduction Method for
  Boolean Network Models Proven to Conserve Attractors*, SIAM Journal on Applied
  Dynamical Systems 12, 1997–2011. [DOI](https://doi.org/10.1137/13090537X).
  Distinguir puntos fijos de otros atractores y sus requisitos de conservación.
- **[R8]** A. Veliz-Cuba et al. (2013), *AND-NOT logic framework for steady state
  analysis of Boolean network models*, Applied Mathematics & Information Sciences
  7, 1263–1274. [Preprint](https://arxiv.org/abs/1211.5633). Representaciones con
  auxiliares, distintas de la eliminación usada aquí.
- **[R9]** J. A. Aledo, E. Goles, M. Montalva-Medel, P. Montealegre y J. C. Valverde
  (2023), *Symmetrizable Boolean networks*, Information Sciences 626, 787–804.
  [Texto institucional](https://ruidera.uclm.es/server/api/core/bitstreams/d3daaf59-63c7-4a36-95f5-23aec3e15244/content).
  Relación entre homogeneidad, signos, grafos no dirigidos y simetría. No implica
  preservación de períodos bajo la reducción de este proyecto.
- **Datos:** [BBM](https://github.com/sybila/biodivine-boolean-models), revisión en
  [manifest.json](../data/raw/manifest.json), con publicaciones y enlaces de origen
  conservados para cada modelo.
