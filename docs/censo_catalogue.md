# Cell Collective: instancias archivadas en BBM

Instancias recuperadas: **78**; clasificadas antes: **78**. Reducciones completas: **312/312**; certificados SMT: **312**.

Los recuentos son por instancia/version, no por ejecución. «Algún orden» significa al menos uno de los cuatro órdenes probados; un resultado negativo no prueba imposibilidad para todos los órdenes.

Las entradas se conservan como parámetros libres. La tabla principal excluye sus identidades artificiales del censo de signos. Los JSON incluyen también el análisis de todas las reglas, con esas identidades.

Se admiten constantes en las familias. Las familias MIN/MAX, de puertas y afines exigen al menos una regla interna no constante; las redes vacías/solo entradas/solo constantes tienen fila propia.

| Propiedad | Original | Reducida: first | Reducida: algún orden |
|---|---:|---:|---:|
| Uniforme respecto de NOT (incluye casos vacíos) | 9 | 24 | 28 |
| Uniforme NOT con alguna regla interna no constante | 9 | 15 | 19 |
| MIN/MAX (AND/OR/NOT) y out-uniform | 4 | 8 | 12 |
| AND/OR/NAND/NOR y out-uniform | 2 | 2 | 4 |
| Homogénea MIN y uniforme NOT | 0 | 6 | 9 |
| Homogénea MAX y uniforme NOT | 2 | 3 | 6 |
| Una misma puerta en todas las reglas no constantes | 1 | 2 | 4 |
| AND positiva | 0 | 1 | 1 |
| OR positiva | 1 | 2 | 3 |
| Afín (ecuaciones lineales sobre F2) | 0 | 1 | 2 |
| MIN/MAX sin exigir uniformidad NOT | 8 | 9 | 13 |
| Cada regla es unate (condición local) | 68 | 49 | 56 |
| Sin reglas internas no constantes | 0 | 9 | 10 |

## Candidatos con reducción efectiva

La pertenencia a una familia no certifica por sí sola todas las hipótesis de un teorema. Hay que revisar las entradas, los bucles y la reciprocidad antes de aplicar resultados sobre grafos no dirigidos.

| ID | Nombre | Orden | Nodos antes → después | Entradas | MIN | MAX | Afín | PF exactos |
|---|---|---|---:|---:|---|---|---|---:|
| 007 | CORTICAL-AREA-DEVELOPMENT | first | 5 → 1 | 0 | True | True | True | 2 |
| 003 | MAMMALIAN-CELL-CYCLE | first | 20 → 2 | 1 | True | False | False | 3 |
| 049 | OXIDATIVE-STRESS-PATHWAY | first | 19 → 2 | 1 | True | False | False | 1 |
| 054 | PC12-CELL-DIFFERENTIATION | min_degree | 62 → 2 | 1 | False | True | False | 3 |
| 031 | CELL-CYCLE-TRANSCRIPTION | first | 9 → 3 | 0 | True | False | False | 1 |
| 015 | NEUROTRANSMITTER-SIGNALING-PATHWAY | first | 16 → 3 | 2 | True | False | False | 2 |
| 061 | TUMOR-MICROENVIRONMENT-IN-LYMPHOBLASTIC-LEUKEAMIA | min_growth | 26 → 3 | 2 | True | False | False | 2 |
| 069 | IRON-ACQUISITION-AND-STRESS-RESPONSE | min_degree | 22 → 3 | 2 | True | True | True | 0 |
| 068 | AURORA-KINASE-A-IN-NEUROBLASTOMA | min_growth | 23 → 6 | 4 | True | False | False | 16 |
| 052 | SEPTATION-INITIATION-NETWORK | min_degree | 31 → 10 | 8 | False | True | False | pendiente |
| 009 | YEAST-APOPTOSIS | first | 73 → 15 | 13 | False | True | False | pendiente |
| 056 | IGVH-MUTATIONS-IN-LYMPHOCYTIC-LEUKEMIA | first | 91 → 26 | 25 | True | False | False | pendiente |

## Funciones de los candidatos

### 007: CORTICAL-AREA-DEVELOPMENT (first)

```text
v_Fgf8 = v_Fgf8
```

Traza y certificado: [first.json](../results/catalogue/007/first.json).

### 003: MAMMALIAN-CELL-CYCLE (first)

```text
v_IGF1R = !v_EGF & v_IGF1R
v_EGF = v_EGF
```

Traza y certificado: [first.json](../results/catalogue/003/first.json).

### 049: OXIDATIVE-STRESS-PATHWAY (first)

```text
v_ARE = !v_ARE & v_Stress
v_Stress = v_Stress
```

Traza y certificado: [first.json](../results/catalogue/049/first.json).

### 054: PC12-CELL-DIFFERENTIATION (min_degree)

```text
v_AP1 = v_AP1 | v_NGF
v_NGF = v_NGF
```

Traza y certificado: [min_degree.json](../results/catalogue/054/min_degree.json).

### 031: CELL-CYCLE-TRANSCRIPTION (first)

```text
v_SFF = v_SFF & !v_YHP1 & !v_YOX1
v_YHP1 = v_SFF & !v_YHP1 & !v_YOX1
v_YOX1 = v_SFF & !v_YHP1 & !v_YOX1
```

Traza y certificado: [first.json](../results/catalogue/031/first.json).

### 015: NEUROTRANSMITTER-SIGNALING-PATHWAY (first)

```text
v_Dopamine = !v_Dopamine & v_Tryosine_hydroxylase
v_Glutamate = v_Glutamate
v_Tryosine_hydroxylase = v_Tryosine_hydroxylase
```

Traza y certificado: [first.json](../results/catalogue/015/first.json).

### 061: TUMOR-MICROENVIRONMENT-IN-LYMPHOBLASTIC-LEUKEAMIA (min_growth)

```text
v_Gfi1_H = !v_Gfi1_H & v_lTLR
v_Cx43_M = v_Cx43_M
v_lTLR = v_lTLR
```

Traza y certificado: [min_growth.json](../results/catalogue/061/min_growth.json).

### 069: IRON-ACQUISITION-AND-STRESS-RESPONSE (min_degree)

```text
v_LIP = !v_LIP
v_Superoxide = v_Superoxide
v__Iron = v__Iron
```

Traza y certificado: [min_degree.json](../results/catalogue/069/min_degree.json).

### 068: AURORA-KINASE-A-IN-NEUROBLASTOMA (min_growth)

```text
v_AURKAActive = v_AURKAActive
v_CentrosomeMat = v_AURKAActive & !v_CentrosomeMat
v_AJUBA = v_AJUBA
v_GSK3B = v_GSK3B
v_MTCanAct = v_MTCanAct
v_STMNCanAct = v_STMNCanAct
```

Traza y certificado: [min_growth.json](../results/catalogue/068/min_growth.json).

### 052: SEPTATION-INITIATION-NETWORK (min_degree)

```text
v_cdc11 = v_cdc11 | !v_cdk_H | v_ppc89
v_cdc42 = v_cdc42
v_CK1 = v_CK1
v_cdk_0 = v_cdk_0
v_cdk_H = v_cdk_H
v_cdk_L = v_cdk_L
v_etd1 = v_etd1
v_ppc89 = v_ppc89
v_ras1 = v_ras1
v_sid2_mob1 = v_sid2_mob1
```

Traza y certificado: [min_degree.json](../results/catalogue/052/min_degree.json).

### 009: YEAST-APOPTOSIS (first)

```text
v_MT_Frag = v_H2O2 | v_HK | v_Heat | v_MT_Frag | v_RedActinDyn | v_Stress
v_PTP3 = !v_PTP3 | v_Stress
v_AbnormalTelomer = v_AbnormalTelomer
v_AceticAcid = v_AceticAcid
v_Adozelesin = v_Adozelesin
v_CPR3 = v_CPR3
v_CU2 = v_CU2
v_H2O2 = v_H2O2
v_HK = v_HK
v_Heat = v_Heat
v_MG2 = v_MG2
v_Mating = v_Mating
v_RedActinDyn = v_RedActinDyn
v_Salt = v_Salt
v_Stress = v_Stress
```

Traza y certificado: [first.json](../results/catalogue/009/first.json).

### 056: IGVH-MUTATIONS-IN-LYMPHOCYTIC-LEUKEMIA (first)

```text
v_NAB1 = v_CNR1 & !v_NAB1 & v_TGFBR3
v_ANXA2 = v_ANXA2
v_BMI1 = v_BMI1
v_CD74 = v_CD74
v_CD81 = v_CD81
v_CHST2 = v_CHST2
v_CNR1 = v_CNR1
v_CREM = v_CREM
v_CSDA = v_CSDA
v_CSNK2A2 = v_CSNK2A2
v_CUL5 = v_CUL5
v_EED = v_EED
v_FGFR1 = v_FGFR1
v_FRK = v_FRK
v_FYN = v_FYN
v_GSK3B = v_GSK3B
v_HSP90AA1 = v_HSP90AA1
v_IL10RA = v_IL10RA
v_LMNA = v_LMNA
v_RFC5 = v_RFC5
v_RRM1 = v_RRM1
v_SIAH1 = v_SIAH1
v_SKI = v_SKI
v_TCF3 = v_TCF3
v_TGFBR3 = v_TGFBR3
v_TNFRSF1B = v_TNFRSF1B
```

Traza y certificado: [first.json](../results/catalogue/056/first.json).

## Cobertura y reproducibilidad

[Manifiesto](../data/cellcollective/manifest.json), [tabla completa](../results/catalogue/summary.csv), [recuentos](../results/catalogue/counts.json), [entorno](../results/catalogue/environment.json).

La enumeración SMT de puntos fijos se limita a 256 soluciones por ejecución: «pendiente» no significa cero. La equivalencia de los conjuntos de puntos fijos se comprueba por separado, sin enumerarlos.

## Ejecuciones incompletas

Ninguna.
