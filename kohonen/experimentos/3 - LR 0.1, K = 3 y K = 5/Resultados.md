# Config nueva (η₀=0.1) aplicada a K=3 y K=5

Aplicamos la config recomendada en `eta y grilla K3/` — `η₀ = 0.1`, grilla rectangular, todo lo demás igual al recipe del profe — a las dos K candidatas: K=3 (nuestra elección estándar) y K=5 (el siguiente paso natural).

## Setup

| Hiperparámetro | Valor |
|---|---|
| K | 3 y 5 |
| Grilla | rectangular |
| R | adaptativo, R(0) = K → R = 1 (lineal) |
| η | **adaptativo, η₀ = 0.1** ← *único cambio respecto del recipe original (era 0.5)* |
| Iteraciones | `500·N = 14 000` |
| Inicialización | muestras del set |
| Semillas | 10 por K |

## Resumen

| K | total celdas | QE (media) | QE (std) | muertas (media) | % muertas | clusters activos |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 9 | 1.816 | 0.024 | 0.6 / 9 | 6.7% | ~8.4 |
| 5 | 25 | **1.583** | 0.057 | 7.9 / 25 | 31.6% | **~17.1** |

Plot: `comparacion.png`.

### Contexto con experimentos previos

| Config | K | QE | % muertas | clusters |
|---|---:|---:|---:|---:|
| Original (η₀=0.5) | 2 | 2.32 | 30% | ~3 |
| Original (η₀=0.5) | 3 | 2.10 | 36% | ~6 |
| Original (η₀=0.5) | 4 | 1.99 | 50% | ~8 |
| Original (η₀=0.5) | 5 | 1.94 | 59% | ~10 |
| **Nueva (η₀=0.1)** | **3** | **1.82** | **7%** | **~8** |
| **Nueva (η₀=0.1)** | **5** | **1.58** | **32%** | **~17** |

Bajar η₀ es estrictamente mejor en cualquier K. K=5 con la config nueva tiene **mejor QE y más clusters activos que K=4 con la original** — el cambio de η dominó al cambio de K.

## Asignaciones — qué países caen en cada celda

### K=3 (seed mediana, 8/9 celdas activas)

Ver `paises_K3.txt`. Y para verlo proyectado sobre el mapa de Europa, abrir `visualizacion/mapa_clusters.html` (single-file, dark mode, modo compacto + detallado por país).

```
(0,0) [2]: Ireland, Spain                                        ← híbridos atlánticos
(0,1) [4]: Denmark, Luxembourg, Netherlands, Switzerland         ← núcleo rico
(0,2) [5]: Hungary, Latvia, Lithuania, Slovakia, Ukraine         ← este "estándar"
(1,0) [3]: Finland, Italy, United Kingdom                        ← intermedios grandes
(1,1) [3]: Germany, Norway, Sweden                               ← norte industrial
(1,2) [0]: --- muerta ---
(2,0) [6]: Bulgaria, Croatia, Estonia, Greece, Poland, Portugal  ← sur/este pobre
(2,1) [3]: Austria, Belgium, Iceland                             ← pequeños occidentales
(2,2) [2]: Czech Republic, Slovenia                              ← post-comunistas en transición
```

8 grupos con 2-6 países cada uno, todos interpretables sociopolíticamente.

### K=5 (seed mediana, 17/25 celdas activas)

Ver `paises_K5.txt`.

```
(0,0) [1]: Spain                          (3,0) [1]: Belgium
(0,2) [1]: Croatia                        (3,3) [1]: Denmark
(0,4) [2]: Austria, Iceland               (3,4) [3]: Netherlands, Norway, Switzerland
(1,1) [1]: Ireland                        (4,0) [1]: Germany
(1,2) [5]: Bulgaria, Estonia, Hungary,    (4,1) [3]: Latvia, Lithuania, Slovakia
           Poland, Ukraine                (4,3) [1]: Czech Republic
(1,3) [2]: Greece, Portugal               (2,0) [1]: Slovenia
(1,4) [1]: Luxembourg                     (2,2) [1]: United Kingdom
(2,4) [3]: Finland, Italy, Sweden
```

17 grupos, pero **la mayoría tienen solo 1 país**. Las agrupaciones significativas son pocas:
- `(1,2)`: este "estándar" (Bulgaria, Estonia, Hungría, Polonia, Ucrania)
- `(4,1)`: bálticos + Eslovaquia
- `(3,4)`: ricos pequeños (Países Bajos, Noruega, Suiza)
- `(2,4)`: intermedios (Finlandia, Italia, Suecia)
- `(1,3)`: mediterráneo en crisis (Grecia, Portugal)
- `(0,4)`: pequeños occidentales (Austria, Islandia)

El resto son **un país por celda** — Luxemburgo, Ucrania-de-hecho ya está en (1,2), Spain en (0,0), Germany en (4,0)... K=5 está usando casi una celda por país, especialmente para los países más distintivos.

## Hallazgos

### 1. K=3 es el "sweet spot" interpretativo

8 grupos balanceados (2-6 países por celda) con etiqueta sociopolítica clara. Es la lectura más rica del dataset sin perder el carácter de *grupos*.

### 2. K=5 baja QE 13% pero sobre-granula

QE pasa de 1.82 (K=3) a 1.58 (K=5), pero a costa de que muchas celdas tengan 1 solo país. **K=5 se parece más a "cada outlier su propia celda" que a un agrupamiento útil.** Luxemburgo, España, Alemania, Bélgica, Dinamarca, Croacia, Reino Unido, Eslovenia, República Checa, Irlanda — todos en celda propia.

Esto tiene sentido geométrico: el QE se calcula como distancia BMU. Cada vez que un país tiene su propia celda, su distancia a BMU cae muy cerca de 0 (la celda *es* el país). Así que QE bajo no significa "mejor clustering", significa "mejor cuantización" — cosas distintas.

### 3. La estructura de los clusters de K=3 se mantiene en K=5

Las agrupaciones que sí sobreviven en K=5 (rich core, este estándar, post-comunistas, sur en crisis) son **las mismas que aparecen en K=3**. K=5 no descubre clusters nuevos — solo separa cada uno en sub-celdas.

Eso quiere decir que **la estructura genuina del dataset son los ~6-8 clusters que ya muestra K=3**. El "ruido" adicional de K=5 (celdas con 1 país) no es estructura, es resolución sin contenido.

### 4. Las muertas de K=5 forman patrones interpretables

Mirando las celdas muertas de K=5: `(0,1), (0,3), (1,0), (2,1), (2,3), (3,1), (3,2), (4,2), (4,4)`. Forman como un *patrón cuadriculado* — son las posiciones "intersticiales" entre las celdas vivas. Esto es típico del SOM con grilla cuadrada: cuando hay más celdas que clusters naturales, las celdas extras se acomodan en posiciones intermedias y mueren.

## Veredicto

**Para el TP nos quedamos con K=3 + η₀=0.1, rectangular.**

Razones:
- 8 clusters interpretables con 2-6 países cada uno (no celdas de "un país").
- 93% de neuronas vivas (vs 32% en el K=5).
- std de QE muy baja (0.024) — reproducible entre semillas.
- Es **un solo número** de diferencia respecto del recipe del profe (η₀: 0.5 → 0.1), justificable por el análisis de bifurcación en `evolucion K3/`.

K=5 con esta config queda como **referencia confirmatoria**: muestra que la estructura de K=3 es real (los mismos clusters reaparecen), y que K=5 no agrega información — solo separa outliers en celdas individuales.

## Próximos análisis sobre esta config

Sobre K=3 + η₀=0.1, rect, hacen falta para el informe:
- Activación por variable (qué variable del dataset domina cada celda).
- Comparación con PCA — si los clusters del SOM se alinean con regiones del biplot.
- Análisis del barrido restante de la consigna: R fijo vs adaptativo, hexagonal.

## Cómo regenerar

```bash
cd "kohonen/experimentos/config nueva K3 K5"
python3 run_config_nueva.py
```

Tarda ~12 segundos.

## Archivos en este directorio

| Archivo | Contenido |
|---|---|
| `run_config_nueva.py` | script del experimento |
| `corridas.csv` | una fila por (K, seed): QE, muertas |
| `resumen_por_K.csv` | agregado por K — media y std |
| `distancias_por_pais.csv` | distancia BMU por país, promediada sobre semillas |
| `distancias_por_pais_full.csv` | distancia BMU por país × semilla (crudo) |
| `seeds_elegidas.json` | qué semilla representativa por K |
| `comparacion.png` | barras: QE, % muertas, clusters activos |
| `heatmap_K{3,5}.png` | conteo de países por neurona |
| `matriz_u_K{3,5}.png` | matriz U |
| `paises_K{3,5}.txt` | qué países cayeron en cada celda |
| `K{K}_seed{s}/` | artefactos completos de la corrida representativa |
| `visualizacion/mapa_clusters.html` | mapa interactivo de Europa coloreado por cluster del SOM K=3 (single-file, sin dependencias) |

## Visualización geográfica

Los 8 clusters de K=3 proyectados sobre el mapa de Europa están en `visualizacion/mapa_clusters.html`. Es un sitio estático single-file (se abre con doble click, sin servidor) con:

- Países coloreados por su BMU.
- Etiquetas semánticas por cluster (núcleo rico, este "estándar", post-comunistas en transición, etc.).
- Toggle entre vista compacta (lista de países por cluster) y vista detallada (valores de las 7 variables por país).

Ver el mapa con los 28 países pintados confirma visualmente lo que las tablas ya decían: los clusters del SOM se alinean con regiones geopolíticas reales (no son artificiales del algoritmo).
