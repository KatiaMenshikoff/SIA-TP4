# Hopfield Noise Sweep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correr un barrido fino de ruido (9 niveles × 30 samples) sobre los 5 grupos de Hopfield ya elegidos, clasificar cada trial con la taxonomía custom (TP/FP/FN/COMPLEMENT/CICLO) y guardar todo en CSVs listos para plotear.

**Architecture:** Un script nuevo `hopfield/noise_sweep_experiment.py` que importa `Hopfield`, `add_noise`, `load_letters` de `hopfield.py` y los helpers `hamming`, `trajectory_rows`, `io_rows` de `run_experiments.py`. La lógica nueva (clasificación, agregación de stats) vive en el script nuevo. Tests unitarios para las funciones puras en `hopfield/test_noise_sweep.py`.

**Tech Stack:** Python 3, numpy, pandas, pytest (para los tests). Sin dependencias nuevas.

**Spec:** `docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md`

**Convenciones del repo (de CLAUDE.md):**
- Comunicación en español.
- **Nunca** agregar `Co-Authored-By: Claude` en los commits.
- Commits: pedir confirmación al usuario antes de cada uno (regla global del usuario). En este plan los pasos de commit están sugeridos pero el ejecutor debe consultar antes de correrlos.

---

## File Structure

**Crear:**
- `hopfield/noise_sweep_experiment.py` — script principal del experimento.
- `hopfield/test_noise_sweep.py` — tests unitarios para `classify_trial` y `resolve_convergio_a`.

**Modificar:** ninguno. El script nuevo solo importa.

**Outputs en runtime** (ignorados por git si corresponde, pero `hopfield/output/` ya tiene contenido versionado):
- `hopfield/output/mega_exp/trials.csv`
- `hopfield/output/mega_exp/stats_by_config.csv`
- `hopfield/output/mega_exp/stats_by_group_noise.csv`
- `hopfield/output/mega_exp/representatives.csv`
- `hopfield/output/mega_exp/trajectories.csv`
- `hopfield/output/mega_exp/io_patterns.csv`

---

## Task 1: `classify_trial` con tests

**Files:**
- Create: `hopfield/test_noise_sweep.py`
- Create: `hopfield/noise_sweep_experiment.py`

- [ ] **Step 1: Crear esqueleto de `noise_sweep_experiment.py`**

Crear el archivo con imports y constantes, sin la lógica todavía:

```python
"""Barrido fino de ruido sobre los 5 grupos de Hopfield.

Para cada (grupo, letra almacenada, nivel de ruido) corre N_SAMPLES
ejecuciones y guarda CSVs en hopfield/output/mega_exp/ listos para plotear.

Ver `docs/superpowers/specs/2026-05-26-hopfield-noise-sweep-design.md`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hopfield import Hopfield, add_noise, load_letters
from run_experiments import hamming, io_rows, trajectory_rows


GROUPS = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
NOISE_LEVELS = [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
N_SAMPLES = 30
BASE_SEED = 1
REPRESENTATIVE_SAMPLE_IDX = 0
OUTCOMES = ["TP", "FP", "FN", "COMPLEMENT", "CICLO"]
```

- [ ] **Step 2: Escribir tests para `classify_trial`**

Crear `hopfield/test_noise_sweep.py`:

```python
"""Tests unitarios para la lógica de clasificación del mega-experimento."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Asegurar que se puede importar desde hopfield/ cuando se corre desde la raíz
sys.path.insert(0, str(Path(__file__).parent))

from hopfield import Hopfield
from noise_sweep_experiment import classify_trial, resolve_convergio_a


@pytest.fixture
def small_net():
    """Red con 2 patrones ortogonales fáciles de razonar."""
    patterns = np.array([
        [1, 1, 1, -1, -1, -1, 1, 1, 1],     # patrón 0
        [1, -1, 1, -1, 1, -1, 1, -1, 1],    # patrón 1 (ortogonal al 0)
    ], dtype=np.float64)
    net = Hopfield(patterns)
    return net, patterns


def test_classify_tp(small_net):
    net, patterns = small_net
    final = patterns[0].copy()
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="stable", group_patterns=patterns)
    assert outcome == "TP"


def test_classify_fp(small_net):
    net, patterns = small_net
    final = patterns[1].copy()  # converge a otro almacenado
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="stable", group_patterns=patterns)
    assert outcome == "FP"


def test_classify_complement_of_target(small_net):
    net, patterns = small_net
    final = -patterns[0].copy()
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="stable", group_patterns=patterns)
    assert outcome == "COMPLEMENT"


def test_classify_complement_of_other(small_net):
    net, patterns = small_net
    final = -patterns[1].copy()
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="stable", group_patterns=patterns)
    assert outcome == "COMPLEMENT"


def test_classify_fn_spurious(small_net):
    net, patterns = small_net
    # Estado que no es ningún almacenado ni complemento
    final = np.array([1, 1, -1, 1, -1, 1, -1, -1, 1], dtype=np.float64)
    # Verificar precondición (es realmente espurio)
    assert not any(np.array_equal(final, p) for p in patterns)
    assert not any(np.array_equal(final, -p) for p in patterns)
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="stable", group_patterns=patterns)
    assert outcome == "FN"


def test_classify_cycle(small_net):
    net, patterns = small_net
    final = patterns[0].copy()  # Aunque el final matchee, si reason=cycle es CICLO
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="cycle", group_patterns=patterns)
    assert outcome == "CICLO"


def test_classify_max_iter_buckets_with_cycle(small_net):
    net, patterns = small_net
    final = np.array([1, 1, -1, 1, -1, 1, -1, -1, 1], dtype=np.float64)
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="max_iter", group_patterns=patterns)
    assert outcome == "CICLO"
```

- [ ] **Step 3: Correr los tests para verificar que fallan**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -m pytest hopfield/test_noise_sweep.py -v
```

Expected: FAIL con `ImportError: cannot import name 'classify_trial'`.

- [ ] **Step 4: Implementar `classify_trial` y `resolve_convergio_a`**

Agregar a `hopfield/noise_sweep_experiment.py`:

```python
def classify_trial(
    net: Hopfield, target_idx: int, final: np.ndarray,
    reason: str, group_patterns: np.ndarray,
) -> str:
    """Clasifica el resultado de una corrida en uno de los 5 buckets.

    - TP: convergió al patrón target (recuperación correcta).
    - FP: convergió a otro patrón almacenado.
    - COMPLEMENT: convergió a `-ξ_k` para algún k del grupo.
    - FN: estable, no es ningún almacenado ni complemento.
    - CICLO: no convergió a punto fijo (cycle o max_iter).
    """
    if reason in ("cycle", "max_iter"):
        return "CICLO"
    idx = net.match_stored(final)
    if idx is not None:
        return "TP" if idx == target_idx else "FP"
    for stored in group_patterns:
        if np.array_equal(final, -stored):
            return "COMPLEMENT"
    return "FN"


def resolve_convergio_a(
    net: Hopfield, final: np.ndarray, outcome: str,
    group_keys: list[str], group_patterns: np.ndarray,
) -> str:
    """Devuelve el string descriptivo del estado final para el CSV.

    - TP/FP → letra del grupo (ej. "G").
    - COMPLEMENT → "-<letra>" (ej. "-G").
    - FN/CICLO → "".
    """
    if outcome in ("TP", "FP"):
        idx = net.match_stored(final)
        return group_keys[idx]
    if outcome == "COMPLEMENT":
        for i, stored in enumerate(group_patterns):
            if np.array_equal(final, -stored):
                return f"-{group_keys[i]}"
    return ""
```

- [ ] **Step 5: Agregar tests para `resolve_convergio_a`**

Agregar al final de `hopfield/test_noise_sweep.py`:

```python
def test_resolve_convergio_a_tp(small_net):
    net, patterns = small_net
    final = patterns[0].copy()
    s = resolve_convergio_a(net, final, "TP", ["A", "B"], patterns)
    assert s == "A"


def test_resolve_convergio_a_fp(small_net):
    net, patterns = small_net
    final = patterns[1].copy()
    s = resolve_convergio_a(net, final, "FP", ["A", "B"], patterns)
    assert s == "B"


def test_resolve_convergio_a_complement(small_net):
    net, patterns = small_net
    final = -patterns[1].copy()
    s = resolve_convergio_a(net, final, "COMPLEMENT", ["A", "B"], patterns)
    assert s == "-B"


def test_resolve_convergio_a_fn(small_net):
    net, patterns = small_net
    final = np.array([1, 1, -1, 1, -1, 1, -1, -1, 1], dtype=np.float64)
    s = resolve_convergio_a(net, final, "FN", ["A", "B"], patterns)
    assert s == ""


def test_resolve_convergio_a_ciclo(small_net):
    net, patterns = small_net
    final = patterns[0].copy()
    s = resolve_convergio_a(net, final, "CICLO", ["A", "B"], patterns)
    assert s == ""
```

- [ ] **Step 6: Correr tests, esperar PASS**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -m pytest hopfield/test_noise_sweep.py -v
```

Expected: 12 tests pasan.

- [ ] **Step 7: Commit (pedir confirmación al usuario primero)**

Mensaje sugerido:

```
hopfield: clasificacion del mega-experimento (TP/FP/FN/COMPLEMENT/CICLO) + tests
```

NO agregar trailer Co-Authored-By.

---

## Task 2: Loop principal — `trials.csv`

**Files:**
- Modify: `hopfield/noise_sweep_experiment.py`

- [ ] **Step 1: Implementar el loop y la escritura de `trials.csv`**

Agregar al script:

```python
def _run_one_trial(
    net: Hopfield, target: np.ndarray, noise: float, seed: int,
) -> dict:
    """Corre una ejecución y devuelve el dict crudo con todo lo necesario."""
    rng = np.random.default_rng(seed)
    query = add_noise(target, noise, rng)
    final, history, reason = net.predict(query)
    energies = [net.energy(s) for s in history]
    return {
        "query": query, "final": final, "history": history,
        "energies": energies, "reason": reason,
    }


def main():
    parser = argparse.ArgumentParser(description="Barrido fino de ruido sobre 5 grupos.")
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument("--output", default="hopfield/output/mega_exp", type=Path)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    trials_rows: list[dict] = []
    traj_rows: list[dict] = []
    iox_rows: list[dict] = []
    repr_rows: list[dict] = []

    for group in GROUPS:
        print(f"Grupo {group}...")
        group_keys = list(group)
        group_patterns = np.array([letters[k].flatten() for k in group_keys])
        net = Hopfield(group_patterns)

        for target_idx, letter in enumerate(group_keys):
            target = group_patterns[target_idx]
            for noise in NOISE_LEVELS:
                for sample_idx in range(N_SAMPLES):
                    seed = BASE_SEED + sample_idx
                    res = _run_one_trial(net, target, noise, seed)
                    outcome = classify_trial(
                        net, target_idx, res["final"], res["reason"], group_patterns,
                    )
                    convergio_a = resolve_convergio_a(
                        net, res["final"], outcome, group_keys, group_patterns,
                    )
                    trials_rows.append({
                        "group": group,
                        "letter": letter,
                        "noise": noise,
                        "sample_idx": sample_idx,
                        "seed": seed,
                        "target_idx": target_idx,
                        "motivo": res["reason"],
                        "iters": len(res["history"]) - 1,
                        "outcome": outcome,
                        "convergio_a": convergio_a,
                        "hamming_input_target": hamming(res["query"], target),
                        "hamming_output_target": hamming(res["final"], target),
                        "hamming_input_output": hamming(res["query"], res["final"]),
                        "energia_inicial": res["energies"][0],
                        "energia_final": res["energies"][-1],
                    })

                    if sample_idx == REPRESENTATIVE_SAMPLE_IDX:
                        repr_rows.append({
                            "group": group, "letter": letter,
                            "noise": noise, "sample_idx": sample_idx,
                        })
                        # trajectories / io_patterns: en Task 3
                        pass

    df_trials = pd.DataFrame(trials_rows)
    df_trials.to_csv(out_dir / "trials.csv", index=False)
    print(f"trials.csv: {len(df_trials)} filas")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Correr el script end-to-end**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python hopfield/noise_sweep_experiment.py
```

Expected output (aprox.):
```
Grupo GRTV...
Grupo JLRX...
Grupo AJKU...
Grupo BDOX...
Grupo HMNW...
trials.csv: 5400 filas
```

- [ ] **Step 3: Verificar `trials.csv`**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -c "
import pandas as pd
df = pd.read_csv('hopfield/output/mega_exp/trials.csv')
print('shape:', df.shape)
print('cols:', list(df.columns))
print('outcomes:', df['outcome'].value_counts().to_dict())
print('grupos:', df['group'].unique())
print('ruidos:', sorted(df['noise'].unique()))
assert df.shape == (5400, 15), f'shape inesperado: {df.shape}'
assert set(df['group'].unique()) == {'GRTV','JLRX','AJKU','BDOX','HMNW'}
assert sorted(df['noise'].unique()) == [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
print('OK')
"
```

Expected: termina con `OK`. La distribución de outcomes va a tener TP alto en niveles bajos y mucho CICLO/FN cerca de 0.5-0.65.

- [ ] **Step 4: Commit (pedir confirmación primero)**

Mensaje sugerido:

```
hopfield: loop principal del mega-experimento, escribe trials.csv
```

---

## Task 3: Representantes — `trajectories.csv`, `io_patterns.csv`, `representatives.csv`

**Files:**
- Modify: `hopfield/noise_sweep_experiment.py`

- [ ] **Step 1: Escribir helpers que agreguen columnas group/noise/sample_idx**

Los helpers `trajectory_rows` y `io_rows` de `run_experiments.py` toman `case` y `letter_label`. Para este experimento necesitamos más columnas (`group`, `noise`, `sample_idx`). Mejor envolverlos:

Reemplazar el bloque `if sample_idx == REPRESENTATIVE_SAMPLE_IDX` en `main()` con el cuerpo siguiente (en lugar del `pass`):

```python
                    if sample_idx == REPRESENTATIVE_SAMPLE_IDX:
                        repr_rows.append({
                            "group": group, "letter": letter,
                            "noise": noise, "sample_idx": sample_idx,
                        })
                        # Trajectories: una fila por estado visitado
                        for it, (state, energy) in enumerate(
                            zip(res["history"], res["energies"])
                        ):
                            row = {
                                "group": group, "letter": letter,
                                "noise": noise, "sample_idx": sample_idx,
                                "iter": it, "energia": energy,
                            }
                            for j, v in enumerate(state):
                                row[f"s_{j}"] = int(v)
                            traj_rows.append(row)
                        # IO patterns: input/output pixel a pixel
                        for j in range(res["query"].shape[0]):
                            iox_rows.append({
                                "group": group, "letter": letter,
                                "noise": noise, "sample_idx": sample_idx,
                                "pixel": j,
                                "input": int(res["query"][j]),
                                "output": int(res["final"][j]),
                            })
```

- [ ] **Step 2: Escribir los tres CSVs después del loop**

Agregar después de `df_trials.to_csv(...)`:

```python
    pd.DataFrame(repr_rows).to_csv(out_dir / "representatives.csv", index=False)
    print(f"representatives.csv: {len(repr_rows)} filas")

    pd.DataFrame(traj_rows).to_csv(out_dir / "trajectories.csv", index=False)
    print(f"trajectories.csv: {len(traj_rows)} filas")

    pd.DataFrame(iox_rows).to_csv(out_dir / "io_patterns.csv", index=False)
    print(f"io_patterns.csv: {len(iox_rows)} filas")
```

- [ ] **Step 3: Correr el script de nuevo**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python hopfield/noise_sweep_experiment.py
```

Expected:
- `representatives.csv`: 180 filas (5×4×9).
- `io_patterns.csv`: 4500 filas (180×25).
- `trajectories.csv`: varía según iters, típicamente 500-1000 filas.

- [ ] **Step 4: Verificar los CSVs**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -c "
import pandas as pd
reps = pd.read_csv('hopfield/output/mega_exp/representatives.csv')
traj = pd.read_csv('hopfield/output/mega_exp/trajectories.csv')
io = pd.read_csv('hopfield/output/mega_exp/io_patterns.csv')
print('reps:', reps.shape)
print('traj:', traj.shape)
print('io:', io.shape)
assert reps.shape == (180, 4)
assert io.shape == (4500, 7)
# Cada representante debe tener al menos 1 fila en trajectories (iter=0)
assert len(traj) >= 180
# Cada representante tiene exactamente 25 filas en io
assert (io.groupby(['group','letter','noise','sample_idx']).size() == 25).all()
print('OK')
"
```

Expected: termina con `OK`.

- [ ] **Step 5: Commit (pedir confirmación primero)**

Mensaje sugerido:

```
hopfield: trajectories y io_patterns para los representantes del mega-experimento
```

---

## Task 4: Stats agregados — `stats_by_config.csv` y `stats_by_group_noise.csv`

**Files:**
- Modify: `hopfield/noise_sweep_experiment.py`
- Modify: `hopfield/test_noise_sweep.py`

- [ ] **Step 1: Escribir test para `_write_stats`**

Agregar a `hopfield/test_noise_sweep.py`:

```python
def test_write_stats(tmp_path):
    from noise_sweep_experiment import _write_stats, OUTCOMES
    df = pd.DataFrame([
        # group GRTV, letter G, noise 0.1: 3 TP, 1 FP, 0 resto
        {"group": "GRTV", "letter": "G", "noise": 0.1, "outcome": "TP"},
        {"group": "GRTV", "letter": "G", "noise": 0.1, "outcome": "TP"},
        {"group": "GRTV", "letter": "G", "noise": 0.1, "outcome": "TP"},
        {"group": "GRTV", "letter": "G", "noise": 0.1, "outcome": "FP"},
        # group GRTV, letter R, noise 0.1: 2 TP, 2 CICLO
        {"group": "GRTV", "letter": "R", "noise": 0.1, "outcome": "TP"},
        {"group": "GRTV", "letter": "R", "noise": 0.1, "outcome": "TP"},
        {"group": "GRTV", "letter": "R", "noise": 0.1, "outcome": "CICLO"},
        {"group": "GRTV", "letter": "R", "noise": 0.1, "outcome": "CICLO"},
    ])
    _write_stats(df, tmp_path)

    by_config = pd.read_csv(tmp_path / "stats_by_config.csv")
    by_gn = pd.read_csv(tmp_path / "stats_by_group_noise.csv")

    # 2 configs (G y R) en by_config
    assert len(by_config) == 2
    g_row = by_config[by_config["letter"] == "G"].iloc[0]
    assert g_row["n_TP"] == 3 and g_row["n_FP"] == 1
    assert g_row["n_samples"] == 4
    assert g_row["tasa_TP"] == 0.75 and g_row["tasa_FP"] == 0.25
    # n_FN, n_COMPLEMENT, n_CICLO deben existir y ser 0
    assert g_row["n_FN"] == 0 and g_row["n_COMPLEMENT"] == 0
    assert g_row["n_CICLO"] == 0

    # 1 fila en by_gn (GRTV + 0.1) agregando las 2 letras
    assert len(by_gn) == 1
    gn = by_gn.iloc[0]
    assert gn["n_TP"] == 5 and gn["n_FP"] == 1 and gn["n_CICLO"] == 2
    assert gn["n_samples"] == 8
```

- [ ] **Step 2: Correr tests, esperar FAIL**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -m pytest hopfield/test_noise_sweep.py::test_write_stats -v
```

Expected: FAIL con `ImportError: cannot import name '_write_stats'`.

- [ ] **Step 3: Implementar `_write_stats`**

Agregar a `hopfield/noise_sweep_experiment.py`:

```python
def _write_stats(df: pd.DataFrame, out_dir: Path) -> None:
    """Deriva stats_by_config.csv y stats_by_group_noise.csv desde trials.

    Genera conteos y tasas por cada outcome del schema OUTCOMES,
    rellenando con 0 los buckets que no aparezcan en el groupby.
    """
    for keys, name in [
        (["group", "letter", "noise"], "stats_by_config.csv"),
        (["group", "noise"], "stats_by_group_noise.csv"),
    ]:
        counts = (
            df.groupby(keys)["outcome"]
            .value_counts()
            .unstack(fill_value=0)
        )
        for o in OUTCOMES:
            if o not in counts.columns:
                counts[o] = 0
        counts = counts[OUTCOMES].rename(columns={o: f"n_{o}" for o in OUTCOMES})
        counts["n_samples"] = counts[[f"n_{o}" for o in OUTCOMES]].sum(axis=1)
        for o in OUTCOMES:
            counts[f"tasa_{o}"] = counts[f"n_{o}"] / counts["n_samples"]
        counts.reset_index().to_csv(out_dir / name, index=False)
```

- [ ] **Step 4: Conectar `_write_stats` al `main()`**

En `main()`, después de `df_trials.to_csv(...)` y antes de los CSVs de representantes, agregar:

```python
    _write_stats(df_trials, out_dir)
    print("stats_by_config.csv y stats_by_group_noise.csv escritos")
```

- [ ] **Step 5: Correr el test unitario, esperar PASS**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -m pytest hopfield/test_noise_sweep.py -v
```

Expected: todos los tests pasan (13 en total).

- [ ] **Step 6: Correr el script completo**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python hopfield/noise_sweep_experiment.py
```

Expected output incluye:
```
trials.csv: 5400 filas
stats_by_config.csv y stats_by_group_noise.csv escritos
representatives.csv: 180 filas
trajectories.csv: ... filas
io_patterns.csv: 4500 filas
```

- [ ] **Step 7: Verificar stats**

```bash
cd /Users/tomaspinausig/code/SIA-TP4 && python -c "
import pandas as pd
bc = pd.read_csv('hopfield/output/mega_exp/stats_by_config.csv')
bg = pd.read_csv('hopfield/output/mega_exp/stats_by_group_noise.csv')
print('by_config:', bc.shape)
print('by_group_noise:', bg.shape)
assert bc.shape[0] == 180  # 5*4*9
assert bg.shape[0] == 45   # 5*9
# Las tasas deben sumar 1
tasa_cols = [c for c in bc.columns if c.startswith('tasa_')]
sums = bc[tasa_cols].sum(axis=1)
import numpy as np
assert np.allclose(sums, 1.0), f'tasas no suman 1: {sums.unique()}'
print('n_samples por config:', bc['n_samples'].unique())
assert (bc['n_samples'] == 30).all()
assert (bg['n_samples'] == 120).all()
# Sanity: TP debería degradarse con el ruido (en promedio)
agg = bg.groupby('noise')['tasa_TP'].mean()
print('tasa_TP promedio por ruido:')
print(agg.to_string())
assert agg.loc[0.10] > agg.loc[0.65], 'esperaba que el ruido degrade TP'
print('OK')
"
```

Expected: termina con `OK`. La tasa TP a ruido 0.10 debe ser sustancialmente mayor que a 0.65.

- [ ] **Step 8: Commit (pedir confirmación primero)**

Mensaje sugerido:

```
hopfield: stats agregados del mega-experimento (por config y por grupo-ruido)
```

---

## Self-Review (post-write checklist)

Después de implementar todo, mirar el spec con ojos frescos:

**Spec coverage:**
- [x] Constantes (GROUPS, NOISE_LEVELS, N_SAMPLES, BASE_SEED, REPRESENTATIVE_SAMPLE_IDX) → Task 1 Step 1.
- [x] `classify_trial` con los 5 buckets → Task 1 Step 4.
- [x] `resolve_convergio_a` con strings TP/FP/COMPLEMENT/FN-CICLO → Task 1 Step 4.
- [x] `trials.csv` con las 15 columnas → Task 2 Step 1.
- [x] `representatives.csv` (180 filas, 4 cols) → Task 3 Step 1-2.
- [x] `trajectories.csv` (representantes, con s_0..s_24) → Task 3 Step 1-2.
- [x] `io_patterns.csv` (representantes, 25 píxeles c/u) → Task 3 Step 1-2.
- [x] `stats_by_config.csv` y `stats_by_group_noise.csv` con n_X y tasa_X → Task 4.
- [x] Sin plots (queda para otro script) → spec respetado.

**Placeholders:** ninguno. Todo el código está expandido.

**Type consistency:** revisado: `classify_trial` y `resolve_convergio_a` tienen las mismas firmas en spec, implementación y tests. `OUTCOMES` es la única constante de strings y se usa consistente en `_write_stats`.

---

## Execution

**Plan complete and saved to `docs/superpowers/plans/2026-05-26-hopfield-noise-sweep.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Dispatch un subagent por task, review entre tasks, iteración rápida.

**2. Inline Execution** — Ejecuto las tasks en esta misma sesión con checkpoints.

¿Cuál preferís?
