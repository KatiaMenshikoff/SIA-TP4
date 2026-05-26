# Mega-experimento: barrido fino de ruido sobre 5 grupos

Experimento global de Hopfield: para cada uno de los 5 grupos de 4 letras
elegidos en `hopfield/Seleccion patrones letras.md`, se mide la
recuperación bajo ruido a 13 niveles, con 30 muestras independientes por
configuración. Total: **7800 ejecuciones**.

El experimento se construyó en dos pasos:
1. `hopfield/noise_sweep_experiment.py` — corre los 9 niveles base.
2. `hopfield/extend_noise_experiment.py` — extiende con 4 niveles
   adicionales (0.05, 0.15, 0.25, 0.35) y mergea con los CSVs existentes
   (idempotente, no re-corre configs ya hechas).

Spec completa:
[`docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md`](../../../docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md).

## Setup

| parámetro                 | valor                                                                              |
| ------------------------- | ---------------------------------------------------------------------------------- |
| Grupos                    | `GRTV`, `JLRX`, `AJKU`, `BDOX`, `HMNW`                                             |
| Niveles de ruido          | 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65       |
| Samples por configuración | 30                                                                                 |
| Seed                      | `1 + sample_idx` (compartido entre niveles de ruido)                               |
| Trials totales            | 5 × 4 × 13 × 30 = **7800**                                                         |

**Diseño del seed.** El seed depende solo de `sample_idx`, no del nivel de
ruido. Como `add_noise` usa `rng.random(shape) < p_flip`, el mismo draw
uniforme con distinto threshold produce bitmasks **anidados** (el bitmask
a noise=0.2 es superset del de noise=0.1). Eso permite comparaciones
pareadas: dentro de un mismo `(grupo, letra, sample)` el ruido escala
agregando flips, sin cambiar la base random. Los niveles agregados por
`extend_noise_experiment.py` siguen el mismo esquema, así que se insertan
naturalmente en la jerarquía.

## Taxonomía de outcomes

Cada trial se etiqueta con uno de 5 buckets:

| outcome        | qué pasó                                                                          |
| -------------- | --------------------------------------------------------------------------------- |
| **TP**         | La red converge al patrón target (recuperación correcta).                         |
| **FP**         | La red converge a otro patrón almacenado del grupo.                               |
| **COMPLEMENT** | La red converge a `-ξ_k` para algún `k` (estado espurio "anti-patrón").           |
| **FN**         | Estable, no es ningún almacenado ni complemento (espurio mixto).                  |
| **CICLO**      | No converge a punto fijo (incluye `reason == "cycle"` y `reason == "max_iter"`).  |

**TN no aplica** acá: todos los inputs son patrones almacenados con ruido,
nunca letras externas. Si queremos medir rechazo (input = letra no
almacenada), va en otro experimento.

Orden de chequeo en `classify_trial`: CICLO → almacenado → complemento →
FN. Eso garantiza que un trial que cicla pero por casualidad cae en un
patrón almacenado se etiquete honestamente como CICLO.

## Resultados resumidos

### Distribución global de outcomes (7800 trials)

| outcome    |    n |     % |
| ---------- | ---: | ----: |
| TP         | 2951 | 37.8% |
| FP         | 1805 | 23.1% |
| COMPLEMENT | 1715 | 22.0% |
| CICLO      |  828 | 10.6% |
| FN         |  501 |  6.4% |

### Tasa de TP por nivel de ruido (promedio sobre grupos y letras)

| ruido | tasa_TP |
| ----: | ------: |
| 0.05  |   0.738 |
| 0.10  |   0.732 |
| 0.15  |   0.705 |
| 0.20  |   0.665 |
| 0.25  |   0.598 |
| 0.30  |   0.485 |
| 0.35  |   0.365 |
| 0.40  |   0.272 |
| 0.45  |   0.165 |
| 0.50  |   0.102 |
| 0.55  |   0.050 |
| 0.60  |   0.032 |
| 0.65  |   0.010 |

Con los niveles agregados el decaimiento queda mucho más suave. Se
distingue una **meseta** entre 0.05 y 0.15 (la red recupera ~73% sin
importar cuánto ruido tenga mientras esté por debajo del 15%), un
**régimen de degradación lineal** entre 0.20 y 0.45 (cada 5% de ruido
adicional bajan ~10 puntos porcentuales de TP), y una **cola plana** a
partir de 0.55 (la red ya casi nunca recupera).

### Tasa de TP por grupo (promedio sobre letras y ruidos)

| grupo | tasa_TP |
| ----- | ------: |
| JLRX  |   0.535 |
| GRTV  |   0.508 |
| AJKU  |   0.452 |
| BDOX  |   0.212 |
| HMNW  |   0.184 |

El ranking sigue el orden esperado por ortogonalidad (ver
`Seleccion patrones letras.md`): los grupos con `|⟨ξ_i, ξ_j⟩|` medio más
bajo (más "ortogonales") recuperan mejor. `HMNW` es el peor grupo
intencionalmente.

### Outcomes por nivel de ruido (sumado entre grupos y letras, 600 trials por fila)

```
outcome  CICLO  COMPLEMENT   FN   FP   TP
noise
0.05         7          30    0  120  443
0.10         6          30    2  123  439
0.15        21          29    5  122  423
0.20        32          29   14  126  399
0.25        58          32   19  132  359
0.30        81          35   45  148  291
0.35        93          61   56  171  219
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

A ruido muy bajo (0.05-0.10) la red rara vez espurea: dominan TP y FP,
y CICLO/FN apenas asoman. CICLO crece monótonamente hasta 0.50 y
después cae porque los inputs muy ruidosos caen directamente en el
atractor antipodal (estable) sin oscilar.

## Archivos en este directorio

| archivo                    | contenido                                                | filas | columnas |
| -------------------------- | -------------------------------------------------------- | ----: | -------: |
| `trials.csv`               | 1 fila por trial (ground truth)                          |  7800 |       15 |
| `stats_by_config.csv`      | Conteos y tasas por `(group, letter, noise)`             |   260 |       14 |
| `stats_by_group_noise.csv` | Conteos y tasas por `(group, noise)`                     |    65 |       13 |
| `representatives.csv`      | Llaves del trial representante (sample_idx=0) por config |   260 |        4 |
| `trajectories.csv`         | Trayectoria completa de los representantes              |   955 |       31 |
| `io_patterns.csv`          | Input vs output pixel a pixel de los representantes      |  6500 |        7 |

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
# (1) Corrida base: 9 niveles, 5400 trials
PYTHONPATH=hopfield python3 hopfield/noise_sweep_experiment.py

# (2) Extensión: agrega 4 niveles más, queda en 7800 trials
PYTHONPATH=hopfield python3 hopfield/extend_noise_experiment.py
```

La extensión es idempotente — si una config ya está en `trials.csv`, no
la re-corre. Si querés agregar más niveles, modificá la lista
`NEW_NOISE_LEVELS` en `extend_noise_experiment.py` y volvé a correrlo.

Tests unitarios:

```bash
python3 -m pytest hopfield/test_noise_sweep.py -v
```

Plots:

```bash
python3 hopfield/plot_mega_exp.py
```

El script de plots **deriva la lista de niveles de ruido del propio
trials.csv**, así que no hace falta tocarlo si extendés el experimento.

## Plots

Ver [`README_resultados_plots.md`](README_resultados_plots.md) para la
guía completa de cada figura. Salidas en [`plots/`](plots/).
