"""Tests unitarios para la lógica de clasificación del mega-experimento."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Asegurar que se puede importar desde hopfield/ cuando se corre desde la raíz
sys.path.insert(0, str(Path(__file__).parent))

from hopfield import Hopfield
from noise_sweep_experiment import classify_trial, resolve_convergio_a, _write_stats, OUTCOMES


@pytest.fixture
def small_net():
    """Red con 2 patrones distintos fáciles de razonar."""
    patterns = np.array([
        [1, 1, 1, -1, -1, -1, 1, 1, 1],     # patrón 0
        [1, -1, 1, -1, 1, -1, 1, -1, 1],    # patrón 1 (distinto al 0)
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


def test_classify_max_iter_is_ciclo(small_net):
    net, patterns = small_net
    final = np.array([1, 1, -1, 1, -1, 1, -1, -1, 1], dtype=np.float64)
    outcome = classify_trial(net, target_idx=0, final=final,
                             reason="max_iter", group_patterns=patterns)
    assert outcome == "CICLO"


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


def test_resolve_convergio_a_complement_first(small_net):
    net, patterns = small_net
    final = -patterns[0].copy()
    s = resolve_convergio_a(net, final, "COMPLEMENT", ["A", "B"], patterns)
    assert s == "-A"


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


def test_write_stats(tmp_path):
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
