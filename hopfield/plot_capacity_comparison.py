"""Plots de comparación cross-experimento: mega_exp (p=4) vs mega_exp_capacity (p=2,3,5,6).

Lee los CSVs ya producidos por los dos mega-experimentos y deja los plots
de comparación en `hopfield/output/mega_exp_capacity/plots/` con prefijo
`comparison_`. La idea es que el README de capacity los referencie
directamente.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Colores por valor de `p` — un degradé para que ordenado por p sea legible
P_COLORS = {
    2: "#1565c0",  # azul oscuro
    3: "#2e7d32",  # verde oscuro
    4: "#9e9e9e",  # gris (los p=4 son el "baseline", no destacan)
    5: "#ef6c00",  # naranja
    6: "#c62828",  # rojo
}

# Colores específicos para los grupos individuales (cuando los queremos distinguir)
GROUP_FALLBACK_PALETTE = [
    "#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


def load_combined(base_dir: Path, capacity_dir: Path) -> pd.DataFrame:
    """Combina los `stats_by_group_noise.csv` de ambos experimentos,
    agregando una columna `p` con el tamaño del grupo."""
    m = pd.read_csv(base_dir / "stats_by_group_noise.csv")
    c = pd.read_csv(capacity_dir / "stats_by_group_noise.csv")
    m["p"] = 4
    c["p"] = c["group"].str.len()
    return pd.concat([m, c], ignore_index=True)


def plot_tp_curves_all(combined: pd.DataFrame, out_dir: Path) -> None:
    """Curvas tasa_TP vs ruido para los 9 grupos (4 capacity + 5 baseline).

    El estilo de línea distingue capacity (sólido, grueso) de baseline
    (punteado, fino) para que los p=4 sean visualmente un "fondo" y los
    capacity destaquen.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=140)

    # Baseline p=4 primero (líneas más delgadas, grises/discretas)
    baseline = combined[combined["p"] == 4]
    base_groups = sorted(baseline["group"].unique())
    base_palette = ["#bdbdbd", "#9e9e9e", "#757575", "#616161", "#424242"]
    for i, g in enumerate(base_groups):
        sub = baseline[baseline["group"] == g].sort_values("noise")
        ax.plot(sub["noise"], sub["tasa_TP"],
                color=base_palette[i % len(base_palette)],
                linewidth=1.5, linestyle="--",
                marker="o", markersize=4,
                label=f"{g} (p=4)", alpha=0.8)

    # Capacity por arriba (líneas gruesas, colores destacados)
    capacity = combined[combined["p"] != 4].sort_values("p")
    for g in capacity["group"].unique():
        sub = capacity[capacity["group"] == g].sort_values("noise")
        p = int(sub["p"].iloc[0])
        ax.plot(sub["noise"], sub["tasa_TP"],
                color=P_COLORS[p], linewidth=2.5,
                marker="o", markersize=7,
                label=f"{g} (p={p})")

    ax.set_xlabel("nivel de ruido (p_flip)")
    ax.set_ylabel("tasa de TP")
    ax.set_title("Comparación de TP vs ruido — capacity (p=2,3,5,6) vs baseline (p=4, 5 grupos)")
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9,
              title="grupo (p)")
    fig.tight_layout()
    fig.savefig(out_dir / "comparison_tp_curves_all.png", bbox_inches="tight")
    plt.close(fig)


def plot_mean_tp_by_group(combined: pd.DataFrame, out_dir: Path) -> None:
    """Barras horizontales con tasa_TP promedio por grupo (sobre todos los
    ruidos), coloreadas por p. Muestra el ranking global combinado."""
    means = (
        combined.groupby(["group", "p"])["tasa_TP"].mean()
        .reset_index().sort_values("tasa_TP", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)
    y = np.arange(len(means))
    colors = [P_COLORS[int(p)] for p in means["p"]]
    bars = ax.barh(y, means["tasa_TP"], color=colors,
                   edgecolor="white", linewidth=1.5)
    labels = [f"{g}  (p={int(p)})" for g, p in zip(means["group"], means["p"])]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_xlabel("tasa_TP promedio (sobre 13 niveles de ruido)")
    ax.set_title("Ranking de grupos por tasa_TP promedio — capacity + baseline")
    ax.set_xlim(0, max(means["tasa_TP"]) * 1.18)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    for bar, v in zip(bars, means["tasa_TP"]):
        ax.text(bar.get_width() + max(means["tasa_TP"]) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", ha="left", fontsize=10,
                fontweight="bold", color="#212121")

    # Leyenda de colores p
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=P_COLORS[p], label=f"p={p}") for p in sorted(P_COLORS)]
    ax.legend(handles=handles, loc="lower right", title="cantidad de patrones",
              fontsize=9)

    fig.tight_layout()
    fig.savefig(out_dir / "comparison_mean_tp_by_group.png", bbox_inches="tight")
    plt.close(fig)


def plot_mean_tp_by_p(combined: pd.DataFrame, out_dir: Path) -> None:
    """Bar chart agregado: tasa_TP promedio por valor de p.

    Para p=4 promedia los 5 grupos baseline; para los otros usa el único
    grupo de capacity. Anota cuántos grupos contribuyen.
    """
    agg = (
        combined.groupby("p")
        .agg(tasa_TP=("tasa_TP", "mean"),
             n_grupos=("group", "nunique"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=140)
    x = np.arange(len(agg))
    colors = [P_COLORS[int(p)] for p in agg["p"]]
    bars = ax.bar(x, agg["tasa_TP"], color=colors,
                  edgecolor="white", linewidth=1.5, width=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([f"p = {int(p)}" for p in agg["p"]], fontsize=11,
                       fontweight="bold")
    ax.set_ylabel("tasa_TP promedio (sobre 13 niveles de ruido)")
    ax.set_title("Capacidad: tasa_TP promedio por cantidad de patrones almacenados")
    ax.set_ylim(0, max(agg["tasa_TP"]) * 1.20)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    for bar, row in zip(bars, agg.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(agg["tasa_TP"]) * 0.02,
                f"{row.tasa_TP:.3f}\n(n_grupos={row.n_grupos})",
                ha="center", va="bottom", fontsize=9,
                color="#212121", fontweight="bold")

    # Anotación: capacidad teórica ≈ 0.15·N = 3.75 con N=25
    ax.axvline(x=2.5, color="#37474f", linestyle=":", linewidth=1.5, alpha=0.7)
    ax.text(2.5, max(agg["tasa_TP"]) * 1.08, "capacidad\nteórica ≈ 3.75",
            ha="center", va="top", fontsize=8, color="#37474f", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#eceff1",
                      edgecolor="#37474f", linewidth=0.5))

    fig.tight_layout()
    fig.savefig(out_dir / "comparison_mean_tp_by_p.png", bbox_inches="tight")
    plt.close(fig)


def plot_tp_at_fixed_noise(combined: pd.DataFrame, out_dir: Path) -> None:
    """Bar chart: tasa_TP de cada grupo a un nivel de ruido representativo
    (0.20, donde la separación entre grupos es máxima)."""
    fixed_noise = 0.20
    sub = combined[np.isclose(combined["noise"], fixed_noise)].copy()
    sub = sub.sort_values("tasa_TP", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=140)
    y = np.arange(len(sub))
    colors = [P_COLORS[int(p)] for p in sub["p"]]
    bars = ax.barh(y, sub["tasa_TP"], color=colors,
                   edgecolor="white", linewidth=1.5)
    labels = [f"{g}  (p={int(p)})" for g, p in zip(sub["group"], sub["p"])]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_xlabel("tasa_TP")
    ax.set_title(f"Comparación a ruido fijo = {fixed_noise:.2f}")
    ax.set_xlim(0, 1.10)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    for bar, v in zip(bars, sub["tasa_TP"]):
        ax.text(bar.get_width() + 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", ha="left", fontsize=10,
                fontweight="bold", color="#212121")

    from matplotlib.patches import Patch
    handles = [Patch(facecolor=P_COLORS[p], label=f"p={p}") for p in sorted(P_COLORS)]
    ax.legend(handles=handles, loc="lower right", title="cantidad de patrones",
              fontsize=9)

    fig.tight_layout()
    fig.savefig(out_dir / "comparison_tp_at_noise20.png", bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Comparación cross-experimento de capacidad.")
    parser.add_argument("--baseline", default="hopfield/output/mega_exp", type=Path)
    parser.add_argument("--capacity", default="hopfield/output/mega_exp_capacity", type=Path)
    args = parser.parse_args()

    out_dir = args.capacity / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    combined = load_combined(args.baseline, args.capacity)
    print(f"Combinado: {len(combined)} filas ({combined['group'].nunique()} grupos)")

    plot_tp_curves_all(combined, out_dir)
    plot_mean_tp_by_group(combined, out_dir)
    plot_mean_tp_by_p(combined, out_dir)
    plot_tp_at_fixed_noise(combined, out_dir)

    print(f"Plots de comparación en {out_dir}")


if __name__ == "__main__":
    main()
