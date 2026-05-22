"""
Config nueva (eta_0 = 0.1, recomendada por 'eta y grilla K3/') aplicada a
K=3 y K=5.

K=3 es nuestra eleccion estandar; K=5 es el siguiente paso natural para
ver si con eta mas bajo la grilla mas grande tambien funciona y revela
estructura adicional.

Setup:
- grilla rectangular
- R adaptativo, R(0) = K (lineal a 1)
- eta adaptativo, eta_0 = 0.1
- 500*N = 14 000 iteraciones
- init por muestras
- 10 semillas por K

Salidas en este directorio.

Uso:
    python3 run_config_nueva.py
"""
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from kohonen import standardize, train, find_bmu  # noqa: E402
from visualizar import plot_heatmap, plot_u_matrix, export_paises_por_neurona  # noqa: E402


CSV = os.path.abspath(os.path.join(HERE, "..", "..", "..", "SIA-PCA", "europe.csv"))
K_LIST = [3, 5]
SEEDS = list(range(10))

BASE = {
    "grilla": "rectangular",
    "R_modo": "adaptativo",
    "eta_inicial": 0.1,
    "eta_modo": "adaptativo",
    "iteraciones_mult": 500,
}


def per_country(W, X, countries):
    rows = []
    for n, x in zip(countries, X):
        bmu = find_bmu(W, x)
        d = float(np.linalg.norm(W[bmu] - x))
        rows.append({"country": n, "i": int(bmu[0]), "j": int(bmu[1]), "dist": d})
    return pd.DataFrame(rows)


def dead_count(asgn_df, K):
    used = set(zip(asgn_df["i"], asgn_df["j"]))
    return K * K - len(used)


def run_one(X, countries, K, seed):
    cfg = dict(BASE)
    cfg["K"] = K
    cfg["R_inicial"] = K
    cfg["seed"] = seed
    rng = np.random.default_rng(seed)
    W, total_iter = train(X, cfg, rng)
    asgn = per_country(W, X, countries)
    dead = dead_count(asgn, K)
    qe = float(asgn["dist"].mean())
    return {"W": W, "asgn": asgn, "qe": qe, "dead_n": dead,
            "dead_frac": dead / (K * K), "total_iter": total_iter, "config": cfg}


def save_artifacts(run, out_dir, var_names):
    os.makedirs(out_dir, exist_ok=True)
    W = run["W"]
    K = W.shape[0]
    rows = []
    for i in range(K):
        for j in range(K):
            row = {"i": i, "j": j}
            for k, v in enumerate(var_names):
                row[v] = float(W[i, j, k])
            rows.append(row)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "weights.csv"), index=False)
    run["asgn"].to_csv(os.path.join(out_dir, "assignments.csv"), index=False)
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump({
            "K": K, "variables": var_names,
            "iteraciones_corridas": run["total_iter"],
            "config": run["config"],
        }, f, indent=2)


def pick_median(runs):
    qes = np.array([r["qe"] for r in runs])
    m = np.median(qes)
    idx = int(np.argmin(np.abs(qes - m)))
    return runs[idx], idx


def plot_comparacion(summary, out):
    Ks = summary["K"].tolist()
    qe = summary["qe_mean"].tolist()
    qe_std = summary["qe_std"].tolist()
    dead = (summary["dead_frac_mean"] * 100).tolist()
    dead_std = (summary["dead_frac_std"] * 100).tolist()
    activas = (summary["K"] ** 2 - summary["dead_n_mean"]).tolist()
    totals = (summary["K"] ** 2).tolist()

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    axes[0].bar(range(len(Ks)), qe, yerr=qe_std, capsize=6, color="#4c72b0", alpha=0.85)
    axes[0].set_xticks(range(len(Ks)))
    axes[0].set_xticklabels([f"K={k}" for k in Ks])
    axes[0].set_ylabel("QE medio"); axes[0].set_title("Error de cuantizacion")

    axes[1].bar(range(len(Ks)), dead, yerr=dead_std, capsize=6, color="#c44e52", alpha=0.85)
    axes[1].set_xticks(range(len(Ks)))
    axes[1].set_xticklabels([f"K={k}\n({t} celdas)" for k, t in zip(Ks, totals)])
    axes[1].set_ylabel("% neuronas muertas"); axes[1].set_title("Fraccion sin asignacion")
    axes[1].set_ylim(0, 100)

    axes[2].bar(range(len(Ks)), activas, color="#55a868", alpha=0.85)
    axes[2].set_xticks(range(len(Ks)))
    axes[2].set_xticklabels([f"K={k}\n(de {t})" for k, t in zip(Ks, totals)])
    axes[2].set_ylabel("clusters efectivos")
    axes[2].set_title("Neuronas activas (= clusters)")

    plt.suptitle("Config nueva (η₀=0.1, rect, R adaptativo)", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(out, "comparacion.png"), dpi=120, bbox_inches="tight")
    plt.close()


def main():
    df = pd.read_csv(CSV)
    name_col = df.columns[0]
    countries = df[name_col].tolist()
    X_df = df.drop(columns=[name_col])
    var_names = X_df.columns.tolist()
    X = standardize(X_df.values.astype(float))

    all_runs = {}
    rows_summary = []
    rows_per_country = []

    for K in K_LIST:
        print(f"\n--- K = {K} ({K*K} celdas) ---")
        all_runs[K] = []
        for seed in SEEDS:
            run = run_one(X, countries, K, seed)
            all_runs[K].append(run)
            rows_summary.append({
                "K": K, "seed": seed, "qe": run["qe"],
                "dead_n": run["dead_n"], "dead_frac": run["dead_frac"],
            })
            for _, r in run["asgn"].iterrows():
                rows_per_country.append({
                    "K": K, "seed": seed, "country": r["country"],
                    "i": int(r["i"]), "j": int(r["j"]),
                    "dist": float(r["dist"]),
                })
            print(f"  seed={seed}: QE={run['qe']:.3f}, dead={run['dead_n']}/{K*K}"
                  f" ({100*run['dead_frac']:.1f}%)")

    runs_df = pd.DataFrame(rows_summary)
    per_country_df = pd.DataFrame(rows_per_country)
    runs_df.to_csv(os.path.join(HERE, "corridas.csv"), index=False)
    per_country_df.to_csv(os.path.join(HERE, "distancias_por_pais_full.csv"), index=False)

    summary = runs_df.groupby("K").agg(
        qe_mean=("qe", "mean"),
        qe_std=("qe", "std"),
        dead_n_mean=("dead_n", "mean"),
        dead_frac_mean=("dead_frac", "mean"),
        dead_frac_std=("dead_frac", "std"),
        n_seeds=("seed", "count"),
    ).reset_index()
    summary["total_neuronas"] = summary["K"] ** 2
    summary.to_csv(os.path.join(HERE, "resumen_por_K.csv"), index=False)

    per_country_mean = per_country_df.groupby(["K", "country"]).agg(
        dist_mean=("dist", "mean"),
        dist_std=("dist", "std"),
    ).reset_index()
    per_country_mean.to_csv(os.path.join(HERE, "distancias_por_pais.csv"), index=False)

    plot_comparacion(summary, HERE)

    chosen_seeds = {}
    for K in K_LIST:
        run, idx = pick_median(all_runs[K])
        chosen_seeds[K] = SEEDS[idx]
        sub_out = os.path.join(HERE, f"K{K}_seed{SEEDS[idx]}")
        save_artifacts(run, sub_out, var_names)
        plot_heatmap(run["asgn"], K, sub_out)
        plot_u_matrix(run["W"], run["config"]["grilla"], sub_out)
        export_paises_por_neurona(run["asgn"], K, sub_out)
        for src, dst in [
            ("heatmap_registros.png", f"heatmap_K{K}.png"),
            ("matriz_u.png", f"matriz_u_K{K}.png"),
            ("paises_por_neurona.txt", f"paises_K{K}.txt"),
        ]:
            with open(os.path.join(sub_out, src), "rb") as fin, \
                 open(os.path.join(HERE, dst), "wb") as fout:
                fout.write(fin.read())

    with open(os.path.join(HERE, "seeds_elegidas.json"), "w") as f:
        json.dump(chosen_seeds, f, indent=2)

    print("\n=== Resumen ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
