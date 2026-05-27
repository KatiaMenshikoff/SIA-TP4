# Mega-experimento de capacidad: barrido fino de ruido sobre p ∈ {2, 3, 5, 6}

Variante del mega-experimento original (`hopfield/output/mega_exp/`) pero
en lugar de 5 grupos de **4 letras**, usa los 4 grupos del experimento de
capacidad (`hopfield/output/capacity/README.md`), con tamaños distintos:

| p | grupo    | letras                |
| - | -------- | --------------------- |
| 2 | `AL`     | A, L                  |
| 3 | `FUY`    | F, U, Y               |
| 5 | `GMPVZ`  | G, M, P, V, Z         |
| 6 | `JLRTVX` | J, L, R, T, V, X      |

Mismos 13 niveles de ruido (0.05–0.65), mismas 30 muestras por config,
misma taxonomía (TP/FP/FN/COMPLEMENT/CICLO).

Total: (2+3+5+6) × 13 × 30 = **6240 trials**.

Spec del experimento original:
[`docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md`](../../../docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md)

Lectura de plots y comparación con el baseline (p=4):
[`README_resultados_plots.md`](README_resultados_plots.md)

## Setup

| parámetro        | valor                                                                              |
| ---------------- | ---------------------------------------------------------------------------------- |
| Grupos           | `AL` (p=2), `FUY` (p=3), `GMPVZ` (p=5), `JLRTVX` (p=6)                             |
| Niveles de ruido | 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65       |
| Samples/config   | 30                                                                                 |
| Seed             | `1 + sample_idx`                                                                   |
| Trials totales   | (2+3+5+6) × 13 × 30 = **6240**                                                     |

Los grupos son los mismos que eligió `capacity_experiments.py` aplicando
el criterio "el grupo de `p` letras con menor `|⟨ξ_i, ξ_j⟩|` medio". O
sea: para cada p, elegimos **el mejor grupo posible** según ortogonalidad.
Eso es distinto del baseline de 4 letras, donde el rango de calidad varía
de muy bueno (`JLRX`) a muy malo (`HMNW`).

## Taxonomía

Idéntica al mega-experimento base. Ver
[`../mega_exp/README.md`](../mega_exp/README.md) para los 5 buckets.

## Resultados resumidos

### Distribución global (6240 trials)

| outcome    |    n |     % |
| ---------- | ---: | ----: |
| TP         | 3010 | 48.2% |
| COMPLEMENT | 1116 | 17.9% |
| FN         |  757 | 12.1% |
| FP         |  697 | 11.2% |
| CICLO      |  660 | 10.6% |

TP global más alto que en el baseline (48.2% vs 37.8%): cuando los
grupos están bien elegidos por ortogonalidad —incluso con p más grande
o más chico—, la red recupera mejor en promedio.

### Tasa de TP por grupo

| grupo  |   p | tasa_TP promedio |
| ------ | --: | ---------------: |
| AL     |   2 |            0.628 |
| FUY    |   3 |            0.570 |
| GMPVZ  |   5 |            0.487 |
| JLRTVX |   6 |            0.386 |

Ordenamiento estricto por p — menos patrones, mejor recuperación. Pero
ojo: comparando con el baseline (sección de plots), **GMPVZ (p=5) supera
a 3 de los 5 grupos p=4**. La cantidad no es lo único que importa.

### Tasa de TP por nivel de ruido (promedio sobre los 4 grupos)

| ruido | tasa_TP |
| ----: | ------: |
| 0.05  |   0.986 |
| 0.10  |   0.969 |
| 0.15  |   0.936 |
| 0.20  |   0.882 |
| 0.25  |   0.830 |
| 0.30  |   0.714 |
| 0.35  |   0.523 |
| 0.40  |   0.373 |
| 0.45  |   0.236 |
| 0.50  |   0.143 |
| 0.55  |   0.078 |
| 0.60  |   0.042 |
| 0.65  |   0.020 |

A ruido bajo (0.05) la red recupera **98.6%** vs **73.8%** en el baseline.
La diferencia se debe sobre todo a `HMNW` y `BDOX` arrastrando al
baseline hacia abajo (sus tasas de TP son ~0.18 y ~0.21).

### Outcomes por nivel de ruido (480 trials por fila)

```
outcome  CICLO  COMPLEMENT   FN   FP   TP
noise
0.05        10           0    0    0  470
0.10        18           1    3    0  458
0.15        25           0   16    2  437
0.20        37           2   31    7  403
0.25        41           6   51   12  370
0.30        49          29   65   31  306
0.35        61          48   84   74  213
0.40        65          79  102   85  149
0.45        73         126   78  108   95
0.50        68         159   82  114   57
0.55        69         180   82  120   29
0.60        79         212   84   89   16
0.65        65         274   79   55    7
```

Tres observaciones notables (contra el baseline):

1. **A ruido muy bajo (0.05) no hay COMPLEMENT ni FP**: la red recupera
   o cicla, no se confunde de letra. En el baseline ya había 30
   COMPLEMENTs y 120 FPs a 0.05. La causa: los grupos `AL`, `FUY`, etc.
   son **mucho más ortogonales** que la mezcla baseline.
2. **FN aparece antes y crece más**: a 0.20, FN=31 vs 14 en baseline.
   Con p=2 o p=3, el paisaje de energía tiene menos atractores
   almacenados, así que un input ruidoso tiene más chance de caer en un
   espurio mixto en lugar de "rebotar" a otro almacenado.
3. **COMPLEMENT mucho más bajo a ruido alto**: a 0.65, COMPLEMENT=274 vs
   395 en baseline. Con pocos patrones almacenados, hay menos antipodales
   donde caer.

## Archivos en este directorio

| archivo                    | filas | columnas |
| -------------------------- | ----: | -------: |
| `trials.csv`               |  6240 |       16 |
| `stats_by_config.csv`      |   208 |       14 |
| `stats_by_group_noise.csv` |    52 |       13 |
| `representatives.csv`      |   208 |        4 |
| `trajectories.csv`         |   895 |       31 |
| `io_patterns.csv`          |  5200 |        7 |

Mismos esquemas que el baseline. `trials.csv` tiene una columna extra
`p` (cantidad de patrones almacenados en el grupo).

## Cómo regenerar

```bash
# Correr el barrido
PYTHONPATH=hopfield python3 hopfield/noise_sweep_capacity_experiment.py

# Plots del experimento solo (los 16 plots del mega-experimento, adaptados a estos 4 grupos)
python3 hopfield/plot_mega_exp.py --input hopfield/output/mega_exp_capacity

# Plots de comparación cross-experimento (capacity vs baseline p=4)
python3 hopfield/plot_capacity_comparison.py
```

`plot_mega_exp.py` deriva grupos y niveles del propio `trials.csv`, así
que funciona igual para baseline y capacity.
