# Experimentos del SOM — bitácora

Este documento traza la **evolución** de los experimentos sobre la red de Kohonen aplicada a `europe.csv` (28 países × 7 variables), desde la primera corrida con la config del profe hasta la config recomendada para entregar el TP.

Cada experimento vive en su propio subdirectorio en `experimentos/` con su propio `Resultados.md` detallado. Acá está el hilo conductor.

```
experimentos/
├── barrido K primer intento/        ← K ∈ {2,3,4} con config original
├── evolucion K3/                    ← visor iteración por iteración + diagnóstico
├── barrido K grande/                ← K ∈ {5,8,15,20} con config original
├── eta y grilla K3/                 ← η × tipo de grilla, K=3 fijo
└── config nueva K3 K5/              ← config recomendada, K ∈ {3, 5}
```

---

## 1. Primer barrido — K ∈ {2, 3, 4}

📁 `experimentos/barrido K primer intento/`

**Setup inicial (recipe del profe tal cual):**
- Grilla rectangular, R adaptativo de K → 1, **η₀ = 0.5 adaptativo**, init por muestras, `500·N = 14 000` iteraciones, 10 semillas.

**Resultado:**

| K | QE (media) | % muertas | clusters efectivos |
|---:|---:|---:|---:|
| 2 | 2.32 | 30% | ~3 |
| 3 | 2.10 | 36% | ~6 |
| 4 | 1.99 | 50% | ~8 |

**Hallazgo molesto:** subiendo K, el QE baja muy poco (14% de 2 a 4) y el % de neuronas muertas explota. Las celdas activas se concentran siempre **en las esquinas y bordes**, con un patrón cuadriculado de muertas en el centro.

**Conclusión inicial:** Elegimos K=3 como compromiso (más interpretable que K=2, menos patológico que K=4). Y nos quedó la pregunta: *¿por qué tantas neuronas muertas?*

**Hipótesis refinada que surgió acá:** las muertas **no son víctimas de competencia** (no hay 2-3 neuronas dominantes que se "comen" los países). Son neuronas cuyos pesos terminaron en zona vacía del espacio 7D — un punto que no corresponde a ningún país real. Ningún país las elige como BMU porque siempre hay otra neurona más cercana.

---

## 2. Evolución temporal K=3 — descubrimos la bifurcación

📁 `experimentos/evolucion K3/`

Para validar la hipótesis, grabamos el estado del SOM K=3 **iteración por iteración** (14 001 snapshots) y armamos un visor HTML con slider (`visor.html`) para revisar la trayectoria.

**Observaciones:**

1. De iter ~50 a iter ~1 200, el heatmap queda **congelado** durante 1 100 iteraciones seguidas. Las asignaciones BMU no cambian.
2. Pero las **distancias entre pesos sí se achican**: el centro de la grilla se vuelve cada vez más homogéneo.
3. De iter ~1 200 a iter ~1 550, **todo colapsa de golpe**: en 350 iteraciones se mueren 4 neuronas, quedando solo las 2 esquinas y un par de celdas con 1-2 países.

**Lo intrigante:** en iter 1 200, el learning rate ya es **η ≈ 0.0004** — minúsculo. ¿Cómo puede divergir tan rápido un sistema con LR así de chico?

### Diagnóstico: bifurcación discreta del vecindario

No es divergencia numérica. Es **geometría de la grilla**.

Para K=3 rectangular, la distancia máxima entre dos neuronas es de una esquina a la opuesta: `√(2² + 2²) = √8 ≈ 2.828`.

- Mientras R > √8, la mask `D < R` incluye **toda la grilla**. Cada update mueve las 9 celdas con el mismo `η · (x − W)` hacia la muestra. Atractor de largo plazo: el centroide de los datos. → las 9 celdas driftean juntas hacia el centroide durante 1 200 iteraciones.
- En **iter ≈ 1 202**, R(i) cruza √8. De repente, las esquinas opuestas se desacoplan. Aparece la primera asimetría dinámica.
- Las dos esquinas activas se tiran hacia clusters opuestos (oeste vs este). Las celdas del medio quedan tironeadas en direcciones contrarias y terminan en el centroide → ningún país las elige → **mueren en cascada**.

La cascada pasa con η ≈ 0.0004 porque los pesos venían "cargados" con 1 200 iteraciones de drift acumulado. El desacople libera esa energía latente.

Plot: `R_vs_dead.png` muestra R(i) y dead vs iteración con los umbrales críticos (√8, √5, 2, √2, 1) marcados.

### El SOM colapsa al PC1

Mirando las asignaciones finales, las dos esquinas vivas contienen:

- **(0,2)** [11 países, este+sur]: Hungary (1.04), Portugal (1.15), Poland (1.23), Slovakia (1.28), Lithuania (1.81), Croatia (2.13), Estonia (2.22), Latvia (2.28), Bulgaria (2.48), Greece (3.67), **Ukraine (5.39)**
- **(2,0)** [12 países, oeste]: Denmark (1.05), Belgium (1.12), Italy (1.33), Netherlands (1.57), Austria (1.59), Germany (1.68), Sweden (1.86), Iceland (2.29), Norway (2.39), Ireland (2.39), Switzerland (3.10), **Luxembourg (3.83)**

Dentro de cada esquina, las distancias a la BMU forman un gradiente sobre PC1 (los más "promedio" cerca, los outliers — Ucrania, Luxemburgo — lejos). **El SOM con esta config está actuando como un cuantizador 1D sobre PC1, no como un mapa 2D.**

Las celdas del medio que podrían haber capturado PC2 (norte industrial vs sur en crisis, o tamaño/poblacional) se murieron antes de poder hacerlo.

---

## 3. Barrido K grande — confirmación del problema

📁 `experimentos/barrido K grande/`

¿Y si subimos K mucho? Probamos K ∈ {5, 8, 15, 20} con la config original.

| K | total celdas | QE | % muertas | activas |
|---:|---:|---:|---:|---:|
| 5  | 25  | 1.94 | 59% | ~10 |
| 8  | 64  | 1.90 | 79% | ~13 |
| 15 | 225 | 1.83 | 92% | ~17 |
| 20 | 400 | 1.86 | 95% | ~19 |

**QE se aplana** y rebota en K=20. **Las neuronas activas convergen a ~17-19** independientemente del K — el SOM "elige" cuántos clusters armar y el resto sobra.

Confirma que el problema **no es K** — es el recipe.

---

## 4. La intervención: η × grilla — bajar η₀ rompe el colapso

📁 `experimentos/eta y grilla K3/`

Si el colapso ocurre porque las primeras iteraciones cargan los pesos hacia el centroide antes del desacople de R=√8, deberíamos poder atenuarlo bajando η₀.

Mini-barrido 2×2 sobre K=3: η₀ ∈ {0.1, 0.3} × grilla ∈ {rectangular, hexagonal}, 10 semillas por config.

| η₀ | grilla | QE | % muertas | clusters activos |
|---:|---|---:|---:|---:|
| **0.1** | **rectangular** | **1.82** | **7%** | **~8.4 / 9** |
| 0.1 | hexagonal | 1.82 | 7% | ~8.4 |
| 0.3 | rectangular | 2.21 | 29% | ~6.4 |
| 0.3 | hexagonal | 2.24 | 31% | ~6.2 |
| *0.5 (baseline)* | *rectangular* | *2.10* | *36%* | *~5.8* |

**Resultado contundente:** η₀ = 0.1 mejora QE 14% y reduce neuronas muertas 80%.

Hexagonal vs rectangular es indistinguible para K=3 (la grilla es tan chica que no hay diferencia de efecto borde).

η₀ = 0.3 está en el medio sin ser mejor que ninguno: **si vamos a tocar el LR, hay que bajarlo en serio (0.1) o no tocarlo.**

---

## 5. Config recomendada — K=3 y K=5 con η₀=0.1

📁 `experimentos/config nueva K3 K5/`

Aplicamos la config nueva a las dos K candidatas. La configuración exacta usada:

| Hiperparámetro          | Valor                            | Cambio vs recipe del profe |
| ----------------------- | -------------------------------- | -------------------------- |
| K                       | 3 y 5                            | (lo que se barre)          |
| Grilla                  | rectangular                      | igual                      |
| R inicial               | `R(0) = K` (3 o 5 según corrida) | igual                      |
| Schedule de R           | adaptativo, lineal `R(0) → 1`    | igual                      |
| η inicial               | **0.1**                          | ← **bajado de 0.5 a 0.1**  |
| Schedule de η           | adaptativo, `η(i) = η₀ / i`      | igual                      |
| Iteraciones             | `500 · N = 14 000`               | igual                      |
| Inicialización de pesos | muestras del set al azar         | igual                      |
| Semillas                | 10 por K                         | (estadística)              |
| Estandarización         | z-score por columna              | igual                      |

| K | QE | % muertas | clusters activos |
|---:|---:|---:|---:|
| **3** | **1.82** | **7%** | **~8.4 / 9** |
| 5 | 1.58 | 32% | ~17.1 / 25 |

### K=3 — el sweet spot interpretativo

8 grupos balanceados con 2-6 países cada uno (asignaciones de la seed mediana):

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

Cada cluster es interpretable sociopolíticamente. Ya no es "PC1 colapsado en 2 esquinas".

### K=5 — confirma estructura pero sobre-granula

17 celdas activas, pero la mayoría tienen **un solo país** (Luxemburgo, España, Alemania, Bélgica, Dinamarca, Croacia, UK, Eslovenia, República Checa, Irlanda — todos en celda propia). Las agrupaciones genuinas (rich core, este estándar, bálticos+Eslovaquia, post-comunistas, intermedios) **son las mismas que aparecen en K=3**.

K=5 baja QE 13% no por mejor clustering sino por mejor **cuantización**: cada celda ≈ 1 país. No descubre clusters nuevos.

### Mapa interactivo

📄 `experimentos/config nueva K3 K5/visualizacion/mapa_clusters.html`

Visualización single-file de los clusters K=3 proyectados sobre el mapa de Europa. Países coloreados por su BMU, etiquetas semánticas por cluster, toggle compacto/detallado. Confirma que los clusters del SOM se alinean con regiones geopolíticas reales.

---

## Veredicto final para la entrega

**Config recomendada:**

| Hiperparámetro | Valor | Cambio vs recipe del profe |
|---|---|---|
| K | 3 | (decidido en barrido inicial) |
| Grilla | rectangular | igual |
| R | adaptativo, R₀ = K = 3 → 1 | igual |
| η | **adaptativo, η₀ = 0.1** | ← **bajamos de 0.5 a 0.1** |
| Iteraciones | 500·N = 14 000 | igual |
| Inicialización | muestras del set | igual |

Un solo número cambiado, justificado por el análisis de la bifurcación en `evolucion K3/`. Resultado: 8 clusters interpretables, 93% de neuronas vivas, QE 14% mejor que con el recipe original.

## Hilo conductor en una frase

> La config original del profe (η₀=0.5) hace que el SOM colapse al eje principal del dataset (PC1) por una bifurcación discreta cuando R cruza √8. Bajando η₀ a 0.1 se atenúa el colapso temprano y emergen 8 clusters interpretables más allá del eje oeste-este.
