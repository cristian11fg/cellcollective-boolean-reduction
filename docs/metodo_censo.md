# Método del censo de Cell Collective

## Unidad de análisis y procedencia

Se conservan dos conjuntos independientes, que **no se suman**:

1. `data/live`: exportaciones directas del catálogo público de modelos booleanos
   publicados de Cell Collective. Se recorren todas las versiones anunciadas por
   cada ficha. El catálogo consultado el 16 de septiembre de 2026 devuelve 89
   modelos y 90 versiones. Esto delimita el universo accesible de esta consulta;
   no incluye modelos privados, borrados o ajenos a la categoría publicada.
2. `data/cellcollective`: todas las instancias de BBM que enlazan Cell Collective,
   sin selección por tamaño: 78, en la revisión fijada por el manifiesto. BBM puede
   incluir transformaciones, variantes o versiones históricas. Sus notas se conservan.

Cada fuente tiene manifiesto, fecha y huellas SHA-256. Se guardan los ZIP EXPR
originales y el mapa entre nombres originales e identificadores BNET.
Los números principales se cuentan por versión; se ofrecen también números por
ID de modelo cuando varias versiones pertenecen a una misma ficha.

La API del cliente oficial antiguo devolvía 404. El frontend actual indica el
prefijo `/web`; la consulta pública usada es
`https://research.cellcollective.org/web/api/model/cards/research?modelTypes=boolean&orderBy=recent&category=published&cards=10000`.
El registro de comprobación se conserva en `data/cellcollective/live_probe.json`.

## Importación y entradas

Las reglas se obtienen de `expressions.ALL.txt`. Los nombres se sustituyen por
identificadores válidos mediante correspondencia exacta, sin ejecutar código de
la fuente. Los reguladores desconocidos generan un error.

Las entradas enumeradas por `external_components.ALL.txt` se mantienen como
parámetros libres: `u'=u`. Los puntos fijos se consideran sobre todas sus
asignaciones. No se impone un estímulo concreto en el censo principal.

Algunas exportaciones EXPR omiten componentes fijados. En esos casos se consulta
el SBML original: solo se añade `x'=0` o `x'=1` si la especie omitida tiene
`constant=true`, `maxLevel=1` e `initialLevel` explícito igual a 0 o 1. Esas
correcciones están identificadas en `sbml_fixed_components`. No se interpreta
automáticamente una regla ausente como entrada libre.

La cifra de componentes de una ficha puede diferir de la de una versión. Si esto
ocurre, se exige que la cobertura de especies de la exportación coincida con el
SBML de esa versión y se conservan ambos recuentos. Los errores de descarga o
importación quedan fuera del denominador evaluado y se listan explícitamente.

## Definiciones confirmadas para este experimento

Las propiedades se calculan sobre **funciones**, después de eliminar dependencias
ficticias; no se cuentan palabras o símbolos en una expresión concreta.

- **Signo positivo de `x` en `f`:** existe un contexto donde cambiar `x` de 0 a 1
  cambia `f` de 0 a 1. Signo negativo: existe un contexto donde cambia de 1 a 0.
  Si ocurren ambas cosas, la dependencia es de signo mixto.
- **Unate local:** cada argumento esencial tiene un único signo en esa función.
- **Out-uniform / uniforme respecto de NOT:** cada variable tiene el mismo signo
  en todas las funciones en las que influye. Una dependencia de signo mixto impide
  esta propiedad. Es equivalente a poder usar una polaridad fija por variable
  en una representación unate; la sintaxis redundante del archivo no decide la clase.
- **AND/OR/NOT:** cada regla no constante es una sola conjunción o disyunción de
  literales, es decir, MIN o MAX en la terminología del borrador.
- **AND/OR/NAND/NOR:** cada regla no constante equivale a una sola de esas puertas
  sobre argumentos positivos. NAND es una disyunción de literales todos negativos;
  NOR es una conjunción de literales todos negativos.
- **Homogénea MIN/MAX:** todas las reglas no constantes son MIN, o todas MAX,
  respectivamente, y además existe uniformidad NOT por variable.
- **Homogénea de puerta:** existe una misma puerta AND, OR, NAND, NOR, COPY o NOT
  válida para todas las reglas no constantes. Se registra por separado; por sí
  sola no impone la condición global de signos en todos los casos posibles.
- **Afín:** cada regla es una suma módulo 2 de variables y una constante. Sus
  puntos fijos resuelven un sistema lineal sobre el cuerpo de dos elementos.

Se admiten constantes, registradas por separado. Las familias requieren alguna
regla interna no constante para evitar que una red vacía pertenezca a todas por
vacuidad. Las reglas unarias pueden ser a la vez MIN y MAX; los recuentos de
familias se solapan y no deben sumarse.

El censo principal de signos excluye los bucles identidad artificiales de las
entradas. Los campos `all_rules_classification` y `all_rules_after` incluyen
también esas identidades. Antes de aplicar un teorema a una red autónoma completa
debe usarse ese segundo alcance, o formular explícitamente el problema condicionado
a los parámetros de entrada. No se omiten bucles de nodos internos.

## Reducción y órdenes

Se implementan los pasos de sustitución y simplificación funcional de
[Veliz-Cuba (2011)](https://doi.org/10.1016/j.jtbi.2011.08.042). Solo se elimina
`x_i` si su función no depende esencialmente de `x_i`; se sustituye su regla en
todas las restantes. Las entradas están protegidas. Los BDD representan las
funciones exactamente y calculan el soporte esencial después de cada sustitución.

Se prueban cuatro órdenes hasta no tener nodos eliminables: `first` lexicográfico,
`min_degree` por grado entrante más saliente, `min_growth` por crecimiento estimado
de los soportes y `random` con semilla 42. El `min_growth` simbólico **no es** el
coste por tablas de verdad del piloto; la diferencia está registrada en el entorno.
Cada política inicia un gestor BDD independiente.

Las funciones se guardan en un BDD JSON compartido con raíces `final:nombre` y
`step:índice:nombre`, cargable con `dd.autoref.BDD.load`. La traza textual incluye
la función vigente al eliminar cada nodo. Las expresiones demasiado grandes
remiten al BDD, sin truncar el objeto matemático almacenado.

«Encontrada con algún orden» es una conclusión existencial sobre los cuatro
órdenes ensayados. No encontrar una familia no demuestra que ningún orden pueda
alcanzarla. Tampoco se han explorado todos los posibles puntos intermedios de
parada; estos pueden ser más interesantes para el artículo que una reducción máxima.

## Comprobación independiente

El sistema original de ecuaciones `x_i=f_i(x)` se traduce directamente del BNET
a Z3. Por otra vía se traducen el BDD reducido y las ecuaciones de la traza.
Z3 intenta encontrar una asignación que satisfaga exactamente uno de estos dos
sistemas. Si responde `unsat`, los sistemas son equivalentes. Se comprueba además
que la traza sea triangular: la regla de un nodo eliminado usa únicamente nodos
todavía presentes. Esto garantiza reconstrucción única, y por tanto biyección
de puntos fijos, sin enumerar todos los estados originales.

Las pruebas comparan el nuevo motor con las tablas de verdad del piloto y con
todas las 256 funciones de tres argumentos, y verifican que una reducción
deliberadamente corrompida no supere el certificado. La importación tiene pruebas
de nombres con espacios, prefijos comunes, colisiones y reguladores ausentes.

La enumeración de puntos fijos tiene un límite de 256 soluciones por ejecución.
Si se supera, se informa una cota inferior, nunca un recuento exacto ni cero.
Los límites de tiempo/memoria se distinguen de la irreducibilidad matemática.

## Cómo elegir el ejemplo del artículo

Se priorizan: reducción efectiva, pocas reglas internas supervivientes, funciones
legibles, uniformidad NOT, MIN/MAX y condiciones del grafo compatibles con el
resultado que se quiera ilustrar. Una familia reconocible proporciona una ruta
teórica; no sustituye la comprobación de todas las hipótesis del teorema.

Cell Cycle Transcription sigue siendo especialmente útil: con `first` quedan
tres nodos, sin entradas, con la misma función `a ∧ ¬b ∧ ¬c`. Todos tienen bucle,
el soporte es recíproco y el único punto fijo es `000`. Otros órdenes la reducen
a la red vacía, que es menos útil para explicar la estructura del borrador.

Como alternativas, las redes positivas AND/OR se conectan con
[Jarrah, Laubenbacher y Veliz-Cuba (2010)](https://arxiv.org/abs/0805.0275).
Los sistemas MIN/MAX del borrador se contrastarán con
[Aledo et al. (2020)](https://doi.org/10.1155/2020/9708347) y
[Aledo et al. (2022)](https://doi.org/10.1016/j.cam.2021.114070), comprobando
explícitamente bucles, reciprocidad y tratamiento de constantes.
[Aracena, Richard y Salinas (2014)](https://doi.org/10.1016/j.jcss.2014.04.025)
aporta cotas para AND–OR–NOT; no se presenta como fórmula exacta universal.
El manuscrito entregado por el usuario sigue identificado como borrador, sin
atribuir a resultados publicados las afirmaciones que solo aparecen en él.
