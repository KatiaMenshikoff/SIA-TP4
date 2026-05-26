# Hopfield — Barrido fino de ruido (mega experimento)

Diseño consensuado el 2026-05-26. Resuelve el pedido de barrer 9 niveles de
ruido sobre los 5 grupos elegidos, con estadística suficiente para curvas, y
clasificación custom (TP/FP/FN/COMPLEMENT/CICLO).

## Objetivo

Medir, para cada uno de los 5 grupos de 4 letras ya elegidos, cómo se degrada
la recuperación de Hopfield a medida que aumenta el ruido en el input. La
salida es una colección de CSVs lista para plotear (los plots vienen en un
script aparte, después).

## Setup

- **Grupos**: `["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]` (los 5 ya elegidos
  en `Seleccion patrones letras.md` y usados por `run_experiments.py`).
- **Niveles de ruido**: `[0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]`.
- **Samples por configuración**: `N_SAMPLES = 30`.
- **Seed**: `seed = BASE_SEED + sample_idx` con `BASE_SEED = 1`. El bitmask de
  ruido del sample `k` es el mismo entre grupos/letras/ruidos para poder
  comparar grupos sobre el "mismo ruido random". Evito 42 a propósito (nota
  guardada en memoria del usuario).
- **Representante visual**: `sample_idx = 0` por configuración. Es el único
  trial cuyas trayectorias y patrón input/output se guardan completos.

**Total de trials**: 5 grupos × 4 letras × 9 ruidos × 30 samples = **5400**.

## Clasificación de outcome

Una sola función `classify_trial(net, target_idx, final, reason, group_patterns)`:

```python
def classify_trial(net, target_idx, final, reason, group_patterns):
    if reason in ("cycle", "max_iter"):
        return "CICLO"
    idx = net.match_stored(final)
    if idx is not None:
        return "TP" if idx == target_idx else "FP"
    for stored in group_patterns:
        if np.array_equal(final, -stored):
            return "COMPLEMENT"
    return "FN"
```

- **TP**: la red converge al patrón almacenado del que se derivó el input
  ruidoso (recuperación correcta).
- **FP**: converge a otro patrón almacenado del grupo (recupera, pero la
  letra equivocada).
- **COMPLEMENT**: converge a `-ξ_k` para *cualquier* `k` del grupo (incluye
  complemento del target).
- **FN**: estable, no es ningún almacenado ni complemento (espurio mixto).
- **CICLO**: no convergió a punto fijo (incluye `reason == "cycle"` y
  `reason == "max_iter"`, semánticamente equivalentes para el outcome).

`TN` no aplica en este experimento porque todos los inputs son patrones
almacenados con ruido (no hay letras externas). Si en el futuro queremos
medir rechazo, va en un experimento aparte.

Orden de chequeo importa: primero almacenado, después complemento. En la
práctica una letra no es complemento de otra, pero el orden lo deja
inambiguo.

## Layout de archivos

Todo bajo `hopfield/output/mega_exp/`:

```
hopfield/output/mega_exp/
├── trials.csv                  # ground truth: 1 fila por trial (5400)
├── stats_by_config.csv         # conteos por (group, letter, noise) — 180 filas
├── stats_by_group_noise.csv    # conteos por (group, noise) — 45 filas
├── representatives.csv         # qué sample es representante visual — 180 filas
├── trajectories.csv            # trayectorias completas de los 180 reps
└── io_patterns.csv             # input/output pixel a pixel de los 180 reps
```

`trials.csv` es la fuente de verdad; los `stats_*` son derivados (groupby).
Los guardo pre-calculados para que el plotting no tenga que re-agregar.

### Esquemas

**`trials.csv`** (5400 filas)

| columna | tipo | nota |
|---|---|---|
| `group` | str | "GRTV", etc. |
| `letter` | str | letra target ∈ group |
| `noise` | float | nivel de ruido aplicado |
| `sample_idx` | int | 0..N_SAMPLES-1 |
| `seed` | int | `BASE_SEED + sample_idx` |
| `target_idx` | int | índice de la letra en group_keys |
| `motivo` | str | "stable" / "cycle" / "max_iter" (razón de corte del solver) |
| `iters` | int | nº de transiciones (len(history)-1) |
| `outcome` | str | TP / FP / FN / COMPLEMENT / CICLO |
| `convergio_a` | str | letra del grupo si TP/FP; "-<letra>" si COMPLEMENT; vacío si FN/CICLO |
| `hamming_input_target` | int | distancia Hamming input vs target |
| `hamming_output_target` | int | distancia Hamming output vs target |
| `hamming_input_output` | int | distancia Hamming input vs output |
| `energia_inicial` | float | H(query) |
| `energia_final` | float | H(final) |

**`stats_by_config.csv`** (180 filas)

```
group, letter, noise, n_samples,
n_TP, n_FP, n_FN, n_COMPLEMENT, n_CICLO,
tasa_TP, tasa_FP, tasa_FN, tasa_COMPLEMENT, tasa_CICLO
```

`tasa_X = n_X / n_samples`. Las 5 tasas suman 1.

**`stats_by_group_noise.csv`** (45 filas)

Mismo esquema que `stats_by_config` pero agregado sobre las 4 letras
(`n_samples = 4 × N_SAMPLES = 120` por fila).

**`representatives.csv`** (180 filas)

```
group, letter, noise, sample_idx
```

Solo `sample_idx = 0` por configuración. Sirve para joinear contra
`trajectories.csv` y `io_patterns.csv`.

**`trajectories.csv`** (~720 filas, depende de cuántas iters)

```
group, letter, noise, sample_idx, iter, energia, s_0, s_1, ..., s_24
```

Una fila por estado visitado por el representante (incluye `iter=0` que es
el query inicial). Los `s_j` son ±1.

**`io_patterns.csv`** (180 × 25 = 4500 filas)

```
group, letter, noise, sample_idx, pixel, input, output
```

Pixel a pixel del representante. Mismo formato que el `io_patterns.csv` que
ya escribe `run_experiments.py`, listo para que el script de plot arme
overlays igual que en `plot_experiments.py`.

## Flujo del script

Archivo nuevo: `hopfield/noise_sweep_experiment.py`. Importa de:

- `hopfield.py` → `Hopfield`, `add_noise`, `load_letters`
- `run_experiments.py` → `trajectory_rows`, `io_rows`, `hamming`

```python
GROUPS = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
NOISE_LEVELS = [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
N_SAMPLES = 30
BASE_SEED = 1
REPRESENTATIVE_SAMPLE_IDX = 0

def main():
    letters = load_letters(...)
    out_dir = Path("hopfield/output/mega_exp")
    out_dir.mkdir(parents=True, exist_ok=True)

    trials_rows, traj_rows, iox_rows, repr_rows = [], [], [], []

    for group in GROUPS:
        group_keys = list(group)
        patterns = np.array([letters[k].flatten() for k in group_keys])
        net = Hopfield(patterns)

        for target_idx, letter in enumerate(group_keys):
            target = patterns[target_idx]
            for noise in NOISE_LEVELS:
                for sample_idx in range(N_SAMPLES):
                    seed = BASE_SEED + sample_idx
                    rng = np.random.default_rng(seed)
                    query = add_noise(target, noise, rng)
                    final, history, reason = net.predict(query)
                    energies = [net.energy(s) for s in history]
                    outcome = classify_trial(net, target_idx, final, reason, patterns)
                    convergio_a = resolve_convergio_a(net, final, outcome, group_keys, patterns)

                    trials_rows.append({
                        "group": group, "letter": letter, "noise": noise,
                        "sample_idx": sample_idx, "seed": seed,
                        "target_idx": target_idx, "motivo": reason,
                        "iters": len(history) - 1,
                        "outcome": outcome, "convergio_a": convergio_a,
                        "hamming_input_target": hamming(query, target),
                        "hamming_output_target": hamming(final, target),
                        "hamming_input_output": hamming(query, final),
                        "energia_inicial": energies[0],
                        "energia_final": energies[-1],
                    })

                    if sample_idx == REPRESENTATIVE_SAMPLE_IDX:
                        repr_rows.append({
                            "group": group, "letter": letter,
                            "noise": noise, "sample_idx": sample_idx,
                        })
                        traj_rows.extend(_traj_rows_for_rep(
                            history, energies, group, letter, noise, sample_idx))
                        iox_rows.extend(_io_rows_for_rep(
                            query, final, group, letter, noise, sample_idx))

    df_trials = pd.DataFrame(trials_rows)
    df_trials.to_csv(out_dir / "trials.csv", index=False)

    _write_stats(df_trials, out_dir)
    pd.DataFrame(repr_rows).to_csv(out_dir / "representatives.csv", index=False)
    pd.DataFrame(traj_rows).to_csv(out_dir / "trajectories.csv", index=False)
    pd.DataFrame(iox_rows).to_csv(out_dir / "io_patterns.csv", index=False)
```

`resolve_convergio_a` produce el string para el CSV:

```python
def resolve_convergio_a(net, final, outcome, group_keys, patterns):
    if outcome in ("TP", "FP"):
        idx = net.match_stored(final)
        return group_keys[idx]
    if outcome == "COMPLEMENT":
        for i, stored in enumerate(patterns):
            if np.array_equal(final, -stored):
                return f"-{group_keys[i]}"
    return ""
```

`_write_stats` hace dos `groupby` sobre `df_trials` para generar
`stats_by_config.csv` y `stats_by_group_noise.csv`. Forma idiomática con
pandas:

```python
def _write_stats(df, out_dir):
    outcomes = ["TP", "FP", "FN", "COMPLEMENT", "CICLO"]
    for keys, name in [
        (["group", "letter", "noise"], "stats_by_config.csv"),
        (["group", "noise"], "stats_by_group_noise.csv"),
    ]:
        g = df.groupby(keys)["outcome"]
        counts = g.value_counts().unstack(fill_value=0)
        for o in outcomes:
            if o not in counts.columns:
                counts[o] = 0
        counts = counts[outcomes].rename(columns={o: f"n_{o}" for o in outcomes})
        counts["n_samples"] = counts.sum(axis=1)
        for o in outcomes:
            counts[f"tasa_{o}"] = counts[f"n_{o}"] / counts["n_samples"]
        counts.reset_index().to_csv(out_dir / name, index=False)
```

## Dependencias y reuso

- **Sin cambios** a `hopfield.py`, `run_experiments.py`, `plot_experiments.py`,
  `capacity_experiments.py`. El script nuevo solo importa.
- **No genera plots**. Plotting va en un script futuro
  (`plot_mega_exp.py`) que consumirá los CSVs.

## Estimación de costo

5400 trials × ~3 iteraciones promedio × multiplicación `W @ s` (25×25)
≈ trivial en CPU. Cuestión de segundos. La memoria es lo más relevante:
`trials.csv` ~5400 × 15 columnas, `io_patterns.csv` ~4500 filas. Nada raro.

## Lo que NO está en scope

- Plots. Van en script aparte (futuro).
- Experimento con letras no-almacenadas barrido por ruido (para medir TN).
- Variación del tamaño del grupo (eso ya lo hace `capacity_experiments.py`).
- Cambio de la regla `sign(0) = previous` o de la actualización síncrona.

## Referencias

- `hopfield/hopfield.py` — clase `Hopfield`, `add_noise`, `load_letters`.
- `hopfield/run_experiments.py` — patrón base de organización de CSVs y
  helpers `trajectory_rows`, `io_rows`, `hamming`.
- `hopfield/Implementación.md` — decisiones de diseño del modelo.
- `hopfield/Seleccion patrones letras.md` — justificación de los 5 grupos.
