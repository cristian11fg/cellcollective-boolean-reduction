# Cell Collective: catálogo público directo

Instancias recuperadas: **84**; clasificadas antes: **83**. Reducciones completas: **332/336**; certificados SMT: **332**.

Los recuentos son por instancia/version, no por ejecución. «Algún orden» significa al menos uno de los cuatro órdenes probados; un resultado negativo no prueba imposibilidad para todos los órdenes.

Las entradas se conservan como parámetros libres. La tabla principal excluye sus identidades artificiales del censo de signos. Los JSON incluyen también el análisis de todas las reglas, con esas identidades.

Se admiten constantes en las familias. Las familias MIN/MAX, de puertas y afines exigen al menos una regla interna no constante; las redes vacías/solo entradas/solo constantes tienen fila propia.

| Propiedad | Original | Reducida: first | Reducida: algún orden |
|---|---:|---:|---:|
| Uniforme respecto de NOT (incluye casos vacíos) | 8 | 24 | 28 |
| Uniforme NOT con alguna regla interna no constante | 8 | 15 | 19 |
| MIN/MAX (AND/OR/NOT) y out-uniform | 3 | 9 | 13 |
| AND/OR/NAND/NOR y out-uniform | 2 | 3 | 5 |
| Homogénea MIN y uniforme NOT | 0 | 7 | 10 |
| Homogénea MAX y uniforme NOT | 2 | 4 | 7 |
| Una misma puerta en todas las reglas no constantes | 1 | 3 | 5 |
| AND positiva | 0 | 2 | 2 |
| OR positiva | 1 | 3 | 4 |
| Afín (ecuaciones lineales sobre F2) | 0 | 2 | 3 |
| MIN/MAX sin exigir uniformidad NOT | 8 | 10 | 14 |
| Cada regla es unate (condición local) | 76 | 51 | 58 |
| Sin reglas internas no constantes | 0 | 9 | 10 |

## Candidatos con reducción efectiva

La pertenencia a una familia no certifica por sí sola todas las hipótesis de un teorema. Hay que revisar las entradas, los bucles y la reciprocidad antes de aplicar resultados sobre grafos no dirigidos.

| ID | Nombre | Orden | Nodos antes → después | Entradas | MIN | MAX | Afín | PF exactos |
|---|---|---|---:|---:|---|---|---|---:|
| 2035_1 | Cortical Area Development | first | 5 → 1 | 0 | True | True | True | 2 |
| 2172_1 | Cholesterol Regulatory Pathway | first | 34 → 2 | 0 | True | True | True | 4 |
| 1607_1 | Mammalian Cell Cycle | first | 20 → 2 | 1 | True | False | False | 3 |
| 3512_1 | Oxidative Stress Pathway | first | 19 → 2 | 1 | True | False | False | 1 |
| 4775_1 | PC12 Cell Differentiation | min_degree | 62 → 2 | 1 | False | True | False | 3 |
| 2202_1 | Neurotransmitter Signaling Pathway | first | 16 → 3 | 0 | True | False | False | 2 |
| 2681_1 | Cell Cycle Transcription by Coupled CDK and Network Oscillators | first | 9 → 3 | 0 | True | False | False | 1 |
| 4942_1 | Pro-inflammatory Tumor Microenvironment in Acute Lymphoblastic Leukemia | min_growth | 26 → 3 | 0 | True | False | False | 2 |
| 7926_1 | Iron acquisition and oxidative stress response in aspergillus fumigatus. | min_degree | 22 → 3 | 2 | True | True | True | 0 |
| 7916_1 | Aurora Kinase A in Neuroblastoma | min_growth | 23 → 6 | 4 | True | False | False | 16 |
| 4705_1 | Septation Initiation Network | min_degree | 31 → 10 | 8 | False | True | False | pendiente |
| 2135_1 | Yeast Apoptosis | first | 73 → 15 | 13 | False | True | False | pendiente |
| 4783_1 |  IGVH mutations in chronic lymphocytic leukemia. | first | 91 → 26 | 0 | True | False | False | pendiente |

## Funciones de los candidatos

### 2035_1: Cortical Area Development (first)

```text
v_Fgf8 = v_Fgf8
```

Traza y certificado: [first.json](../results/live/2035_1/first.json).

### 2172_1: Cholesterol Regulatory Pathway (first)

```text
v_Statins = v_Statins
v_Acetyl_CoA = v_Acetyl_CoA
```

Traza y certificado: [first.json](../results/live/2172_1/first.json).

### 1607_1: Mammalian Cell Cycle (first)

```text
v_IGF1R = !v_EGF & v_IGF1R
v_EGF = v_EGF
```

Traza y certificado: [first.json](../results/live/1607_1/first.json).

### 3512_1: Oxidative Stress Pathway (first)

```text
v_ARE = !v_ARE & v_Stress
v_Stress = v_Stress
```

Traza y certificado: [first.json](../results/live/3512_1/first.json).

### 4775_1: PC12 Cell Differentiation (min_degree)

```text
v_AP1 = v_AP1 | v_NGF
v_NGF = v_NGF
```

Traza y certificado: [min_degree.json](../results/live/4775_1/min_degree.json).

### 2202_1: Neurotransmitter Signaling Pathway (first)

```text
v_Dopamine = !v_Dopamine & v_Tryosine_hydroxylase
v_Tryosine_hydroxylase = v_Tryosine_hydroxylase
v_Glutamate = v_Glutamate
```

Traza y certificado: [first.json](../results/live/2202_1/first.json).

### 2681_1: Cell Cycle Transcription by Coupled CDK and Network Oscillators (first)

```text
v_SFF = v_SFF & !v_YHP1 & !v_YOX1
v_YHP1 = v_SFF & !v_YHP1 & !v_YOX1
v_YOX1 = v_SFF & !v_YHP1 & !v_YOX1
```

Traza y certificado: [first.json](../results/live/2681_1/first.json).

### 4942_1: Pro-inflammatory Tumor Microenvironment in Acute Lymphoblastic Leukemia (min_growth)

```text
v_Gfi1_H = !v_Gfi1_H & v_lTLR
v_Cx43_M = v_Cx43_M
v_lTLR = v_lTLR
```

Traza y certificado: [min_growth.json](../results/live/4942_1/min_growth.json).

### 7926_1: Iron acquisition and oxidative stress response in aspergillus fumigatus. (min_degree)

```text
v_LIP = !v_LIP
v_Superoxide = v_Superoxide
v_Iron = v_Iron
```

Traza y certificado: [min_degree.json](../results/live/7926_1/min_degree.json).

### 7916_1: Aurora Kinase A in Neuroblastoma (min_growth)

```text
v_CentrosomeMat = v_AURKAActive & !v_CentrosomeMat
v_AURKAActive = v_AURKAActive
v_AJUBA = v_AJUBA
v_STMNCanAct = v_STMNCanAct
v_MTCanAct = v_MTCanAct
v_GSK3B = v_GSK3B
```

Traza y certificado: [min_growth.json](../results/live/7916_1/min_growth.json).

### 4705_1: Septation Initiation Network (min_degree)

```text
v_cdc42 = v_cdc42
v_cdc11 = v_cdc11 | !v_cdk_H | v_ppc89
v_cdk_0 = v_cdk_0
v_sid2_mob1 = v_sid2_mob1
v_cdk_L = v_cdk_L
v_ras1 = v_ras1
v_CK1 = v_CK1
v_etd1 = v_etd1
v_ppc89 = v_ppc89
v_cdk_H = v_cdk_H
```

Traza y certificado: [min_degree.json](../results/live/4705_1/min_degree.json).

### 2135_1: Yeast Apoptosis (first)

```text
v_MT_Frag = v_H2O2 | v_HK | v_Heat | v_MT_Frag | v_RedActinDyn | v_Stress
v_PTP3 = !v_PTP3 | v_Stress
v_CU2 = v_CU2
v_Stress = v_Stress
v_Adozelesin = v_Adozelesin
v_CPR3 = v_CPR3
v_MG2 = v_MG2
v_Heat = v_Heat
v_AbnormalTelomer = v_AbnormalTelomer
v_Salt = v_Salt
v_AceticAcid = v_AceticAcid
v_RedActinDyn = v_RedActinDyn
v_H2O2 = v_H2O2
v_HK = v_HK
v_Mating = v_Mating
```

Traza y certificado: [first.json](../results/live/2135_1/first.json).

### 4783_1:  IGVH mutations in chronic lymphocytic leukemia. (first)

```text
v_CSDA = v_CSDA
v_HSP90AA1 = v_HSP90AA1
v_BMI1 = v_BMI1
v_CUL5 = v_CUL5
v_NAB1 = v_CNR1 & !v_NAB1 & v_TGFBR3
v_SKI = v_SKI
v_CD74 = v_CD74
v_CNR1 = v_CNR1
v_CD81 = v_CD81
v_CHST2 = v_CHST2
v_SIAH1 = v_SIAH1
v_ANXA2 = v_ANXA2
v_IL10RA = v_IL10RA
v_RRM1 = v_RRM1
v_CREM = v_CREM
v_LMNA = v_LMNA
v_RFC5 = v_RFC5
v_FYN = v_FYN
v_EED = v_EED
v_TGFBR3 = v_TGFBR3
v_CSNK2A2 = v_CSNK2A2
v_TCF3 = v_TCF3
v_FRK = v_FRK
v_FGFR1 = v_FGFR1
v_GSK3B = v_GSK3B
v_TNFRSF1B = v_TNFRSF1B
```

Traza y certificado: [first.json](../results/live/4783_1/first.json).

## Cobertura y reproducibilidad

[Manifiesto](../data/live/manifest.json), [tabla completa](../results/live/summary.csv), [recuentos](../results/live/counts.json), [entorno](../results/live/environment.json).

La enumeración SMT de puntos fijos se limita a 256 soluciones por ejecución: «pendiente» no significa cero. La equivalencia de los conjuntos de puntos fijos se comprueba por separado, sin enumerarlos.

## Ejecuciones incompletas

- 8558_1, first: No completed result
- 8558_1, min_degree: No completed result
- 8558_1, min_growth: No completed result
- 8558_1, random: No completed result
