"""
Plot R(i) y cantidad de neuronas muertas vs iteracion, marcando los
umbrales criticos del vecindario para K=3 rectangular.

Lee assignments_evolution.csv y produce R_vs_dead.png.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

K = 3
TOTAL = 14000
R0 = 3.0


def R(i):
    return np.maximum(1.0, R0 - (R0 - 1.0) * ((i - 1) / (TOTAL - 1)))


def main():
    asgn = pd.read_csv(os.path.join(HERE, "assignments_evolution.csv"))

    dead_per_iter = []
    iters = sorted(asgn["iter"].unique())
    for it in iters:
        sub = asgn[asgn["iter"] == it]
        counts = np.zeros((K, K), int)
        for _, r in sub.iterrows():
            counts[int(r["i"]), int(r["j"])] += 1
        dead_per_iter.append((counts == 0).sum())
    iters = np.array(iters)
    dead = np.array(dead_per_iter)

    Rs = R(iters)

    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    # R(i): linea azul
    color_R = "#1f77b4"
    ax1.plot(iters, Rs, color=color_R, lw=2, label="R(i)")
    ax1.set_xlabel("iteracion")
    ax1.set_ylabel("radio del vecindario  R(i)", color=color_R)
    ax1.tick_params(axis="y", labelcolor=color_R)
    ax1.set_xlim(0, TOTAL)
    ax1.set_ylim(0.8, 3.2)

    # umbrales criticos para K=3 rectangular
    thresholds = [
        (np.sqrt(8), "$R=\\sqrt{8}\\approx 2.828$\n(esquinas opuestas)"),
        (np.sqrt(5), "$R=\\sqrt{5}\\approx 2.236$\n(esquina ↔ celda lejana)"),
        (2.0,        "$R=2$"),
        (np.sqrt(2), "$R=\\sqrt{2}\\approx 1.414$\n(diagonales)"),
        (1.0,        "$R=1$\n(solo BMU)"),
    ]
    for thr, label in thresholds:
        # encontrar iter donde R(i) = thr
        i_cross = (R0 - thr) * (TOTAL - 1) / (R0 - 1) + 1
        ax1.axhline(thr, color="gray", linestyle=":", lw=0.7, alpha=0.5)
        ax1.axvline(i_cross, color="gray", linestyle=":", lw=0.7, alpha=0.4)
        ax1.annotate(
            label,
            xy=(i_cross, thr),
            xytext=(i_cross + 200, thr + 0.05),
            fontsize=8,
            color="#555",
            ha="left",
        )

    # dead: linea roja, eje derecho
    ax2 = ax1.twinx()
    color_dead = "#c44e52"
    ax2.plot(iters, dead, color=color_dead, lw=2, label="neuronas muertas")
    ax2.set_ylabel("neuronas muertas (de 9)", color=color_dead)
    ax2.tick_params(axis="y", labelcolor=color_dead)
    ax2.set_ylim(-0.3, 9.3)
    ax2.set_yticks(range(0, 10))

    # leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", framealpha=0.9)

    plt.title(
        "Radio del vecindario y neuronas muertas — K=3, schedule lineal\n"
        "Las transiciones en 'dead' coinciden con los cruces de R por umbrales criticos"
    )
    plt.tight_layout()
    out = os.path.join(HERE, "R_vs_dead.png")
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Guardado: {out}")


if __name__ == "__main__":
    main()
