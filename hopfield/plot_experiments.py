"""Genera plots y README.md autogenerado por grupo a partir de los CSVs
producidos por `run_experiments.py`.

Salida por grupo (en `output/<grupo>/`):
  - `plots/exp1_<L>.png`          : input | output | overlay  (patrones almacenados)
  - `plots/exp2_<L>_n<XX>.png`    : input | output | overlay  (patrón con ruido)
  - `plots/exp3_<L>.png`          : input | output | overlay  (letra no-almacenada)
  - `plots/energy_<caso>_<L>.png` : energía vs iteración
  - `plots/states_<caso>_<L>.png` : tira con todos los estados S_0..S_final
  - `plots/outcomes_summary.png`  : conteo de outcomes por experimento
  - `README.md`                   : índice de los plots con contexto

Convención del overlay:
  - input=+1, output=+1 → verde claro (match en pixel encendido)
  - input=-1, output=-1 → blanco       (match en pixel apagado)
  - input ≠ output      → rojo         (mismatch — la red flippeó ese pixel)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap


GROUPS = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
NOISE_LEVELS = [0.10, 0.20, 0.65]

COLOR_BG = "#ffffff"
COLOR_ON = "#222222"
COLOR_MATCH_ON = "#a8e6a3"   # verde claro: match en +1
COLOR_MATCH_OFF = "#ffffff"  # blanco:      match en -1
COLOR_MISMATCH = "#e04848"   # rojo:        mismatch


def draw_pattern(ax, flat: np.ndarray, title: str | None = None) -> None:
    """Dibuja un patrón 25-D como grilla 5×5 en blanco/negro."""
    grid = flat.reshape(5, 5)
    cmap = ListedColormap([COLOR_BG, COLOR_ON])
    ax.imshow((grid > 0).astype(int), cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(np.arange(-0.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 5, 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=1)
    ax.set_xticks([]); ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)


def draw_overlay(ax, inp: np.ndarray, out: np.ndarray, title: str | None = None) -> None:
    """Pinta cada celda según matching input/output."""
    grid_in = inp.reshape(5, 5)
    grid_out = out.reshape(5, 5)
    h, w = grid_in.shape
    # Construyo array de colores
    colors = np.empty((h, w, 3))
    for i in range(h):
        for j in range(w):
            a, b = grid_in[i, j], grid_out[i, j]
            if a > 0 and b > 0:
                hexc = COLOR_MATCH_ON
            elif a < 0 and b < 0:
                hexc = COLOR_MATCH_OFF
            else:
                hexc = COLOR_MISMATCH
            colors[i, j] = [int(hexc[k:k+2], 16) / 255 for k in (1, 3, 5)]
    ax.imshow(colors)
    ax.set_xticks(np.arange(-0.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 5, 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=1)
    ax.set_xticks([]); ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)


def plot_io_triplet(inp: np.ndarray, out: np.ndarray, label: str, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.8), dpi=140)
    draw_pattern(axes[0], inp, "input")
    draw_pattern(axes[1], out, "output")
    draw_overlay(axes[2], inp, out, "overlay")
    fig.suptitle(label, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_energy(traj: pd.DataFrame, label: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.5, 2.8), dpi=140)
    ax.plot(traj["iter"], traj["energia"], marker="o")
    ax.set_xlabel("iteración")
    ax.set_ylabel("H(S)")
    ax.set_title(f"Energía vs iter — {label}")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_states_strip(traj: pd.DataFrame, label: str, path: Path) -> None:
    """Tira de estados S_0 → S_1 → ... → S_final."""
    n = len(traj)
    fig, axes = plt.subplots(1, n, figsize=(1.6 * n, 1.9), dpi=140)
    if n == 1:
        axes = [axes]
    for i, (_, row) in enumerate(traj.iterrows()):
        state = np.array([row[f"s_{j}"] for j in range(25)])
        draw_pattern(axes[i], state, f"t={int(row['iter'])}")
    fig.suptitle(label, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_outcomes_summary(group_dir: Path, group: str) -> None:
    """Barras apiladas: outcome por experimento."""
    counts = {}
    for exp_name, csv in [
        ("exp1", "exp1_almacenados.csv"),
        ("exp2_10", "exp2_ruido.csv"),
        ("exp2_20", "exp2_ruido.csv"),
        ("exp2_65", "exp2_ruido.csv"),
        ("exp3", "exp3_no_almacenadas.csv"),
    ]:
        df = pd.read_csv(group_dir / csv)
        if exp_name.startswith("exp2_"):
            n = int(exp_name.split("_")[1]) / 100
            df = df[df["ruido"] == n]
        counts[exp_name] = df["outcome"].value_counts().to_dict()

    all_outcomes = sorted({o for d in counts.values() for o in d})
    palette = {"TP": "#4caf50", "FP": "#ff9800", "Espurio": "#9e9e9e",
               "Ciclo": "#9c27b0", "MatchAlmacenado": "#2196f3"}
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=140)
    bottoms = np.zeros(len(counts))
    x = np.arange(len(counts))
    for outcome in all_outcomes:
        vals = np.array([counts[exp].get(outcome, 0) for exp in counts])
        ax.bar(x, vals, bottom=bottoms, label=outcome,
               color=palette.get(outcome, "#777"))
        bottoms += vals
    ax.set_xticks(x)
    ax.set_xticklabels(list(counts.keys()), rotation=15)
    ax.set_ylabel("# casos")
    ax.set_title(f"Outcomes por experimento — grupo {group}")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(group_dir / "plots" / "outcomes_summary.png", bbox_inches="tight")
    plt.close(fig)


def render_readme(group: str, group_dir: Path) -> None:
    exp1 = pd.read_csv(group_dir / "exp1_almacenados.csv")
    exp2 = pd.read_csv(group_dir / "exp2_ruido.csv")
    exp3 = pd.read_csv(group_dir / "exp3_no_almacenadas.csv")

    lines: list[str] = []
    lines.append(f"# Grupo {group}\n")
    lines.append(f"Letras almacenadas: **{', '.join(list(group))}**\n")
    lines.append("Convención del overlay: verde claro = match `+1↔+1`, "
                 "blanco = match `-1↔-1`, rojo = mismatch.\n")
    lines.append("![Outcomes](plots/outcomes_summary.png)\n")

    # Exp1
    lines.append("## Experimento 1 — Patrones almacenados como input\n")
    lines.append("Esperamos que cada patrón almacenado sea un punto fijo "
                 "(convergencia en 1 iteración a sí mismo).\n")
    lines.append(exp1.to_markdown(index=False) + "\n")
    for _, row in exp1.iterrows():
        k = row["letra"]
        lines.append(f"### {k} (almacenada)\n")
        lines.append(f"![exp1 {k}](plots/exp1_{k}.png)\n")

    # Exp2
    lines.append("## Experimento 2 — Patrones almacenados con ruido\n")
    lines.append(f"Niveles: {', '.join(f'{int(n*100)}%' for n in NOISE_LEVELS)}. "
                 "Una muestra determinística por nivel (seed=1).\n")
    lines.append(exp2.to_markdown(index=False) + "\n")
    for _, row in exp2.iterrows():
        k, n = row["letra_objetivo"], int(row["ruido"] * 100)
        tag = f"n{n:02d}"
        lines.append(f"### {k} con ruido {n}% → {row['outcome']}"
                     + (f" ({row['convergio_a']})" if pd.notna(row["convergio_a"]) else "") + "\n")
        lines.append(f"![exp2 {k} {tag}](plots/exp2_{k}_{tag}.png)\n")
        lines.append(f"![energía exp2 {k} {tag}](plots/energy_exp2_{tag}_{k}.png) "
                     f"![estados exp2 {k} {tag}](plots/states_exp2_{tag}_{k}.png)\n")

    # Exp3
    lines.append("## Experimento 3 — Letras no almacenadas\n")
    lines.append("Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados "
                 "(similares), 3 con menor (distintas).\n")
    lines.append(exp3.to_markdown(index=False) + "\n")
    for _, row in exp3.iterrows():
        k = row["letra_query"]
        lines.append(f"### {k} ({row['tipo']}, max_ip={row['max_inner_product']} con {row['mas_parecida_a']}) "
                     f"→ {row['outcome']}"
                     + (f" ({row['convergio_a']})" if pd.notna(row["convergio_a"]) else "") + "\n")
        lines.append(f"![exp3 {k}](plots/exp3_{k}.png)\n")
        lines.append(f"![energía exp3 {k}](plots/energy_exp3_{k}.png) "
                     f"![estados exp3 {k}](plots/states_exp3_{k}.png)\n")

    (group_dir / "README.md").write_text("\n".join(lines))


def plot_for_group(group: str, output_root: Path) -> None:
    group_dir = output_root / group
    plots_dir = group_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    io = pd.read_csv(group_dir / "io_patterns.csv")
    traj = pd.read_csv(group_dir / "trajectories.csv")

    # Plots de input/output/overlay por caso
    cases = io[["caso", "letra"]].drop_duplicates().itertuples(index=False)
    for caso, letra in cases:
        sub = io[(io["caso"] == caso) & (io["letra"] == letra)].sort_values("pixel")
        inp = sub["input"].to_numpy()
        out = sub["output"].to_numpy()
        if caso == "exp1":
            path = plots_dir / f"exp1_{letra}.png"
            label = f"exp1 — {letra} (almacenada)"
        elif caso.startswith("exp2_"):
            tag = caso.split("_")[1]
            path = plots_dir / f"exp2_{letra}_{tag}.png"
            label = f"exp2 — {letra} con ruido {tag[1:]}%"
        else:
            path = plots_dir / f"exp3_{letra}.png"
            label = f"exp3 — {letra} (no almacenada)"
        plot_io_triplet(inp, out, label, path)

    # Plots de energía y tira de estados (solo casos con trayectoria guardada)
    traj_cases = traj[["caso", "letra"]].drop_duplicates().itertuples(index=False)
    for caso, letra in traj_cases:
        sub = traj[(traj["caso"] == caso) & (traj["letra"] == letra)].sort_values("iter")
        label = f"{caso} — {letra}"
        plot_energy(sub, label, plots_dir / f"energy_{caso}_{letra}.png")
        plot_states_strip(sub, label, plots_dir / f"states_{caso}_{letra}.png")

    plot_outcomes_summary(group_dir, group)
    render_readme(group, group_dir)
    n_plots = len(list(plots_dir.glob("*.png")))
    print(f"  → {group_dir}: {n_plots} plots + README.md")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="hopfield/output", type=Path)
    args = parser.parse_args()
    for group in GROUPS:
        print(f"Grupo {group}:")
        plot_for_group(group, args.output)
    print("Listo.")


if __name__ == "__main__":
    main()
