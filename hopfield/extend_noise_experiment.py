"""Extiende el mega-experimento con niveles de ruido adicionales.

Lee los CSVs ya producidos por `noise_sweep_experiment.py` en
`hopfield/output/mega_exp/`, corre los `NEW_NOISE_LEVELS` que falten
(idempotente — no re-corre configs que ya están), y vuelca todos los
CSVs combinados ordenados.

Después de correr este script los CSVs tienen los niveles originales
+ los nuevos, y `_write_stats` se recalcula sobre el set completo.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hopfield import Hopfield, load_letters
from noise_sweep_experiment import (
    GROUPS, N_SAMPLES, BASE_SEED, REPRESENTATIVE_SAMPLE_IDX,
    _run_one_trial, classify_trial, resolve_convergio_a, _write_stats,
)
from run_experiments import hamming


NEW_NOISE_LEVELS = [0.05, 0.15, 0.25, 0.35]


def _config_already_done(
    trials: pd.DataFrame, group: str, letter: str, noise: float,
) -> bool:
    """¿Esta config ya tiene N_SAMPLES filas en trials.csv?"""
    if trials.empty:
        return False
    mask = (
        (trials["group"] == group)
        & (trials["letter"] == letter)
        & (np.isclose(trials["noise"], noise))
    )
    return int(mask.sum()) >= N_SAMPLES


def _run_new_trials(
    letters: dict, existing_trials: pd.DataFrame, new_noise_levels: list[float],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Corre los trials faltantes para `new_noise_levels`.

    Devuelve (trials_rows, traj_rows, iox_rows, repr_rows) — solo los nuevos.
    """
    new_trials: list[dict] = []
    new_traj: list[dict] = []
    new_iox: list[dict] = []
    new_repr: list[dict] = []

    for group in GROUPS:
        group_keys = list(group)
        group_patterns = np.array([letters[k].flatten() for k in group_keys])
        net = Hopfield(group_patterns)

        for target_idx, letter in enumerate(group_keys):
            target = group_patterns[target_idx]
            for noise in new_noise_levels:
                if _config_already_done(existing_trials, group, letter, noise):
                    continue
                for sample_idx in range(N_SAMPLES):
                    seed = BASE_SEED + sample_idx
                    res = _run_one_trial(net, target, noise, seed)
                    outcome = classify_trial(
                        net, target_idx, res["final"], res["reason"], group_patterns,
                    )
                    convergio_a = resolve_convergio_a(
                        net, res["final"], outcome, group_keys, group_patterns,
                    )
                    new_trials.append({
                        "group": group, "letter": letter, "noise": noise,
                        "sample_idx": sample_idx, "seed": seed,
                        "target_idx": target_idx, "motivo": res["reason"],
                        "iters": len(res["history"]) - 1,
                        "outcome": outcome, "convergio_a": convergio_a,
                        "hamming_input_target": hamming(res["query"], target),
                        "hamming_output_target": hamming(res["final"], target),
                        "hamming_input_output": hamming(res["query"], res["final"]),
                        "energia_inicial": res["energies"][0],
                        "energia_final": res["energies"][-1],
                    })

                    if sample_idx == REPRESENTATIVE_SAMPLE_IDX:
                        new_repr.append({
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
                            new_traj.append(row)
                        for j in range(res["query"].shape[0]):
                            new_iox.append({
                                "group": group, "letter": letter,
                                "noise": noise, "sample_idx": sample_idx,
                                "pixel": j,
                                "input": int(res["query"][j]),
                                "output": int(res["final"][j]),
                            })

    return new_trials, new_traj, new_iox, new_repr


def _sort_combined(df: pd.DataFrame, sort_cols: list[str]) -> pd.DataFrame:
    """Ordena por las llaves indicadas para que los CSVs queden tidy."""
    available = [c for c in sort_cols if c in df.columns]
    return df.sort_values(available).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Extiende el mega-experimento con más niveles de ruido.")
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument("--output", default="hopfield/output/mega_exp", type=Path)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    out_dir: Path = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    # Cargar CSVs existentes (o vacíos si no hay nada todavía)
    def _read(name: str) -> pd.DataFrame:
        path = out_dir / name
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    trials_old = _read("trials.csv")
    traj_old = _read("trajectories.csv")
    iox_old = _read("io_patterns.csv")
    repr_old = _read("representatives.csv")

    print(f"Existentes: trials={len(trials_old)}, traj={len(traj_old)}, "
          f"io={len(iox_old)}, repr={len(repr_old)}")
    print(f"Niveles de ruido a agregar: {NEW_NOISE_LEVELS}")

    new_trials, new_traj, new_iox, new_repr = _run_new_trials(
        letters, trials_old, NEW_NOISE_LEVELS,
    )
    print(f"Nuevos: trials={len(new_trials)}, traj={len(new_traj)}, "
          f"io={len(new_iox)}, repr={len(new_repr)}")

    # Combinar y ordenar
    trials_full = _sort_combined(
        pd.concat([trials_old, pd.DataFrame(new_trials)], ignore_index=True),
        ["group", "letter", "noise", "sample_idx"],
    )
    traj_full = _sort_combined(
        pd.concat([traj_old, pd.DataFrame(new_traj)], ignore_index=True),
        ["group", "letter", "noise", "sample_idx", "iter"],
    )
    iox_full = _sort_combined(
        pd.concat([iox_old, pd.DataFrame(new_iox)], ignore_index=True),
        ["group", "letter", "noise", "sample_idx", "pixel"],
    )
    repr_full = _sort_combined(
        pd.concat([repr_old, pd.DataFrame(new_repr)], ignore_index=True),
        ["group", "letter", "noise", "sample_idx"],
    )

    # Guardar todos los CSVs (overwriting)
    trials_full.to_csv(out_dir / "trials.csv", index=False)
    traj_full.to_csv(out_dir / "trajectories.csv", index=False)
    iox_full.to_csv(out_dir / "io_patterns.csv", index=False)
    repr_full.to_csv(out_dir / "representatives.csv", index=False)
    print(f"Final: trials={len(trials_full)}, traj={len(traj_full)}, "
          f"io={len(iox_full)}, repr={len(repr_full)}")

    # Re-derivar stats sobre el set completo
    _write_stats(trials_full, out_dir)
    print("stats_by_config.csv y stats_by_group_noise.csv reescritos")

    # Resumen
    niveles = sorted(trials_full["noise"].unique())
    print(f"Niveles de ruido en el dataset final: {niveles}")


if __name__ == "__main__":
    main()
