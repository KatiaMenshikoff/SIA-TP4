"""Genera plots y README.md para los experimentos de capacidad.

Lee CSVs producidos por `capacity_experiments.py` en `output/capacity/p<P>/`
y genera plots + README individuales, más un README raíz en `output/capacity/`
con la tabla resumen y enlaces.

Reusa los helpers de `plot_experiments.py`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plot_experiments import (
    draw_pattern, plot_io_triplet, plot_energy, plot_states_strip,
)


PS = [2, 3, 5, 6]


def plot_outcomes_for_p(p_dir: Path, p: int) -> None:
    """Barras apiladas por fase (exp1, exp2_10, exp2_20) para este p."""
    df = pd.read_csv(p_dir / "summary.csv")
    fases = ["exp1", "exp2_n10", "exp2_n20"]
    counts = {f: df[df["fase"] == f]["outcome"].value_counts().to_dict() for f in fases}
    all_outcomes = sorted({o for d in counts.values() for o in d})
    palette = {"TP": "#4caf50", "FP": "#ff9800", "Espurio": "#9e9e9e",
               "Ciclo": "#9c27b0", "MatchAlmacenado": "#2196f3"}
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=140)
    bottoms = np.zeros(len(fases))
    x = np.arange(len(fases))
    for outcome in all_outcomes:
        vals = np.array([counts[f].get(outcome, 0) for f in fases])
        ax.bar(x, vals, bottom=bottoms, label=outcome,
               color=palette.get(outcome, "#777"))
        bottoms += vals
    ax.set_xticks(x); ax.set_xticklabels(fases, rotation=10)
    ax.set_ylabel("# casos")
    ax.set_title(f"Outcomes — p={p}")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(p_dir / "plots" / "outcomes_summary.png", bbox_inches="tight")
    plt.close(fig)


def render_readme_for_p(p_dir: Path, p: int) -> None:
    group_txt = (p_dir / "group.txt").read_text().strip()
    df = pd.read_csv(p_dir / "summary.csv")

    lines: list[str] = []
    lines.append(f"# Capacidad p={p}\n")
    lines.append(f"```\n{group_txt}\n```\n")
    lines.append("![Outcomes](plots/outcomes_summary.png)\n")

    # Exp1
    exp1 = df[df["fase"] == "exp1"]
    lines.append("## Experimento 1 — almacenados como input\n")
    lines.append("Esperamos punto fijo en 1 iteración. Si alguno NO es estable, "
                 "ya excedimos la capacidad incluso sin ruido.\n")
    lines.append(exp1[["letra", "iters", "motivo", "outcome", "es_fijo",
                       "hamming_final", "energia_inicial", "energia_final"]]
                 .to_markdown(index=False) + "\n")
    for _, row in exp1.iterrows():
        k = row["letra"]
        lines.append(f"### {k} (almacenada)\n")
        lines.append(f"![exp1 {k}](plots/exp1_{k}.png)\n")

    # Exp2
    for noise_tag, noise_pct in [("n10", 10), ("n20", 20)]:
        sub = df[df["fase"] == f"exp2_{noise_tag}"]
        lines.append(f"## Experimento 2 — ruido {noise_pct}%\n")
        lines.append(f"Una muestra determinística por letra (seed=1).\n")
        lines.append(sub[["letra", "iters", "motivo", "convergio_a", "outcome",
                          "hamming_inicial", "hamming_final",
                          "energia_inicial", "energia_final"]]
                     .to_markdown(index=False) + "\n")
        for _, row in sub.iterrows():
            k = row["letra"]
            outcome = row["outcome"]
            extra = f" ({row['convergio_a']})" if pd.notna(row["convergio_a"]) else ""
            lines.append(f"### {k} con ruido {noise_pct}% → {outcome}{extra}\n")
            lines.append(f"![exp2 {k} {noise_tag}](plots/exp2_{k}_{noise_tag}.png)\n")
            lines.append(f"![energía {k} {noise_tag}](plots/energy_exp2_{noise_tag}_{k}.png) "
                         f"![estados {k} {noise_tag}](plots/states_exp2_{noise_tag}_{k}.png)\n")

    (p_dir / "README.md").write_text("\n".join(lines))


def plot_for_p(p: int, capacity_dir: Path) -> None:
    p_dir = capacity_dir / f"p{p}"
    plots_dir = p_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    io = pd.read_csv(p_dir / "io_patterns.csv")
    traj = pd.read_csv(p_dir / "trajectories.csv")

    # Plots input/output/overlay por caso
    cases = io[["caso", "letra"]].drop_duplicates().itertuples(index=False)
    for caso, letra in cases:
        sub = io[(io["caso"] == caso) & (io["letra"] == letra)].sort_values("pixel")
        inp = sub["input"].to_numpy()
        out = sub["output"].to_numpy()
        if caso == "exp1":
            path = plots_dir / f"exp1_{letra}.png"
            label = f"exp1 — {letra} (p={p}, almacenada)"
        else:
            tag = caso.split("_")[1]
            path = plots_dir / f"exp2_{letra}_{tag}.png"
            label = f"exp2 — {letra} con ruido {tag[1:]}% (p={p})"
        plot_io_triplet(inp, out, label, path)

    # Trayectorias (energía + tira de estados)
    traj_cases = traj[["caso", "letra"]].drop_duplicates().itertuples(index=False)
    for caso, letra in traj_cases:
        sub = traj[(traj["caso"] == caso) & (traj["letra"] == letra)].sort_values("iter")
        label = f"{caso} — {letra} (p={p})"
        plot_energy(sub, label, plots_dir / f"energy_{caso}_{letra}.png")
        plot_states_strip(sub, label, plots_dir / f"states_{caso}_{letra}.png")

    plot_outcomes_for_p(p_dir, p)
    render_readme_for_p(p_dir, p)
    n_plots = len(list(plots_dir.glob("*.png")))
    print(f"  → {p_dir}: {n_plots} plots + README.md")


def render_root_readme(capacity_dir: Path) -> None:
    summary = pd.read_csv(capacity_dir / "summary_capacity.csv")

    lines: list[str] = []
    lines.append("# Experimentos de capacidad\n")
    lines.append("Para cada `p ∈ {2, 3, 5, 6}` elegimos el grupo de `p` letras con "
                 "menor `|<,>| medio` (más ortogonal posible) y entrenamos una red.\n")
    lines.append("Capacidad teórica de Hopfield: `~0.15·N = ~3.75 patrones` para N=25. "
                 "Esperamos comportamiento perfecto en p=2,3 y degradación a partir "
                 "de p=5 (excediendo la capacidad teórica).\n")
    lines.append("## Resumen\n")
    lines.append(summary.to_markdown(index=False) + "\n")
    lines.append("## Lectura\n")
    lines.append("- **`fijos_exp1`**: cuántos de los almacenados son punto fijo al pasarles "
                 "su propio patrón limpio. Si no son todos, ya excedimos capacidad.\n")
    lines.append("- **`TP_ruido10` / `TP_ruido20`**: cuántos almacenados se recuperan "
                 "correctamente con ruido del 10% y 20%. Mide la cuenca de atracción.\n")
    lines.append("## Observaciones del experimento\n")
    lines.append("- **p=2, p=3**: todo funciona perfecto. Estamos muy por debajo de la "
                 "capacidad y los grupos son perfectamente ortogonales (`|<,>|=1.0`).\n")
    lines.append("- **p=5**: los 5 almacenados siguen siendo punto fijo, y resisten 10% "
                 "de ruido. Con 20% ya se rompe uno (4/5). La cuenca de atracción se achicó.\n")
    lines.append("- **p=6**: punto fijo OK al pasar los limpios, pero ya con 10% de ruido "
                 "fallan 2 de 6. La capacidad de la red está saturada.\n")
    lines.append("Esto es la **degradación gradual por capacidad** clásica de Hopfield: "
                 "los almacenados pueden seguir siendo estables, pero sus cuencas se "
                 "vuelven más finas hasta que la mínima perturbación los saca.\n")
    lines.append("## Detalle por experimento\n")
    for p in PS:
        lines.append(f"- [p={p}](p{p}/README.md)")
    lines.append("")

    (capacity_dir / "README.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity", default="hopfield/output/capacity", type=Path)
    args = parser.parse_args()
    for p in PS:
        print(f"p = {p}:")
        plot_for_p(p, args.capacity)
    render_root_readme(args.capacity)
    print(f"\nREADME raíz en {args.capacity / 'README.md'}")


if __name__ == "__main__":
    main()
