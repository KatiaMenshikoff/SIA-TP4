"""Red de Hopfield para memoria asociativa.

Modelo clásico (Hebb + actualización síncrona) para asociar un patrón de
consulta al patrón almacenado más cercano. Ver `Implementación.md` para
las decisiones de diseño y las referencias a las clases.
"""
from __future__ import annotations

import argparse
import string
from pathlib import Path

import numpy as np


def sign_keep(h: np.ndarray, previous: np.ndarray) -> np.ndarray:
    """Función signo con la convención `sign(0) = estado previo`.

    h > 0  → +1
    h < 0  → -1
    h == 0 → previous[i]  (no flippea cuando h_i = 0, según Euge)
    """
    return np.where(h > 0, 1.0, np.where(h < 0, -1.0, previous))


class Hopfield:
    """Red de Hopfield con actualización síncrona.

    Pesos: `W = (1/N) · K · K^T` con `K` de shape `(N, p)` (patrones en
    columnas). En numpy lo armamos con patrones por fila por comodidad:
        W = (K_filas.T @ K_filas) / N
    `W` queda simétrica por construcción; se pone la diagonal en 0 para
    eliminar conexiones de una neurona consigo misma.
    """

    def __init__(self, patterns: np.ndarray):
        """`patterns` puede ser `(p, N)` o `(p, h, w)` (se aplana si es 3D)."""
        patterns = np.asarray(patterns, dtype=np.float64)
        if patterns.ndim == 3:
            p, h, w = patterns.shape
            patterns = patterns.reshape(p, h * w)
        if patterns.ndim != 2:
            raise ValueError(f"Esperaba patterns 2D o 3D, vino shape {patterns.shape}")
        self.patterns = patterns  # (p, N)
        self.p, self.N = patterns.shape
        self.W = (patterns.T @ patterns) / self.N  # (N, N) simétrica
        np.fill_diagonal(self.W, 0.0)

    def energy(self, state: np.ndarray) -> float:
        """`H(S) = -1/2 · S^T · W · S`."""
        s = np.asarray(state, dtype=np.float64).flatten()
        return float(-0.5 * s @ self.W @ s)

    def predict(
        self, query: np.ndarray, max_iter: int = 50,
    ) -> tuple[np.ndarray, list[np.ndarray], str]:
        """Itera `S_{t+1} = sign(W · S_t)` hasta estabilizar.

        Devuelve `(estado_final, historia, motivo)` con `motivo` en
        {`"stable"`, `"cycle"`, `"max_iter"`}. La historia incluye el
        estado inicial y todos los intermedios hasta el final.
        - `stable`: `S_{t+1} == S_t` (punto fijo, normalmente un patrón
          almacenado o un estado espurio).
        - `cycle`: `S_{t+1} == S_{t-1}` (2-ciclo, lo más típico bajo
          actualización síncrona).
        - `max_iter`: no estabilizó en `max_iter` pasos.
        """
        s = np.asarray(query, dtype=np.float64).flatten()
        if s.shape[0] != self.N:
            raise ValueError(f"Query de tamaño {s.shape[0]}, esperaba {self.N}")
        history = [s.copy()]
        prev_prev: np.ndarray | None = None
        for _ in range(max_iter):
            h = self.W @ s
            new_s = sign_keep(h, s)
            history.append(new_s.copy())
            if np.array_equal(new_s, s):
                return new_s, history, "stable"
            if prev_prev is not None and np.array_equal(new_s, prev_prev):
                return new_s, history, "cycle"
            prev_prev = s
            s = new_s
        return s, history, "max_iter"

    def match_stored(self, state: np.ndarray) -> int | None:
        """Si `state` coincide exacto con un patrón almacenado devuelve su
        índice; si no, `None`. El complemento (`-pattern`) no cuenta:
        es un estado espurio clásico, lo dejamos para el llamador."""
        s = np.asarray(state, dtype=np.float64).flatten()
        for i, pattern in enumerate(self.patterns):
            if np.array_equal(s, pattern):
                return i
        return None


# ---------------------------------------------------------------------------
# Helpers para el CLI / demo
# ---------------------------------------------------------------------------

def load_letters(path: Path) -> dict[str, np.ndarray]:
    """Carga `letters.txt`: 5 líneas por letra, `*` = 1, separador `=`."""
    letters: dict[str, np.ndarray] = {}
    current = np.ones((5, 5)) * -1
    idx = 0
    with open(path) as fp:
        for line in fp:
            if not line.strip():
                continue
            if line[0] == '=':
                letters[string.ascii_uppercase[len(letters)]] = current
                current = np.ones((5, 5)) * -1
                idx = 0
            else:
                for i, c in enumerate(line.rstrip('\n')[:5]):
                    current[idx][i] = 1 if c == '*' else -1
                idx += 1
    return letters


def add_noise(pattern: np.ndarray, p_flip: float, rng: np.random.Generator) -> np.ndarray:
    """Da vuelta cada pixel con probabilidad `p_flip` (Bernoulli independiente)."""
    flips = rng.random(pattern.shape) < p_flip
    return np.where(flips, -pattern, pattern)


def ascii_letter(flat_pattern: np.ndarray) -> str:
    """Dibuja un patrón 25-D como ASCII art 5×5."""
    grid = np.asarray(flat_pattern).reshape(5, 5)
    return '\n'.join(''.join('*' if v > 0 else '.' for v in row) for row in grid)


def main():
    parser = argparse.ArgumentParser(description="Demo de Hopfield con el abecedario 5×5.")
    parser.add_argument("--letters", default="hopfield/letters.txt", type=Path)
    parser.add_argument("--group", default="GRTV",
                        help="Letras a almacenar (ej: GRTV — mejor grupo según ortogonalidad)")
    parser.add_argument("--query", default="G",
                        help="Letra a consultar con ruido (debe estar en --group para esperar TP)")
    parser.add_argument("--noise", type=float, default=0.15,
                        help="Probabilidad de flip por pixel en la consulta")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--max_iter", type=int, default=50)
    args = parser.parse_args()

    letters = load_letters(args.letters)
    group_keys = list(args.group)
    patterns = np.array([letters[k].flatten() for k in group_keys])
    net = Hopfield(patterns)

    rng = np.random.default_rng(args.seed)
    target = letters[args.query].flatten()
    query = add_noise(target, args.noise, rng)

    print(f"Grupo almacenado: {group_keys}")
    print(f"Consulta: {args.query} con ruido {args.noise:.0%} (seed={args.seed})\n")
    print("Patrón objetivo:")
    print(ascii_letter(target))
    print("\nConsulta ruidosa:")
    print(ascii_letter(query))
    print(f"\nEnergía inicial: {net.energy(query):.3f}")

    final, history, reason = net.predict(query, max_iter=args.max_iter)
    energies = [net.energy(s) for s in history]
    iters = len(history) - 1
    print(f"\nMotivo de corte: {reason} (en {iters} iteraciones)")
    print(f"Energía final:   {energies[-1]:.3f}")
    print(f"Trayectoria E:   {[f'{e:.2f}' for e in energies]}")

    print("\nEstado final:")
    print(ascii_letter(final))

    idx = net.match_stored(final)
    if idx is not None:
        matched = group_keys[idx]
        outcome = "TP" if matched == args.query else "FP"
        print(f"\n→ {outcome}: convergió al patrón almacenado '{matched}'")
    elif reason == "cycle":
        print("\n→ CICLO: no convergió a un punto fijo")
    else:
        # Chequear si es complemento de algún almacenado (espurio típico)
        for k, p in zip(group_keys, net.patterns):
            if np.array_equal(final, -p):
                print(f"\n→ ESPURIO: complemento del patrón '{k}'")
                break
        else:
            print("\n→ ESPURIO: estado estable que no es ningún patrón almacenado ni complemento")


if __name__ == "__main__":
    main()
