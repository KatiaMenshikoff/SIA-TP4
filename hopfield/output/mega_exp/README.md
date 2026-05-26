# Mega-experimento: barrido fino de ruido sobre 5 grupos

Experimento global de Hopfield: para cada uno de los 5 grupos de 4 letras
elegidos en `hopfield/Seleccion patrones letras.md`, se mide la
recuperación bajo ruido a 9 niveles, con 30 muestras independientes por
configuración. Total: **5400 ejecuciones**.

Spec completa: [`docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md`](../../../docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md).

## Setup

| parámetro | valor |
| --- | --- |
| Grupos | `GRTV`, `JLRX`, `AJKU`, `BDOX`, `HMNW` |
| Niveles de ruido | 0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65 |
| Samples por configuración | 30 |
| Seed | `1 + sample_idx` (compartido entre niveles de ruido) |
| Trials totales | 5 × 4 × 9 × 30 = **5400** |

**Diseño del seed.** El seed depende solo de `sample_idx`, no del nivel de
ruido. Como `add_noise` usa `rng.random(shape) < p_flip`, el mismo draw
uniforme con distinto threshold produce bitmasks **anidados** (el bitmask
a noise=0.2 es superset del de noise=0.1). Eso permite comparaciones
pareadas: dentro de un mismo `(grupo, letra, sample)` el ruido escala
agregando flips, sin cambiar la base random.

## Taxonomía de outcomes

Cada trial se etiqueta con uno de 5 buckets:

| outcome | qué pasó |
| --- | --- |
| **TP** | La red converge al patrón target (recuperación correcta). |
| **FP** | La red converge a otro patrón almacenado del grupo. |
| **COMPLEMENT** | La red converge a `-ξ_k` para algún `k` (estado espurio "anti-patrón"). |
| **FN** | Estable, no es ningún almacenado ni complemento (espurio mixto). |
| **CICLO** | No converge a punto fijo (incluye `reason == "cycle"` y `reason == "max_iter"`). |

**TN no aplica** acá: todos los inputs son patrones almacenados con ruido,
nunca letras externas. Si queremos medir rechazo (input = letra no
almacenada), va en otro experimento.

Orden de chequeo en `classify_trial`: CICLO → almacenado → complemento →
FN. Eso garantiza que un trial que cicla pero por casualidad cae en un
patrón almacenado se etiquete honestamente como CICLO.

## Resultados resumidos

### Distribución global de outcomes (5400 trials)

| outcome | n | % |
| --- | ---: | ---: |
| COMPLEMENT | 1563 | 28.9% |
| TP | 1507 | 27.9% |
| FP | 1260 | 23.3% |
| CICLO | 649 | 12.0% |
| FN | 421 | 7.8% |

### Tasa de TP por nivel de ruido (promedio sobre grupos y letras)

| ruido | tasa_TP |
| ---: | ---: |
| 0.10 | 0.732 |
| 0.20 | 0.665 |
| 0.30 | 0.485 |
| 0.40 | 0.272 |
| 0.45 | 0.165 |
| 0.50 | 0.102 |
| 0.55 | 0.050 |
| 0.60 | 0.032 |
| 0.65 | 0.010 |

Decaimiento monótono. A noise=0.10 la red recupera tres de cada cuatro
veces; a noise=0.50 (el "punto de no-información") solo un 10%; a
noise=0.65 casi nunca.

### Tasa de TP por grupo (promedio sobre letras y ruidos)

| grupo | tasa_TP |
| --- | ---: |
| JLRX | 0.393 |
| GRTV | 0.368 |
| AJKU | 0.318 |
| BDOX | 0.162 |
| HMNW | 0.156 |

El ranking sigue el orden esperado por ortogonalidad (ver
`Seleccion patrones letras.md`): los grupos con `|⟨ξ_i, ξ_j⟩|` medio más
bajo (más "ortogonales") recuperan mejor. `HMNW` es el peor grupo
intencionalmente.

### Outcomes por nivel de ruido (sumado entre grupos y letras)

```
outcome  CICLO  COMPLEMENT   FN   FP   TP
noise
0.10         6          30    2  123  439
0.20        32          29   14  126  399
0.30        81          35   45  148  291
0.40        89         107   58  183  163
0.45        94         174   52  181   99
0.50       107         216   55  161   61
0.55        98         260   64  148   30
0.60        85         317   69  110   19
0.65        57         395   62   80    6
```

Patrón claro: a medida que sube el ruido, TP cae, COMPLEMENT crece. El
input se "voltea" más allá del 50% (más de la mitad de los pixeles
flippeados) y la red termina en el atractor antipodal del target — un
fenómeno bien conocido de Hopfield.

## Archivos en este directorio

| archivo | contenido | filas | columnas |
| --- | --- | ---: | ---: |
| `trials.csv` | 1 fila por trial (ground truth) | 5400 | 15 |
| `stats_by_config.csv` | Conteos y tasas por `(group, letter, noise)` | 180 | 14 |
| `stats_by_group_noise.csv` | Conteos y tasas por `(group, noise)` | 45 | 13 |
| `representatives.csv` | Llaves del trial representante (sample_idx=0) por config | 180 | 4 |
| `trajectories.csv` | Trayectoria completa de los representantes (estado por iteración) | ~680 | 31 |
| `io_patterns.csv` | Input vs output pixel a pixel de los representantes | 4500 | 7 |

### Esquema `trials.csv`

```
group, letter, noise, sample_idx, seed, target_idx,
motivo (stable/cycle/max_iter), iters,
outcome (TP/FP/FN/COMPLEMENT/CICLO),
convergio_a (letra del grupo si TP/FP; "-<letra>" si COMPLEMENT; "" si FN/CICLO),
hamming_input_target, hamming_output_target, hamming_input_output,
energia_inicial, energia_final
```

### Esquema `stats_by_config.csv` y `stats_by_group_noise.csv`

```
{keys}, n_samples,
n_TP, n_FP, n_FN, n_COMPLEMENT, n_CICLO,
tasa_TP, tasa_FP, tasa_FN, tasa_COMPLEMENT, tasa_CICLO
```

Las 5 tasas suman 1.

### Esquema `trajectories.csv`

```
group, letter, noise, sample_idx, iter, energia, s_0, s_1, ..., s_24
```

Una fila por estado visitado (incluye `iter=0` que es el query inicial).
Los `s_j` son ±1.

### Esquema `io_patterns.csv`

```
group, letter, noise, sample_idx, pixel, input, output
```

25 filas por representante (una por pixel). Mismo formato que el
`io_patterns.csv` que escribe `run_experiments.py`, así que se puede
reusar el código de overlay de `plot_experiments.py` con cambios mínimos.

## Cómo regenerar

Desde la raíz del repo:

```bash
PYTHONPATH=hopfield python3 hopfield/noise_sweep_experiment.py
```

Tarda pocos segundos. Salidas en `hopfield/output/mega_exp/`.

Tests unitarios de la lógica de clasificación y agregación:

```bash
python3 -m pytest hopfield/test_noise_sweep.py -v
```

## Próximo paso: plots

El script no genera plots, solo CSVs. El plotting va en un script aparte
(pendiente) que va a producir:

- Curvas `tasa_TP` vs `ruido`, una por grupo, en un mismo gráfico (para
  comparar grupos buenos vs malos).
- Heatmap o barras apiladas con la distribución de outcomes por
  `(grupo, ruido)`.
- Para los 180 representantes: triplete input/output/overlay (igual que en
  `output/<group>/plots/`), energía vs iteración, y tira de estados.

Los CSVs ya tienen toda la información necesaria.
