# Barrido de K grande — K ∈ {5, 8, 15, 20}

¿Qué pasa cuando metemos grillas mucho más grandes que el dataset? Con N=28 países, K=5 ya está al límite (25 celdas), K=20 son **400 celdas para 28 países** — un caso patológico a propósito.

Pregunta concreta: ¿el SOM saca provecho de tener más neuronas, o simplemente se llena de muertas y QE no mejora?

## Setup

Mismo recipe que el primer barrido (para que la comparación sea limpia):

- grilla rectangular,
- R adaptativo `R(0)=K → R=1` (lineal),
- η adaptativo `0.5 / i`,
- inicialización por muestras,
- **`500·N = 14 000` iteraciones** (no escalamos con K — eso es parte del punto: para K=20 son apenas 35 updates promedio por celda),
- 5 semillas por K.

> Nota: en SOM "serios" se suele escalar iteraciones con K². Acá mantenemos la receta del profe para apples-to-apples con el barrido chico.

## Resumen por K

| K | total neuronas | QE (media) | QE (std) | muertas (media) | % muertas | activas |
|---:|---:|---:|---:|---:|---:|---:|
| 5  | 25  | **1.939** | 0.027 | 14.8 / 25  | **59.2%** | ~10 |
| 8  | 64  | **1.900** | 0.048 | 50.6 / 64  | **79.1%** | ~13 |
| 15 | 225 | **1.835** | 0.021 | 207.6 / 225 | **92.3%** | ~17 |
| 20 | 400 | **1.862** | 0.086 | 381.4 / 400 | **95.4%** | ~19 |

Plot: `qe_y_dead_vs_k.png`.

## Hallazgos

### 1. QE se aplana — más neuronas no ayudan

Combinando con el primer barrido:

| K | QE | activas | % muertas |
|---:|---:|---:|---:|
| 2  | 2.323 | ~3 | 30% |
| 3  | 2.103 | ~6 | 36% |
| 4  | 1.987 | ~8 | 50% |
| 5  | 1.939 | ~10 | 59% |
| 8  | 1.900 | ~13 | 79% |
| 15 | 1.835 | ~17 | 92% |
| 20 | 1.862 | ~19 | 95% |

QE baja monotónicamente hasta K=15 y **rebota** en K=20 (1.835 → 1.862). De K=4 a K=20 — multiplicando neuronas por **25** — el QE solo baja 6%. Después de K=8 las ganancias son insignificantes.

### 2. La cantidad de neuronas activas converge a ~20

El número de neuronas que ganan al menos un país no crece con K²: crece sublineal y se estabiliza alrededor de 17-19, **independientemente del tamaño de la grilla**. Es como si el SOM "eligiera" cuántos clusters útiles armar y el resto sobrara.

Esto confirma una versión más fuerte de la hipótesis del primer barrido: las neuronas muertas no son víctimas de competencia, son neuronas que **nunca encontraron un país que las eligiera**. Si meto 400 neuronas, 381 quedan en zona vacía del espacio 7D y solo ~19 logran posicionarse cerca de algún país.

### 3. Variabilidad entre semillas baja con K grande

La std de % muertas baja de 19.7% (K=2) a 0.5% (K=20). Con K grande el resultado es **más reproducible**, pero solo porque siempre converge al mismo patrón patológico: muchas muertas, pocas activas, distribuidas siempre parecido.

### 4. Distancia BMU por país: tampoco mejora con K

Tabla de distancias promediadas sobre semillas, ordenada por K=5:

| País | K=5 | K=8 | K=15 | K=20 |
|---|---:|---:|---:|---:|
| Ukraine | 5.048 | 5.035 | 4.918 | 4.862 |
| Greece | 3.581 | 3.607 | 3.304 | 3.142 |
| Luxembourg | 3.563 | 3.544 | 3.453 | 3.498 |
| Spain | 3.494 | 3.410 | 3.438 | 3.424 |
| Switzerland | 2.768 | 2.713 | 2.548 | 2.658 |
| Ireland | 2.264 | 2.264 | 2.250 | 2.221 |
| Iceland | 2.161 | 2.176 | 2.091 | 2.145 |
| Norway | 2.147 | 2.071 | 1.985 | 2.146 |
| Bulgaria | 2.134 | 2.103 | 1.972 | 2.094 |
| Croatia | 2.037 | 2.016 | 1.797 | 1.891 |
| Latvia | 1.961 | 1.862 | 1.795 | 1.929 |
| United Kingdom | 1.900 | 1.877 | 1.931 | 1.768 |
| Estonia | 1.852 | 1.774 | 1.656 | 1.816 |
| Sweden | 1.767 | 1.711 | 1.721 | 1.757 |
| Germany | 1.662 | 1.628 | 1.611 | 1.571 |
| Lithuania | 1.627 | 1.528 | 1.483 | 1.583 |
| Slovenia | 1.548 | 1.544 | 1.541 | 1.497 |
| Austria | 1.510 | 1.457 | 1.326 | 1.393 |
| Czech Republic | 1.382 | 1.352 | 1.348 | 1.341 |
| Netherlands | 1.347 | 1.276 | 1.139 | 1.223 |
| Italy | 1.261 | 1.226 | 1.231 | 1.248 |
| Slovakia | 1.188 | 1.146 | 1.170 | 1.197 |
| Finland | 1.183 | 1.152 | 1.228 | 1.043 |
| Portugal | 1.153 | 1.139 | 1.041 | 1.038 |
| Belgium | 1.057 | 0.987 | 0.955 | 0.974 |
| Denmark | 0.970 | 0.910 | 0.827 | 0.822 |
| Poland | 0.960 | 1.002 | 0.959 | 0.998 |
| Hungary | 0.769 | 0.693 | 0.660 | 0.844 |

- **Ucrania** sigue siendo intratable: pasa de distancia 5.65 con K=2 a 4.86 con K=20. Aún con 400 celdas, su BMU está a ~5 unidades. *Es un outlier real, no un problema de resolución de la grilla.*
- **Países "fáciles"** (Hungría, Dinamarca, Polonia) ya están a < 1.0 desde K=5 y casi no mejoran.
- **Países intermedios** (Croatia, Estonia, Netherlands) tienen pequeñas mejoras de ~10-15% pasando de K=5 a K=20, pero nada espectacular.

### 5. Lectura visual: heatmap se vuelve ilegible

Plots: `heatmap_registros_K{5,8,15,20}.png` y `matriz_u_K{5,8,15,20}.png` (de la corrida con seed mediana).

Con K=15 y K=20 la grilla es un mar de celdas negras (muertas) con puntitos esparcidos donde cae 1 país. La matriz U se vuelve **inútil para visualizar clusters** porque la mayoría de los pesos están en zona muerta y las "fronteras" se confunden con celdas vacías.

> En SOMs sobre datasets grandes (miles de muestras) un K=15 o K=20 sí puede ser útil porque hay muchas muestras para "llenar" la grilla. Acá con N=28 simplemente no hay material suficiente — la grilla es más grande que la información disponible.

## Conclusión

Confirmamos el límite práctico que el profe dejó implícito: **K no puede ser arbitrariamente grande**. Para N=28 países:

- K ≤ 4: gana resolución sin patología extrema.
- K = 5 a 8: zona gris, ya hay más celdas que países pero todavía se puede leer.
- K ≥ 15: la grilla deja de ser un mapa interpretable — es una matriz dispersa con ~20 puntos activos y el resto vacío.

Y el QE casi no se mueve, lo que sugiere que **los ~20 países "centrales" del dataset definen un agrupamiento natural de ~15-20 clusters, y agregar más neuronas no descubre nada nuevo** — solo agrega ruido decorativo.

Para el TP nos quedamos con la decisión del primer barrido: **K=3** (lectura interpretable + baja patología). K=5 a 8 podrían usarse si quisiéramos un mapa más fino, pero el costo en muertas no vale lo poco que se gana en QE.

## Cómo regenerar

```bash
cd "kohonen/experimentos/barrido K grande"
python3 barrido_K_grande.py
```

Tarda ~25 segundos (K=20 con 5 semillas es lo más pesado).

## Archivos en este directorio

| Archivo | Contenido |
|---|---|
| `barrido_K_grande.py` | script del barrido |
| `corridas.csv` | una fila por (K, seed): QE, neuronas muertas |
| `resumen_por_K.csv` | agregado por K |
| `distancias_por_pais.csv` | distancia BMU por país, promediada sobre semillas |
| `distancias_por_pais_full.csv` | distancia BMU por país × semilla (crudo) |
| `seeds_elegidas.json` | qué semilla representativa por K |
| `qe_y_dead_vs_k.png` | barras: QE y % muertas vs K |
| `heatmap_registros_K{5,8,15,20}.png` | conteo de países por neurona |
| `matriz_u_K{5,8,15,20}.png` | matriz U |
| `paises_K{5,8,15,20}.txt` | qué países cayeron en cada celda |
| `K{K}_seed{s}/` | artefactos completos de la corrida representativa |
