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
