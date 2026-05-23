"""
Visualizaciones de los resultados de kohonen.py.

Lee resultados/{weights.csv, assignments.csv, metadata.json} y genera:
- heatmap_registros.png       : cantidad de muestras asignadas por neurona.
- matriz_u.png                : distancia promedio de cada neurona a sus vecinas.
- activacion_por_variable.png : valor promedio de cada variable por neurona.
- paises_por_neurona.txt      : que paises cayeron en cada neurona.

Uso:
    python visualizar.py --resultados resultados
"""
import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def neuron_distance(a, b, grid_type):
    ai, aj = a
    bi, bj = b
    if grid_type == "rectangular":
        return np.hypot(ai - bi, aj - bj)
    if grid_type == "hexagonal":
        ax = aj + 0.5 * (ai % 2)
        bx = bj + 0.5 * (bi % 2)
        ay = ai * np.sqrt(3) / 2
        by = bi * np.sqrt(3) / 2
        return np.hypot(ax - bx, ay - by)
    raise ValueError(f"grilla desconocida: {grid_type}")


def load(path):
    with open(os.path.join(path, "metadata.json")) as f:
        meta = json.load(f)
    weights_df = pd.read_csv(os.path.join(path, "weights.csv"))
    asgn_df = pd.read_csv(os.path.join(path, "assignments.csv"))
    K = meta["K"]
    vars_ = meta["variables"]
    W = np.zeros((K, K, len(vars_)))
    for _, row in weights_df.iterrows():
        W[int(row["i"]), int(row["j"])] = [row[v] for v in vars_]
    return W, asgn_df, meta


def plot_heatmap(asgn_df, K, out):
    counts = np.zeros((K, K), dtype=int)
    for _, row in asgn_df.iterrows():
        counts[int(row["i"]), int(row["j"])] += 1

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(counts, cmap="viridis")
    for i in range(K):
        for j in range(K):
            color = "white" if counts[i, j] < counts.max() / 2 else "black"
            ax.text(j, i, str(counts[i, j]), ha="center", va="center", color=color)
    ax.set_title("Registros por neurona")
    ax.set_xticks(range(K))
    ax.set_yticks(range(K))
    plt.colorbar(im, ax=ax, label="cantidad de muestras")
    plt.tight_layout()
    plt.savefig(os.path.join(out, "heatmap_registros.png"), dpi=120)
    plt.close()


def _vecinos_directos(coord, K, grid_type):
    """Devuelve coords de neuronas vecinas inmediatas (radio chico)."""
    threshold = 1.5 if grid_type == "rectangular" else 1.1
    vecinos = []
    for a in range(K):
        for b in range(K):
            if (a, b) == coord:
                continue
            if neuron_distance(coord, (a, b), grid_type) <= threshold:
                vecinos.append((a, b))
    return vecinos


def plot_u_matrix(W, grid_type, out):
    K = W.shape[0]
    U = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            vecinos = _vecinos_directos((i, j), K, grid_type)
            if not vecinos:
                continue
            U[i, j] = np.mean(
                [np.linalg.norm(W[i, j] - W[a, b]) for a, b in vecinos]
            )

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(U, cmap="bone_r")
    for i in range(K):
        for j in range(K):
            ax.text(j, i, f"{U[i, j]:.2f}", ha="center", va="center",
                    color="black", fontsize=8,
                    bbox=dict(facecolor="white", edgecolor="none",
                              boxstyle="round,pad=0.25", alpha=0.85))
    ax.set_title("Matriz U (distancia promedio a vecinas)")
    ax.set_xticks(range(K))
    ax.set_yticks(range(K))
    plt.colorbar(im, ax=ax, label="distancia euclidea promedio")
    plt.tight_layout()
    plt.savefig(os.path.join(out, "matriz_u.png"), dpi=120)
    plt.close()


def plot_activacion_por_variable(W, vars_, out):
    K = W.shape[0]
    n = len(vars_)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.5))
    axes_flat = np.array(axes).flatten() if rows * cols > 1 else [axes]

    for k, var in enumerate(vars_):
        ax = axes_flat[k]
        im = ax.imshow(W[:, :, k], cmap="coolwarm")
        ax.set_title(var)
        ax.set_xticks(range(K))
        ax.set_yticks(range(K))
        plt.colorbar(im, ax=ax)

    for k in range(n, len(axes_flat)):
        axes_flat[k].axis("off")

    plt.suptitle("Valor promedio de cada variable por neurona", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(out, "activacion_por_variable.png"),
                dpi=120, bbox_inches="tight")
    plt.close()


def export_paises_por_neurona(asgn_df, K, out):
    lines = []
    for i in range(K):
        for j in range(K):
            sub = asgn_df[(asgn_df["i"] == i) & (asgn_df["j"] == j)]
            if not sub.empty:
                paises = ", ".join(sub["country"].astype(str).tolist())
                lines.append(f"({i},{j}) [{len(sub)}]: {paises}")
            else:
                lines.append(f"({i},{j}) [0]: --- neurona muerta ---")
    with open(os.path.join(out, "paises_por_neurona.txt"), "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultados", default="resultados")
    args = ap.parse_args()

    W, asgn_df, meta = load(args.resultados)
    K = meta["K"]
    grid_type = meta["grilla"]
    vars_ = meta["variables"]

    plot_heatmap(asgn_df, K, args.resultados)
    plot_u_matrix(W, grid_type, args.resultados)
    plot_activacion_por_variable(W, vars_, args.resultados)
    export_paises_por_neurona(asgn_df, K, args.resultados)

    print(f"Listo. Salidas en {args.resultados}/")
    for f in ["heatmap_registros.png", "matriz_u.png",
              "activacion_por_variable.png", "paises_por_neurona.txt"]:
        print(f"  {f}")


if __name__ == "__main__":
    main()
