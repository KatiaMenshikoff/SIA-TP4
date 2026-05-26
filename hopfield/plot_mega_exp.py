"""Plots para el mega-experimento de barrido de ruido.

Lee los CSVs producidos por `noise_sweep_experiment.py` y genera:

  - `tp_curves_by_group.png`         : tasa_TP vs ruido, una línea por grupo.
  - `outcomes_stacked_global.png`    : outcomes apilados por ruido (todos los grupos).
  - `outcomes_stacked_by_group.png`  : small multiples, una grilla por grupo.
  - `heatmap_tp.png`                 : heatmap tasa_TP (grupos × ruidos).
  - `heatmap_complement.png`         : heatmap tasa_COMPLEMENT.
  - `<grupo>_overlay_grid.png`       : 4 letras × 9 ruidos de overlays input/output
                                       para los trials representantes.
  - `<grupo>_outcomes_by_letter.png` : barras apiladas por (letra, ruido) del grupo.

Convención del overlay (igual que en `plot_experiments.py`):
  - input=+1 ∧ output=+1 → verde claro  (match en pixel encendido)
  - input=-1 ∧ output=-1 → blanco       (match en pixel apagado)
  - input ≠ output       → rojo         (mismatch: la red flippeó ese pixel)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


GROUPS = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
# NOISE_LEVELS se rellena en `main()` desde la data (sorted unique del CSV),
# para que los plots se adapten si se agregan más niveles con extend_noise_experiment.
NOISE_LEVELS: list[float] = []
OUTCOMES = ["TP", "FP", "FN", "COMPLEMENT", "CICLO"]

# Paleta consistente entre todos los plots
OUTCOME_COLORS = {
    "TP":         "#4caf50",  # verde
    "FP":         "#ff9800",  # naranja
    "FN":         "#9e9e9e",  # gris
    "COMPLEMENT": "#7e57c2",  # violeta
    "CICLO":      "#42a5f5",  # azul
}

# Colores de los overlays
COLOR_BG = "#ffffff"
COLOR_ON = "#222222"
COLOR_MATCH_ON = "#a8e6a3"   # verde claro: match en +1
COLOR_MATCH_OFF = "#ffffff"  # blanco:      match en -1
COLOR_MISMATCH = "#e04848"   # rojo:        mismatch

# Color de cada grupo en los plots cross-cutting
GROUP_COLORS = {
    "GRTV": "#1f77b4",
    "JLRX": "#2ca02c",
    "AJKU": "#ff7f0e",
    "BDOX": "#d62728",
    "HMNW": "#9467bd",
}


# ---------------------------------------------------------------------------
# Plots cross-cutting (agregados)
# ---------------------------------------------------------------------------

def plot_tp_curves(stats_gn: pd.DataFrame, out_dir: Path) -> None:
    """Curva tasa_TP vs ruido, una línea por grupo."""
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=140)
    for group in GROUPS:
        sub = stats_gn[stats_gn["group"] == group].sort_values("noise")
        ax.plot(sub["noise"], sub["tasa_TP"], marker="o",
                color=GROUP_COLORS[group], label=group, linewidth=2)
    ax.set_xlabel("nivel de ruido (p_flip)")
    ax.set_ylabel("tasa de TP")
    ax.set_title("Tasa de recuperación correcta (TP) vs ruido por grupo")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(title="grupo", loc="upper right")
    fig.tight_layout()
    fig.savefig(out_dir / "tp_curves_by_group.png", bbox_inches="tight")
    plt.close(fig)


def plot_outcomes_stacked_global(trials: pd.DataFrame, out_dir: Path) -> None:
    """Barras apiladas: distribución de outcomes por nivel de ruido (todos los grupos juntos)."""
    counts = (
        trials.groupby(["noise", "outcome"]).size()
        .unstack(fill_value=0)
        .reindex(columns=OUTCOMES, fill_value=0)
    )
    totals = counts.sum(axis=1)
    proportions = counts.div(totals, axis=0)

    fig, ax = plt.subplots(figsize=(max(8, 0.65 * len(NOISE_LEVELS)), 4.5), dpi=140)
    bottom = np.zeros(len(proportions))
    x = np.arange(len(proportions))
    for outcome in OUTCOMES:
        vals = proportions[outcome].to_numpy()
        ax.bar(x, vals, bottom=bottom, label=outcome,
               color=OUTCOME_COLORS[outcome], edgecolor="white", linewidth=0.5)
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n:.2f}" for n in proportions.index], rotation=45)
    ax.set_xlabel("nivel de ruido")
    ax.set_ylabel("proporción de trials")
    ax.set_title("Distribución de outcomes por ruido (todos los grupos)")
    ax.set_ylim(0, 1)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), title="outcome")
    fig.tight_layout()
    fig.savefig(out_dir / "outcomes_stacked_global.png", bbox_inches="tight")
    plt.close(fig)


def plot_outcomes_stacked_by_group(trials: pd.DataFrame, out_dir: Path) -> None:
    """5 subplots, uno por grupo: outcomes apilados por ruido."""
    fig, axes = plt.subplots(1, 5, figsize=(18, 4), dpi=140, sharey=True)
    for ax, group in zip(axes, GROUPS):
        sub = trials[trials["group"] == group]
        counts = (
            sub.groupby(["noise", "outcome"]).size()
            .unstack(fill_value=0)
            .reindex(columns=OUTCOMES, fill_value=0)
        )
        totals = counts.sum(axis=1)
        proportions = counts.div(totals, axis=0)

        bottom = np.zeros(len(proportions))
        x = np.arange(len(proportions))
        for outcome in OUTCOMES:
            vals = proportions[outcome].to_numpy()
            ax.bar(x, vals, bottom=bottom,
                   color=OUTCOME_COLORS[outcome], edgecolor="white", linewidth=0.3,
                   label=outcome if group == GROUPS[0] else None)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels([f"{n:.2f}" for n in proportions.index], rotation=45, fontsize=8)
        ax.set_title(f"{group}", fontsize=11)
        ax.set_xlabel("ruido", fontsize=9)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("proporción")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", title="outcome",
               bbox_to_anchor=(1.005, 0.5))
    fig.suptitle("Distribución de outcomes por ruido — por grupo", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "outcomes_stacked_by_group.png", bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(stats_gn: pd.DataFrame, column: str, title: str,
                 cmap: str, out_path: Path) -> None:
    """Heatmap genérico de una columna `tasa_X` indexado por (group, noise)."""
    matrix = (
        stats_gn.pivot(index="group", columns="noise", values=column)
        .reindex(index=GROUPS, columns=NOISE_LEVELS)
    )

    fig, ax = plt.subplots(figsize=(max(8, 0.7 * len(NOISE_LEVELS)), 3.5), dpi=140)
    im = ax.imshow(matrix.to_numpy(), aspect="auto", cmap=cmap,
                   vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks(range(len(NOISE_LEVELS)))
    ax.set_xticklabels([f"{n:.2f}" for n in NOISE_LEVELS])
    ax.set_yticks(range(len(GROUPS)))
    ax.set_yticklabels(GROUPS)
    ax.set_xlabel("nivel de ruido")
    ax.set_ylabel("grupo")
    ax.set_title(title)

    # Anotar cada celda con el valor
    for i, group in enumerate(GROUPS):
        for j, noise in enumerate(NOISE_LEVELS):
            v = matrix.iloc[i, j]
            txt_color = "white" if v > 0.5 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color=txt_color, fontsize=8)

    fig.colorbar(im, ax=ax, label=column)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plots por grupo: overlays en grilla 4 letras × 9 ruidos
# ---------------------------------------------------------------------------

def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    return tuple(int(h[i:i+2], 16) / 255 for i in (1, 3, 5))


def _overlay_array(inp: np.ndarray, out: np.ndarray) -> np.ndarray:
    """Construye un (5, 5, 3) de colores para el overlay."""
    grid_in = inp.reshape(5, 5)
    grid_out = out.reshape(5, 5)
    colors = np.empty((5, 5, 3))
    rgb_match_on = _hex_to_rgb(COLOR_MATCH_ON)
    rgb_match_off = _hex_to_rgb(COLOR_MATCH_OFF)
    rgb_mismatch = _hex_to_rgb(COLOR_MISMATCH)
    for i in range(5):
        for j in range(5):
            a, b = grid_in[i, j], grid_out[i, j]
            if a > 0 and b > 0:
                colors[i, j] = rgb_match_on
            elif a < 0 and b < 0:
                colors[i, j] = rgb_match_off
            else:
                colors[i, j] = rgb_mismatch
    return colors


def plot_overlay_grid_for_group(
    group: str, io_df: pd.DataFrame, trials_df: pd.DataFrame, out_dir: Path,
) -> None:
    """Genera una grilla 4 (letras) × 9 (ruidos) de overlays, con el outcome
    anotado debajo de cada celda. Usa solo los representantes (sample_idx=0)."""
    group_keys = list(group)
    fig, axes = plt.subplots(
        len(group_keys), len(NOISE_LEVELS),
        figsize=(1.5 * len(NOISE_LEVELS), 1.7 * len(group_keys)),
        dpi=140,
    )
    if len(group_keys) == 1:
        axes = np.array([axes])

    for i, letter in enumerate(group_keys):
        for j, noise in enumerate(NOISE_LEVELS):
            ax = axes[i, j]
            sub = io_df[
                (io_df["group"] == group)
                & (io_df["letter"] == letter)
                & (io_df["noise"] == noise)
                & (io_df["sample_idx"] == 0)
            ].sort_values("pixel")
            if len(sub) == 0:
                ax.axis("off")
                continue
            inp = sub["input"].to_numpy()
            out = sub["output"].to_numpy()
            colors = _overlay_array(inp, out)
            ax.imshow(colors)
            ax.set_xticks(np.arange(-0.5, 5, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, 5, 1), minor=True)
            ax.grid(which="minor", color="black", linewidth=0.5)
            ax.set_xticks([]); ax.set_yticks([])

            # Outcome del trial (de trials_df)
            tr = trials_df[
                (trials_df["group"] == group)
                & (trials_df["letter"] == letter)
                & (trials_df["noise"] == noise)
                & (trials_df["sample_idx"] == 0)
            ]
            outcome = tr["outcome"].iloc[0] if len(tr) else ""
            convergio = tr["convergio_a"].iloc[0] if len(tr) else ""
            label = outcome
            if pd.notna(convergio) and convergio != "":
                label = f"{outcome}\n({convergio})"
            ax.set_xlabel(label, fontsize=7,
                          color=OUTCOME_COLORS.get(outcome, "black"))

            if i == 0:
                ax.set_title(f"{noise:.2f}", fontsize=9)
            if j == 0:
                ax.set_ylabel(letter, fontsize=11, rotation=0, labelpad=12,
                              va="center")

    fig.suptitle(
        f"Grupo {group} — overlays input/output del representante (sample_idx=0)\n"
        "verde claro = match +1, blanco = match -1, rojo = mismatch",
        fontsize=11, y=1.01,
    )
    fig.tight_layout()
    fig.savefig(out_dir / f"{group}_overlay_grid.png", bbox_inches="tight")
    plt.close(fig)


def plot_outcomes_by_letter_for_group(
    group: str, trials_df: pd.DataFrame, out_dir: Path,
) -> None:
    """4 subplots (uno por letra del grupo) con outcomes apilados por ruido."""
    group_keys = list(group)
    fig, axes = plt.subplots(1, len(group_keys),
                             figsize=(4 * len(group_keys), 3.5),
                             dpi=140, sharey=True)
    if len(group_keys) == 1:
        axes = [axes]

    for ax, letter in zip(axes, group_keys):
        sub = trials_df[
            (trials_df["group"] == group) & (trials_df["letter"] == letter)
        ]
        counts = (
            sub.groupby(["noise", "outcome"]).size()
            .unstack(fill_value=0)
            .reindex(columns=OUTCOMES, fill_value=0)
        )
        totals = counts.sum(axis=1)
        proportions = counts.div(totals, axis=0)

        bottom = np.zeros(len(proportions))
        x = np.arange(len(proportions))
        for outcome in OUTCOMES:
            vals = proportions[outcome].to_numpy()
            ax.bar(x, vals, bottom=bottom,
                   color=OUTCOME_COLORS[outcome], edgecolor="white",
                   linewidth=0.3, label=outcome if letter == group_keys[0] else None)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels([f"{n:.2f}" for n in proportions.index],
                           rotation=45, fontsize=8)
        ax.set_title(f"letra {letter}")
        ax.set_xlabel("ruido")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("proporción")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", title="outcome",
               bbox_to_anchor=(1.01, 0.5))
    fig.suptitle(f"Grupo {group} — outcomes por letra y ruido", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / f"{group}_outcomes_by_letter.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Distribución global y tabla de outcomes por ruido
# ---------------------------------------------------------------------------

def plot_outcomes_global_bar(trials: pd.DataFrame, out_dir: Path) -> None:
    """Barras horizontales con la distribución global de outcomes (todos los trials)."""
    counts = trials["outcome"].value_counts()
    counts = counts.reindex(OUTCOMES).fillna(0).astype(int)
    # Ordenar de mayor a menor para que el ranking sea visualmente obvio
    counts = counts.sort_values(ascending=True)
    total = int(counts.sum())

    fig, ax = plt.subplots(figsize=(9, 4), dpi=140)
    y = np.arange(len(counts))
    bars = ax.barh(y, counts.to_numpy(),
                   color=[OUTCOME_COLORS[o] for o in counts.index],
                   edgecolor="white", linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels(counts.index, fontsize=11, fontweight="bold")
    ax.set_xlabel(f"# trials  (total: {total:,})")
    ax.set_title(f"Distribución global de outcomes — {total:,} trials")
    ax.set_xlim(0, counts.max() * 1.20)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Etiqueta con n + porcentaje al final de cada barra
    for bar, val in zip(bars, counts.to_numpy()):
        pct = 100 * val / total
        ax.text(bar.get_width() + counts.max() * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,}  ({pct:.1f}%)",
                va="center", ha="left", fontsize=10, fontweight="bold",
                color="#212121")

    # Pequeña leyenda de qué significa cada outcome
    legend_text = ("TP=recupera target  ·  FP=converge a otro almacenado  ·  "
                   "COMPLEMENT=converge a -ξ_k  ·  CICLO=no converge  ·  FN=espurio mixto")
    ax.text(0.5, -0.20, legend_text, transform=ax.transAxes,
            ha="center", va="top", fontsize=8, color="#607d8b", style="italic")

    fig.tight_layout()
    fig.savefig(out_dir / "outcomes_global_bar.png", bbox_inches="tight")
    plt.close(fig)


def plot_outcomes_table_by_noise(trials: pd.DataFrame, out_dir: Path) -> None:
    """Tabla coloreada con outcomes × niveles de ruido.

    Cada celda se tintea por intensidad dentro de su columna (más saturado
    = más trials), usando la paleta del repo por outcome.
    """
    # Ordeno columnas como en la paleta: CICLO, COMPLEMENT, FN, FP, TP (alfabético)
    col_order = sorted(OUTCOMES)
    counts = (
        trials.groupby(["noise", "outcome"]).size()
        .unstack(fill_value=0)
        .reindex(columns=col_order, fill_value=0)
        .sort_index()
    )
    noises = counts.index.to_numpy()
    data = counts.to_numpy()
    n_rows, n_cols = data.shape
    total_per_row = int(data.sum(axis=1)[0])  # mismo en todas las filas
    col_max = data.max(axis=0)

    def col_cmap(hex_color: str) -> LinearSegmentedColormap:
        return LinearSegmentedColormap.from_list("col", ["#ffffff", hex_color])

    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=200)
    ax.set_xlim(0, n_cols + 1)
    ax.set_ylim(0, n_rows + 2)
    ax.axis("off")

    cell_h = 1.0
    cw_noise = 1.0
    cw_data = 1.0

    ax.text((n_cols + 1) / 2, n_rows + 1.5,
            f"Outcomes por nivel de ruido  ({total_per_row} trials por fila)",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#212121")

    # Header
    ax.add_patch(patches.Rectangle((0, n_rows), cw_noise, cell_h,
                                    facecolor="#37474f",
                                    edgecolor="white", lw=1.5))
    ax.text(cw_noise / 2, n_rows + cell_h / 2, "ruido",
            ha="center", va="center", fontsize=11, fontweight="bold",
            color="white")

    for j, outcome in enumerate(col_order):
        x = cw_noise + j * cw_data
        ax.add_patch(patches.Rectangle((x, n_rows), cw_data, cell_h,
                                        facecolor=OUTCOME_COLORS[outcome],
                                        edgecolor="white", lw=1.5))
        ax.text(x + cw_data / 2, n_rows + cell_h / 2, outcome,
                ha="center", va="center", fontsize=11, fontweight="bold",
                color="white")

    # Filas (ruido bajo arriba)
    for i in range(n_rows):
        y = n_rows - 1 - i
        ax.add_patch(patches.Rectangle((0, y), cw_noise, cell_h,
                                        facecolor="#eceff1",
                                        edgecolor="white", lw=1.0))
        ax.text(cw_noise / 2, y + cell_h / 2, f"{noises[i]:.2f}",
                ha="center", va="center", fontsize=10,
                color="#212121", fontweight="bold")

        for j, outcome in enumerate(col_order):
            x = cw_noise + j * cw_data
            val = data[i, j]
            intensity = val / col_max[j] if col_max[j] > 0 else 0
            cmap = col_cmap(OUTCOME_COLORS[outcome])
            bg = cmap(0.15 + 0.7 * intensity)
            rgb = np.array(bg[:3])
            lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
            text_color = "white" if lum < 0.55 else "#212121"

            ax.add_patch(patches.Rectangle((x, y), cw_data, cell_h,
                                            facecolor=bg,
                                            edgecolor="white", lw=1.0))
            ax.text(x + cw_data / 2, y + cell_h / 2, f"{int(val)}",
                    ha="center", va="center", fontsize=11,
                    color=text_color,
                    fontweight="bold" if intensity > 0.5 else "normal")

    ax.text((n_cols + 1) / 2, -0.3,
            "Color saturado = mayor cantidad de trials dentro de la columna  ·  "
            "paleta del repo (TP=verde, FP=naranja, COMPLEMENT=violeta, FN=gris, CICLO=azul)",
            ha="center", va="center", fontsize=8,
            color="#607d8b", style="italic")

    fig.tight_layout()
    fig.savefig(out_dir / "outcomes_table_by_noise.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Energía: una figura con la trayectoria del representante peor de cada grupo
# ---------------------------------------------------------------------------

def plot_energy_examples(
    traj: pd.DataFrame, trials: pd.DataFrame, out_dir: Path,
) -> None:
    """Una figura con 5 subplots: para cada grupo, energía vs iter de un
    representante "interesante" (el que más iteraciones tardó)."""
    fig, axes = plt.subplots(1, 5, figsize=(18, 3.2), dpi=140, sharey=False)
    for ax, group in zip(axes, GROUPS):
        # Elijo el representante con más iters dentro del grupo
        reps_group = trials[(trials["group"] == group) & (trials["sample_idx"] == 0)]
        if len(reps_group) == 0:
            ax.axis("off")
            continue
        winner = reps_group.sort_values("iters", ascending=False).iloc[0]
        letter = winner["letter"]
        noise = winner["noise"]
        outcome = winner["outcome"]

        sub = traj[
            (traj["group"] == group)
            & (traj["letter"] == letter)
            & (traj["noise"] == noise)
            & (traj["sample_idx"] == 0)
        ].sort_values("iter")

        ax.plot(sub["iter"], sub["energia"], marker="o",
                color=GROUP_COLORS[group], linewidth=2)
        ax.set_xlabel("iter")
        ax.set_ylabel("H(S)")
        ax.set_title(
            f"{group} — {letter} @ ruido {noise:.2f}\n{outcome} ({int(winner['iters'])} iters)",
            fontsize=9,
        )
        ax.grid(True, alpha=0.3)
    fig.suptitle("Energía vs iteración — representantes con más iteraciones por grupo",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "energy_longest_per_group.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Plots del mega-experimento.")
    parser.add_argument("--input", default="hopfield/output/mega_exp", type=Path,
                        help="Directorio donde están los CSVs del experimento.")
    args = parser.parse_args()

    in_dir: Path = args.input
    out_dir = in_dir / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Leyendo CSVs...")
    trials = pd.read_csv(in_dir / "trials.csv")
    stats_gn = pd.read_csv(in_dir / "stats_by_group_noise.csv")
    io_df = pd.read_csv(in_dir / "io_patterns.csv")
    traj = pd.read_csv(in_dir / "trajectories.csv")
    print(f"  trials: {len(trials)}  stats_gn: {len(stats_gn)}  io: {len(io_df)}  traj: {len(traj)}")

    # Derivar los niveles de ruido del dataset (admite extensiones via extend_noise_experiment)
    global NOISE_LEVELS
    NOISE_LEVELS = sorted(trials["noise"].unique().tolist())
    print(f"  niveles de ruido: {NOISE_LEVELS}")

    print("Plots cross-cutting...")
    plot_tp_curves(stats_gn, out_dir)
    plot_outcomes_global_bar(trials, out_dir)
    plot_outcomes_table_by_noise(trials, out_dir)
    plot_outcomes_stacked_global(trials, out_dir)
    plot_outcomes_stacked_by_group(trials, out_dir)
    plot_heatmap(stats_gn, "tasa_TP",
                 "Tasa de TP por grupo y nivel de ruido",
                 "viridis", out_dir / "heatmap_tp.png")
    plot_heatmap(stats_gn, "tasa_COMPLEMENT",
                 "Tasa de COMPLEMENT por grupo y nivel de ruido",
                 "magma", out_dir / "heatmap_complement.png")
    plot_energy_examples(traj, trials, out_dir)

    print("Plots por grupo (overlays + outcomes por letra)...")
    for group in GROUPS:
        plot_overlay_grid_for_group(group, io_df, trials, out_dir)
        plot_outcomes_by_letter_for_group(group, trials, out_dir)
        print(f"  {group}")

    n_plots = len(list(out_dir.glob("*.png")))
    print(f"Listo. {n_plots} plots en {out_dir}")


if __name__ == "__main__":
    main()
