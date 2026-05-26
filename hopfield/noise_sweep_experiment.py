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
