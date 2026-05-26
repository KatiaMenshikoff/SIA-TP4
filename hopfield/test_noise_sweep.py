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


def test_classify_max_iter_buckets_with_cycle(small_net):
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
