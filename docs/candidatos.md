# Funciones locales de los dos candidatos

Este documento recoge las dos redes del piloto que resultaron **out-uniformes en signo**: `Toll Pathway of Drosophila` (BBM 029) y `Cell Cycle Transcription` (BBM 031). Las expresiones usan `¬` para NOT, `∧` para AND y `∨` para OR.

La comprobación debe hacerse con el mismo orden `first` usado por el experimento. En cada paso se elimina un nodo sin dependencia propia y se sustituye su función en las funciones que todavía lo utilizan.

## 1. Toll Pathway of Drosophila (BBM 029)

### Funciones originales

Entradas protegidas: `Nec`, `Slmb`. Salida biológica: `Targets`.

```text
Cactus  = ¬(Pelle ∧ Slmb)
Dif     = ¬Cactus
Dorsal  = ¬Cactus
MyD88   = Toll
Pelle   = Tube
Spz     = ¬Nec
Targets = Dorsal ∨ Dif
Toll    = Spz
Tube    = MyD88
```

### Sustituciones que se pueden verificar a mano

1. Eliminar `Cactus`:

   ```text
   Dif    = ¬Cactus = ¬[¬(Pelle ∧ Slmb)] = Pelle ∧ Slmb
   Dorsal = Pelle ∧ Slmb
   ```

2. Eliminar `Dif` y después `Dorsal`:

   ```text
   Targets = Dif ∨ Dorsal
           = (Pelle ∧ Slmb) ∨ (Pelle ∧ Slmb)
           = Pelle ∧ Slmb
   ```

3. Eliminar `MyD88` y `Pelle`:

   ```text
   Tube  = MyD88 = Toll
   Pelle = Tube
   ```

4. Eliminar `Spz`:

   ```text
   Toll = Spz = ¬Nec
   ```

5. Eliminar `Targets`, `Toll` y `Tube`:

   ```text
   Targets = Pelle ∧ Slmb = Tube ∧ Slmb
   Tube    = Toll = ¬Nec
   Pelle   = ¬Nec
   MyD88   = ¬Nec
   ```

Por tanto, al proteger las dos entradas, la red reducida solo contiene:

```text
Nec  = Nec
Slmb = Slmb
```

La reconstrucción de cualquier punto fijo reducido se comprueba con las fórmulas compactas:

```text
Spz = Toll = Tube = Pelle = MyD88 = ¬Nec
Dif = Dorsal = Targets = ¬Nec ∧ Slmb
Cactus = ¬(¬Nec ∧ Slmb)
```

Hay cuatro puntos fijos, uno por cada asignación de `(Nec, Slmb)`. Por ejemplo, para `(Nec,Slmb)=(0,1)` se obtiene `Spz=Toll=Tube=Pelle=MyD88=1`, `Dif=Dorsal=Targets=1` y `Cactus=0`.

## 2. Cell Cycle Transcription (BBM 031)

Esta red no tiene entradas protegidas.

### Funciones originales

```text
ACE2 = SFF
CLN3 = SWI5 ∧ ACE2 ∧ ¬(YOX1 ∨ YHP1)
HCM1 = MBF ∧ SBF
MBF  = CLN3
SBF  = (MBF ∧ ¬(YHP1 ∨ YOX1)) ∨ (CLN3 ∧ ¬(YHP1 ∨ YOX1))
SFF  = SBF ∧ HCM1
SWI5 = SFF
YHP1 = SBF ∨ MBF
YOX1 = MBF ∧ SBF
```

Para abreviar, sea `t = ¬YHP1 ∧ ¬YOX1`, que es equivalente a `¬(YOX1 ∨ YHP1)`.

### Sustituciones en el orden de reducción

1. Eliminar `ACE2`:

   ```text
   CLN3 = SWI5 ∧ SFF ∧ t
   ```

2. Eliminar `CLN3`:

   ```text
   MBF = SWI5 ∧ SFF ∧ t
   ```

   En `SBF`, ambas ramas coinciden:

   ```text
   SBF = (MBF ∧ t) ∨ (CLN3 ∧ t) = SWI5 ∧ SFF ∧ t
   ```

3. Eliminar `HCM1`:

   ```text
   SFF = SBF ∧ (MBF ∧ SBF)
   ```

4. Eliminar `MBF` y después `SBF`. Al sustituir las expresiones del paso anterior, la función que queda para cada uno de los tres nodos supervivientes es:

   ```text
   q = SWI5 ∧ SFF ∧ ¬YHP1 ∧ ¬YOX1
   ```

   Es decir, tras esas sustituciones:

   ```text
   SFF  = q
   YHP1 = q
   YOX1 = q
   ```

5. Eliminar `SWI5`, usando `SWI5=SFF`:

   ```text
   q = SFF ∧ ¬YHP1 ∧ ¬YOX1
   ```

La red reducida es, por tanto,

```text
SFF  = SFF ∧ ¬YHP1 ∧ ¬YOX1
YHP1 = SFF ∧ ¬YHP1 ∧ ¬YOX1
YOX1 = SFF ∧ ¬YHP1 ∧ ¬YOX1
```

### Punto fijo reducido y reconstrucción

En un punto fijo, `SFF=YHP1=YOX1=q`. Si `q=1`, la expresión derecha de `q` contiene `¬YHP1=0`, contradicción. Luego `q=0`, y el único punto fijo reducido es `(SFF,YHP1,YOX1)=(0,0,0)`.

La elevación por las ecuaciones originales da el único punto fijo de la red completa:

```text
ACE2=CLN3=HCM1=MBF=SBF=SFF=SWI5=YHP1=YOX1=0
```

Estas identidades son además un ejemplo especialmente claro para el artículo: la reducción convierte la red en una función local `MIN` con literales negados y permite demostrar el punto fijo sin enumerar los `2^9` estados originales.
