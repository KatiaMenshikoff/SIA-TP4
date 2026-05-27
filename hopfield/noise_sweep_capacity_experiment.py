"""Mega-experimento sobre los grupos de capacidad (p = 2, 3, 5, 6).

Replica el barrido de `noise_sweep_experiment.py` (13 niveles de ruido,
30 samples por config, clasificación TP/FP/FN/COMPLEMENT/CICLO) pero con
los grupos elegidos en `hopfield/output/capacity/README.md`:

  - p=2: `AL`
  - p=3: `FUY`
  - p=5: `GMPVZ`
  - p=6: `JLRTVX`

Salida en `hopfield/output/mega_exp_capacity/`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hopfield import Hopfield, load_letters
from noise_sweep_experiment import (
    N_SAMPLES, BASE_SEED, REPRESENTATIVE_SAMPLE_IDX,
    _run_one_trial, classify_trial, resolve_convergio_a, _write_stats,
)
from run_experiments import hamming


# Grupos de capacidad (mismas tuplas que `capacity_experiments.py`)
CAPACITY_GROUPS = ["AL", "FUY", "GMPVZ", "JLRTVX"]

# Mismos 13 niveles que en el mega-experimento extendido
ALL_NOISE_LEVELS = [
    0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35,
    0.40, 0.45, 0.50, 0.55, 0.60, 0.65,
]


def main():
    parser = argparse.ArgumentParser(
        description="Barrido fino de ruido sobre los grupos de capacidad (p=2,3,5,6).")
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument(
        "--output", default="hopfield/output/mega_exp_capacity", type=Path)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    out_dir: Path = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    trials_rows: list[dict] = []
    traj_rows: list[dict] = []
    iox_rows: list[dict] = []
    repr_rows: list[dict] = []

    for group in CAPACITY_GROUPS:
        print(f"Grupo {group} (p={len(group)})...")
        group_keys = list(group)
        group_patterns = np.array([letters[k].flatten() for k in group_keys])
        net = Hopfield(group_patterns)

        for target_idx, letter in enumerate(group_keys):
            target = group_patterns[target_idx]
            for noise in ALL_NOISE_LEVELS:
                for sample_idx in range(N_SAMPLES):
                    # Seed compartido entre niveles de ruido para el mismo sample_idx
                    # (mismo diseño anidado que noise_sweep_experiment).
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
                        "p": len(group),
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
                        for j in range(res["query"].shape[0]):
                            iox_rows.append({
                                "group": group, "letter": letter,
                                "noise": noise, "sample_idx": sample_idx,
                                "pixel": j,
                                "input": int(res["query"][j]),
                                "output": int(res["final"][j]),
                            })

    df_trials = pd.DataFrame(trials_rows)
    df_trials.to_csv(out_dir / "trials.csv", index=False)
    print(f"trials.csv: {len(df_trials)} filas")

    # Stats: por (group, letter, noise) y por (group, noise).
    # `_write_stats` no incluye `p` en el groupby, pero p ↔ group es 1-a-1
    # acá, así que se reconstruye trivialmente al leer.
    _write_stats(df_trials, out_dir)
    print("stats_by_config.csv y stats_by_group_noise.csv escritos")

    pd.DataFrame(repr_rows).to_csv(out_dir / "representatives.csv", index=False)
    print(f"representatives.csv: {len(repr_rows)} filas")

    pd.DataFrame(traj_rows).to_csv(out_dir / "trajectories.csv", index=False)
    print(f"trajectories.csv: {len(traj_rows)} filas")

    pd.DataFrame(iox_rows).to_csv(out_dir / "io_patterns.csv", index=False)
    print(f"io_patterns.csv: {len(iox_rows)} filas")


if __name__ == "__main__":
    main()
