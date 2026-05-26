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
from run_experiments import hamming


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
                    # Seed compartido entre niveles de ruido para el mismo sample_idx:
                    # add_noise usa rng.random(shape) < p_flip, así que el mismo draw
                    # uniforme con distinto threshold genera bitmasks anidados (el de
                    # noise=0.2 es superset del de noise=0.1). Permite comparaciones
                    # pareadas entre niveles para un mismo (grupo, letra, sample).
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

    df_trials = pd.DataFrame(trials_rows)
    df_trials.to_csv(out_dir / "trials.csv", index=False)
    print(f"trials.csv: {len(df_trials)} filas")

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
