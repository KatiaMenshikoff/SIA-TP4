# Barrido η₀ × grilla — K=3

¿Podemos romper el colapso a "solo 2 clusters" diagnosticado en `evolucion K3/`? La hipótesis que veníamos manejando era que el problema no es K=3 en sí, sino el **η inicial demasiado alto (0.5)** que dispara un colapso temprano hacia el centroide, sumado al efecto borde de la grilla rectangular.

Acá testeamos las dos palancas con un mini-barrido 2×2.

## Setup

Mismo recipe que los barridos anteriores, dejando todo fijo salvo lo que se barre:

- **K = 3** (manteniendo nuestra elección estándar),
- R adaptativo `R(0) = K = 3 → R = 1` (lineal),
- η adaptativo `η(i) = η₀ / i`,
- `500·N = 14 000` iteraciones,
- inicialización por muestras,
- 10 semillas por config.

**Lo que varía:**

| | rectangular | hexagonal |
|---|---|---|
| η₀ = 0.1 | ✓ | ✓ |
| η₀ = 0.3 | ✓ | ✓ |

Y como referencia, el baseline del primer barrido (η₀ = 0.5, rectangular) que es lo que veníamos usando.

## Resumen

| η₀ | grilla | QE (media) | QE (std) | muertas (media) | % muertas | clusters efectivos |
|---:|---|---:|---:|---:|---:|---:|
| **0.1** | **rectangular** | **1.816** | 0.024 | 0.6 / 9 | **6.7%** | **~8.4** |
| **0.1** | **hexagonal** | **1.822** | 0.024 | 0.6 / 9 | **6.7%** | **~8.4** |
| 0.3 | rectangular | 2.208 | 0.034 | 2.6 / 9 | 28.9% | ~6.4 |
| 0.3 | hexagonal | 2.236 | 0.031 | 2.8 / 9 | 31.1% | ~6.2 |
| *0.5 (baseline)* | *rectangular* | *2.103* | *0.013* | *3.2 / 9* | *35.6%* | *~5.8* |

Plot: `comparacion.png`.

## Hallazgos

### 1. η₀ = 0.1 rompe el colapso — el efecto es enorme

Comparado con el baseline (η₀ = 0.5):

- **QE baja 14%**: 2.10 → 1.82.
- **Neuronas muertas caen 80%**: 36% → 7%.
- **Clusters efectivos suben 45%**: 5.8 → 8.4 (de 9 celdas, ~8 ganan al menos un país).

Esto valida la hipótesis del bifurcation analysis en `evolucion K3/`: con η₀ más bajo, la fase de "drift colectivo hacia el centroide" se atenúa lo suficiente como para que cuando R cruce √8 ≈ 2.828, las celdas del medio todavía tengan suficiente energía individual para no colapsar al centro.

### 2. η₀ = 0.3 está en el medio y no vale la pena

QE *peor* que el baseline (2.21 vs 2.10), aunque tiene menos muertas (29% vs 36%). Es la peor combinación de las tres: pierde la simplicidad de "dejar el default del profe" pero no logra el beneficio de bajar realmente η₀. **Si vamos a tocar el LR, hay que bajarlo en serio (0.1) o no tocarlo.**

### 3. Hexagonal ≈ rectangular para K=3

La diferencia entre hex y rect es despreciable (QE 1.816 vs 1.822, igual % de muertas). Para K=3 la grilla es tan chica que el "efecto borde" — el motivo por el que probamos hexagonal — no tiene mucho lugar de manifestarse: en 3×3 todas las celdas son borde o esquina. Hexagonal probablemente brilla más a K mayor (K ≥ 5).

> Decisión: **rectangular sigue siendo la elección razonable para K=3**. Si más adelante subimos a K=5, vale la pena re-testar hex.

### 4. Los clusters dejan de ser solo "PC1" — aparece estructura secundaria

Esto es lo más importante visualmente. Con η₀=0.5 las dos esquinas vivas concentraban casi todos los países en un gradiente sobre PC1 (`evolucion K3/Resultados.md`, sección "Qué queda al final"). Ahora con η₀=0.1, el mapa cuenta otra historia.

**Asignaciones para η₀=0.1, rectangular** (seed mediana — ver `paises_eta0.1_rect.txt`):

```
(0,0) [2]: Ireland, Spain
(0,1) [4]: Denmark, Luxembourg, Netherlands, Switzerland       ← núcleo rico
(0,2) [5]: Hungary, Latvia, Lithuania, Slovakia, Ukraine       ← este "promedio"
(1,0) [3]: Finland, Italy, United Kingdom
(1,1) [3]: Germany, Norway, Sweden                              ← norte industrial
(1,2) [0]: --- muerta ---
(2,0) [6]: Bulgaria, Croatia, Estonia, Greece, Poland, Portugal ← sur/este pobre
(2,1) [3]: Austria, Belgium, Iceland
(2,2) [2]: Czech Republic, Slovenia                             ← post-comunistas en transicion
```

Y para η₀=0.1, hexagonal (ver `paises_eta0.1_hexa.txt`):

```
(0,0) [2]: Norway, Sweden                                  ← nórdicos
(0,1) [3]: Croatia, Czech Republic, Slovenia               ← transición
(0,2) [3]: Austria, Belgium, Iceland
(1,0) [0]: --- muerta ---
(1,1) [2]: Italy, Spain                                    ← sur grande
(1,2) [8]: Bulgaria, Estonia, Hungary, Latvia, Lithuania,  ← este completo
           Poland, Slovakia, Ukraine
(2,0) [5]: Denmark, Ireland, Luxembourg, Netherlands,      ← rich core
           Switzerland
(2,1) [2]: Finland, Germany
(2,2) [3]: Greece, Portugal, United Kingdom
```

Ahora **sí** aparecen agrupamientos interpretables más allá del eje oeste-este:

- **Núcleo rico** (Dinamarca, Luxemburgo, Países Bajos, Suiza) en celda propia.
- **Países nórdicos industriales** (Alemania, Noruega, Suecia) separados del núcleo rico.
- **Post-comunistas en transición** (República Checa, Eslovenia, a veces Croacia) en celda propia.
- **Sur/este pobre** (Bulgaria, Croacia, Estonia, Grecia, Polonia, Portugal) en otra.
- **Híbridos** (Irlanda+España, o Italia+España según semilla) ocupan celdas intermedias.

Esto es exactamente lo que esperábamos: cuando el SOM no colapsa, captura PC1 (oeste-este) **y** dimensiones secundarias (norte industrial vs sur transición, núcleo rico vs intermedios). Pasamos de "un cuantizador 1D sobre PC1" a un mapa genuinamente 2D.

### 5. Reproducibilidad

La std de QE para η₀=0.1 es 0.024 — muy baja. Las 10 semillas dan resultados consistentes. Lo que cambia entre semillas es **qué celda concreta de la grilla** termina representando cada cluster (rotaciones/reflexiones), no la estructura de los clusters en sí.

## Conclusión

**La nueva config recomendada es K=3, rectangular, η₀=0.1, R₀=K, adaptativos ambos.**

- Sigue siendo el recipe del profe (z-score, init por muestras, R y η adaptativos, 500·N iteraciones), solo cambia un número: η₀ pasa de 0.5 a 0.1.
- QE 14% mejor, neuronas muertas 80% menos, clusters efectivos 45% más.
- Los clusters resultantes son interpretables más allá del eje oeste-este.

Si quisiéramos pushear más, las próximas palancas serían:
- **Subir K a 5** con η₀=0.1 (más resolución, ver si emergen más clusters genuinos sin reintroducir el colapso).
- **Bajar R₀** a K/2 (sería un cambio más invasivo respecto del recipe del profe).
- **Schedule no-lineal de R** (exponencial en vez de lineal): atenuar las transiciones discretas estudiadas en `evolucion K3/`.

Pero ya con este cambio simple el SOM pasa de "casi inservible para clustering 2D" a "lectura razonable del dataset".

## Cómo regenerar

```bash
cd "kohonen/experimentos/eta y grilla K3"
python3 barrido_eta_grilla.py
```

Tarda ~20 segundos.

## Archivos en este directorio

| Archivo | Contenido |
|---|---|
| `barrido_eta_grilla.py` | script del barrido 2×2 |
| `corridas.csv` | una fila por (η, grilla, seed): QE, neuronas muertas |
| `resumen.csv` | agregado por (η, grilla) — media y std |
| `distancias_por_pais.csv` | distancia BMU por país, promediada sobre semillas |
| `distancias_por_pais_full.csv` | distancia BMU por país × semilla (crudo) |
| `seeds_elegidas.json` | qué semilla es la "mediana" por config |
| `comparacion.png` | barras: QE, % muertas, clusters activos por config |
| `heatmap_eta{0.1,0.3}_{rect,hexa}.png` | conteo de países por neurona |
| `matriz_u_eta{0.1,0.3}_{rect,hexa}.png` | matriz U |
| `paises_eta{0.1,0.3}_{rect,hexa}.txt` | qué países cayeron en cada celda |
| `eta{η}_{grid}_seed{s}/` | artefactos completos de la corrida representativa |
