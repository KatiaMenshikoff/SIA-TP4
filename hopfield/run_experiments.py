"""Corre los 3 experimentos por grupo y guarda CSVs.

Experimentos por grupo (5 grupos: GRTV, JLRX, AJKU, BDOX, HMNW):
  - exp1: alimentar la red con sus propios patrones almacenados (deben ser
    puntos fijos en 1 iteración).
  - exp2: alimentar versiones ruidosas (10%, 20%, 65%) — una muestra
    determinística por nivel.
  - exp3: alimentar 5 letras NO almacenadas — 2 parecidas + 3 distintas,
    elegidas por grupo según `max |inner|` con los almacenados.

Salidas en `output/<grupo>/`:
  - `exp1_almacenados.csv`  (métricas por letra)
  - `exp2_ruido.csv`        (métricas por letra × nivel de ruido)
  - `exp3_no_almacenadas.csv` (métricas por letra externa)
  - `trajectories.csv`      (cada iteración: energía + estado flatten)
  - `io_patterns.csv`       (input/output pixel a pixel para overlays)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hopfield import Hopfield, add_noise, load_letters


GROUPS = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
NOISE_LEVELS = [0.10, 0.20, 0.65]
SEED = 1


def classify_outcome(
    net: Hopfield, target_idx: int | None, final: np.ndarray,
    reason: str, group_keys: list[str],
) -> tuple[str, str | None]:
    """Devuelve (outcome, letra_a_la_que_convergió).

    - `TP`:    convergió al patrón objetivo (solo aplica si target_idx no es None).
    - `FP`:    convergió a otro patrón almacenado del grupo.
    - `MatchAlmacenado`: idem FP, pero cuando no había objetivo (exp3).
    - `Espurio`: estado estable no almacenado (incluye complementos).
    - `Ciclo`:  no convergió a un punto fijo (típicamente 2-ciclo).
    """
    if reason == "cycle":
        return "Ciclo", None
    idx = net.match_stored(final)
    if idx is None:
        return "Espurio", None
    matched = group_keys[idx]
    if target_idx is None:
        return "MatchAlmacenado", matched
    return ("TP" if idx == target_idx else "FP"), matched


def hamming(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.sum(a != b))


def pick_external_letters(
    letters: dict[str, np.ndarray], group_keys: list[str],
    n_similar: int = 2, n_distinct: int = 3,
) -> list[tuple[str, str, int, str]]:
    """Elige n_similar letras parecidas y n_distinct letras distintas a los
    almacenados, fuera del grupo. Métrica: `max_k |<letra, almacenado_k>|`.

    Devuelve lista de (letra, tipo, max_ip, letra_más_parecida_del_grupo).
    """
    group_flats = {k: letters[k].flatten() for k in group_keys}
    scores = []
    for k, v in letters.items():
        if k in group_keys:
            continue
        flat = v.flatten()
        ips = {gk: abs(int(flat.dot(gv))) for gk, gv in group_flats.items()}
        max_gk = max(ips, key=ips.get)
        scores.append((k, ips[max_gk], max_gk))
    scores_sorted = sorted(scores, key=lambda x: -x[1])
    similar = scores_sorted[:n_similar]
    distinct = scores_sorted[-n_distinct:]
    return (
        [(k, "similar", ip, closest) for k, ip, closest in similar]
        + [(k, "distinta", ip, closest) for k, ip, closest in distinct]
    )


def trajectory_rows(
    history: list[np.ndarray], energies: list[float],
    case: str, letter_label: str,
) -> list[dict]:
    rows = []
    for i, (s, e) in enumerate(zip(history, energies)):
        row = {"caso": case, "letra": letter_label, "iter": i, "energia": e}
        for j, v in enumerate(s):
            row[f"s_{j}"] = int(v)
        rows.append(row)
    return rows


def io_rows(query: np.ndarray, final: np.ndarray, case: str, letter_label: str) -> list[dict]:
    rows = []
    for j in range(query.shape[0]):
        rows.append({
            "caso": case, "letra": letter_label, "pixel": j,
            "input": int(query[j]), "output": int(final[j]),
        })
    return rows


def run_case(
    net: Hopfield, query: np.ndarray, group_keys: list[str],
    target_idx: int | None,
) -> dict:
    final, history, reason = net.predict(query)
    energies = [net.energy(s) for s in history]
    outcome, matched = classify_outcome(net, target_idx, final, reason, group_keys)
    return dict(
        query=query, final=final, history=history, energies=energies,
        reason=reason, outcome=outcome, matched=matched,
    )


def run_for_group(group: str, letters: dict[str, np.ndarray], output_root: Path) -> None:
    group_keys = list(group)
    group_patterns = np.array([letters[k].flatten() for k in group_keys])
    net = Hopfield(group_patterns)

    out_dir = output_root / group
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plots").mkdir(exist_ok=True)

    traj_rows: list[dict] = []
    iox_rows: list[dict] = []

    # -------- Experimento 1: almacenados --------
    exp1_rows = []
    for i, k in enumerate(group_keys):
        target = group_patterns[i]
        res = run_case(net, target, group_keys, target_idx=i)
        exp1_rows.append({
            "letra": k, "iters": len(res["history"]) - 1, "motivo": res["reason"],
            "convergio_a": res["matched"], "outcome": res["outcome"],
            "es_fijo": np.array_equal(res["final"], target),
            "energia_inicial": res["energies"][0], "energia_final": res["energies"][-1],
        })
        iox_rows.extend(io_rows(res["query"], res["final"], "exp1", k))
        if i == 0:
            traj_rows.extend(trajectory_rows(res["history"], res["energies"], "exp1", k))
    pd.DataFrame(exp1_rows).to_csv(out_dir / "exp1_almacenados.csv", index=False)

    # -------- Experimento 2: ruido --------
    rng = np.random.default_rng(SEED)
    exp2_rows = []
    for i, k in enumerate(group_keys):
        target = group_patterns[i]
        for noise in NOISE_LEVELS:
            query = add_noise(target, noise, rng)
            res = run_case(net, query, group_keys, target_idx=i)
            n_tag = f"n{int(noise * 100):02d}"
            case = f"exp2_{n_tag}"
            exp2_rows.append({
                "letra_objetivo": k, "ruido": noise, "seed": SEED,
                "iters": len(res["history"]) - 1, "motivo": res["reason"],
                "convergio_a": res["matched"], "outcome": res["outcome"],
                "hamming_inicial": hamming(query, target),
                "hamming_final": hamming(res["final"], target),
                "energia_inicial": res["energies"][0], "energia_final": res["energies"][-1],
            })
            iox_rows.extend(io_rows(query, res["final"], case, k))
            traj_rows.extend(trajectory_rows(res["history"], res["energies"], case, k))
    pd.DataFrame(exp2_rows).to_csv(out_dir / "exp2_ruido.csv", index=False)

    # -------- Experimento 3: no-almacenadas --------
    external = pick_external_letters(letters, group_keys)
    exp3_rows = []
    for k, tipo, max_ip, closest in external:
        query = letters[k].flatten()
        res = run_case(net, query, group_keys, target_idx=None)
        exp3_rows.append({
            "letra_query": k, "tipo": tipo,
            "max_inner_product": max_ip, "mas_parecida_a": closest,
            "iters": len(res["history"]) - 1, "motivo": res["reason"],
            "convergio_a": res["matched"], "outcome": res["outcome"],
            "energia_inicial": res["energies"][0], "energia_final": res["energies"][-1],
        })
        iox_rows.extend(io_rows(query, res["final"], "exp3", k))
        traj_rows.extend(trajectory_rows(res["history"], res["energies"], "exp3", k))
    pd.DataFrame(exp3_rows).to_csv(out_dir / "exp3_no_almacenadas.csv", index=False)

    pd.DataFrame(traj_rows).to_csv(out_dir / "trajectories.csv", index=False)
    pd.DataFrame(iox_rows).to_csv(out_dir / "io_patterns.csv", index=False)

    print(f"  → {out_dir}: 5 CSVs escritos ({len(exp1_rows)+len(exp2_rows)+len(exp3_rows)} casos)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument("--output", default="hopfield/output", type=Path)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    print(f"Letras cargadas: {len(letters)}")
    for group in GROUPS:
        print(f"Grupo {group}:")
        run_for_group(group, letters, args.output)
    print("Listo.")


if __name__ == "__main__":
    main()
