# Análisis del dataset

Fuente: `SIA-PCA/europe.csv` (28 países × 7 variables).

## Estadísticas por variable

| Variable             |      Media | Desvío (ddof=1) |      Min |        Max |
| -------------------- | ---------: | --------------: | -------: | ---------: |
| Area (km²)           | 166 422.54 |      165 538.68 | 2 586.00 | 603 550.00 |
| GDP (USD per cápita) |  31 860.71 |       14 502.12 | 7 200.00 |  80 600.00 |
| Inflation (%)        |       3.34 |            1.40 |     0.20 |       8.00 |
| Life.expect (años)   |      78.12 |            3.19 |    68.74 |      81.86 |
| Military (% GDP)     |       1.61 |            0.80 |     0.00 |       4.30 |
| Pop.growth (%)       |       0.12 |            0.50 |    −0.80 |       1.14 |
| Unemployment (%)     |       9.92 |            4.68 |     2.80 |      21.70 |

## Notas

- **Diferencia de escalas enorme**: `Area` está en cinco órdenes de magnitud, `Pop.growth` en décimas — por eso se estandariza z-score antes de Kohonen / Oja.
- **Variables con desvío comparable a la media** (alto coeficiente de variación): `Area`, `Pop.growth`, `Unemployment` — son las que más empujan a separar países.
- **Variables compactas** (bajo CV): `Life.expect` (CV ≈ 0.04) está casi constante alrededor de 78-82 años, salvo Ucrania (68.7) que tira el min.
- Los valores `Min`/`Max` corresponden mayormente a outliers: Luxemburgo arriba en GDP (80.6k), Ucrania abajo en GDP (7.2k) y Life.expect, España arriba en Unemployment (21.7), Islandia en cero en Military.
