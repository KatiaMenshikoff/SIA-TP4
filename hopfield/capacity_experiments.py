"""Experimento de capacidad: varía p (cantidad de patrones almacenados).

Para cada p ∈ {2, 3, 5, 6}, elegimos el "mejor" grupo de p letras (el de menor
`|<,>| medio` entre todas las combinaciones) y entrenamos una red. Después:

  - exp1: ¿cada almacenado es punto fijo? (con p > capacidad teórica puede
    fallar — esa es la observación didáctica clave)
  - exp2: ruido 10% y 20% sobre cada almacenado, una muestra determinística.

Salidas en `output/capacity/p<P>/`:
  - `summary.csv`               (un row por almacenado, exp1+exp2)
  - `group.txt`                 (el grupo elegido)
  - `trajectories.csv`, `io_patterns.csv`  (igual que `run_experiments.py`)

La capacidad teórica de Hopfield es ~0.15·N = ~3.75 patrones para N=25.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from hopfield import Hopfield, add_noise, load_letters
from run_experiments import (
    classify_outcome, hamming, io_rows, trajectory_rows, run_case,
)


PS = [2, 3, 5, 6]
NOISE_LEVELS = [0.10, 0.20]
SEED = 1


def best_group(letters: dict[str, np.ndarray], p: int) -> tuple[str, ...]:
    """Devuelve el grupo de p letras con menor `|<,>| medio`."""
    flat = {k: v.flatten() for k, v in letters.items()}
    best_score = float("inf")
    best: tuple[str, ...] | None = None
    for combo in itertools.combinations(flat.keys(), r=p):
        group = np.array([flat[k] for k in combo])
        orto = group.dot(group.T)
        np.fill_diagonal(orto, 0)
        n_off = orto.size - orto.shape[0]
        score = np.abs(orto).sum() / n_off if n_off > 0 else 0.0
        if score < best_score:
            best_score = score
            best = combo
    assert best is not None
    return best


def run_for_p(p: int, letters: dict[str, np.ndarray], output_root: Path) -> dict:
    group = best_group(letters, p)
    group_keys = list(group)
    group_patterns = np.array([letters[k].flatten() for k in group_keys])
    net = Hopfield(group_patterns)

    # Producto interno medio del grupo (para reportar)
    orto = group_patterns.dot(group_patterns.T)
    np.fill_diagonal(orto, 0)
    n_off = orto.size - orto.shape[0]
    avg_ip = np.abs(orto).sum() / n_off if n_off > 0 else 0.0

    out_dir = output_root / f"p{p}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plots").mkdir(exist_ok=True)
    (out_dir / "group.txt").write_text(
        f"p={p}\ngrupo={''.join(group)}\n|<,>| medio={avg_ip:.3f}\n"
    )

    rows = []
    traj_rows: list[dict] = []
    iox_rows: list[dict] = []

    # exp1: stored as input
    n_fijos = 0
    for i, k in enumerate(group_keys):
        target = group_patterns[i]
        res = run_case(net, target, group_keys, target_idx=i)
        es_fijo = bool(np.array_equal(res["final"], target))
        if es_fijo:
            n_fijos += 1
        rows.append({
            "fase": "exp1", "letra": k, "ruido": 0.0,
            "iters": len(res["history"]) - 1, "motivo": res["reason"],
            "convergio_a": res["matched"], "outcome": res["outcome"],
            "es_fijo": es_fijo,
            "hamming_inicial": 0,
            "hamming_final": hamming(res["final"], target),
            "energia_inicial": res["energies"][0],
            "energia_final": res["energies"][-1],
        })
        iox_rows.extend(io_rows(target, res["final"], "exp1", k))
        traj_rows.extend(trajectory_rows(res["history"], res["energies"], "exp1", k))

    # exp2: noise
    rng = np.random.default_rng(SEED)
    n_tp = {n: 0 for n in NOISE_LEVELS}
    for i, k in enumerate(group_keys):
        target = group_patterns[i]
        for noise in NOISE_LEVELS:
            query = add_noise(target, noise, rng)
            res = run_case(net, query, group_keys, target_idx=i)
            if res["outcome"] == "TP":
                n_tp[noise] += 1
            tag = f"n{int(noise*100):02d}"
            case = f"exp2_{tag}"
            rows.append({
                "fase": case, "letra": k, "ruido": noise,
                "iters": len(res["history"]) - 1, "motivo": res["reason"],
                "convergio_a": res["matched"], "outcome": res["outcome"],
                "es_fijo": False,
                "hamming_inicial": hamming(query, target),
                "hamming_final": hamming(res["final"], target),
                "energia_inicial": res["energies"][0],
                "energia_final": res["energies"][-1],
            })
            iox_rows.extend(io_rows(query, res["final"], case, k))
            traj_rows.extend(trajectory_rows(res["history"], res["energies"], case, k))

    pd.DataFrame(rows).to_csv(out_dir / "summary.csv", index=False)
    pd.DataFrame(traj_rows).to_csv(out_dir / "trajectories.csv", index=False)
    pd.DataFrame(iox_rows).to_csv(out_dir / "io_patterns.csv", index=False)

    return {
        "p": p,
        "grupo": "".join(group),
        "|<,>|_medio": round(avg_ip, 3),
        "fijos_exp1": f"{n_fijos}/{p}",
        "TP_ruido10": f"{n_tp[0.10]}/{p}",
        "TP_ruido20": f"{n_tp[0.20]}/{p}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument("--output", default="hopfield/output/capacity", type=Path)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    print(f"Letras cargadas: {len(letters)}\n")

    summary = []
    for p in PS:
        print(f"p = {p}:")
        info = run_for_p(p, letters, args.output)
        print(f"  grupo: {info['grupo']}  |<,>|_medio={info['|<,>|_medio']}")
        print(f"  exp1 (almacenados como input): {info['fijos_exp1']} son punto fijo")
        print(f"  exp2 ruido 10%: TP {info['TP_ruido10']}")
        print(f"  exp2 ruido 20%: TP {info['TP_ruido20']}\n")
        summary.append(info)

    pd.DataFrame(summary).to_csv(args.output / "summary_capacity.csv", index=False)
    print(f"Listo. Resumen en {args.output / 'summary_capacity.csv'}")


if __name__ == "__main__":
    main()
