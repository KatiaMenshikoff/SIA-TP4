"""
Mini-barrido para K=3: 2 learning rates x 2 tipos de grilla.

  eta_0 in {0.1, 0.3}  x  grilla in {rectangular, hexagonal}

Pregunta: ¿bajando eta_0 (atacando el "colapso temprano" diagnosticado en
evolucion K3) y/o cambiando a grilla hexagonal (suavizando el efecto borde)
podemos lograr que sobrevivan mas de 2 clusters?

Setup fijo:
- K = 3
- R adaptativo, R(0) = K = 3 (lineal a 1)
- 500 * N = 14 000 iteraciones
- init por muestras
- 10 semillas por config

Salidas en este directorio.

Uso:
    python3 barrido_eta_grilla.py
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
K = 3
ETAS = [0.1, 0.3]
GRIDS = ["rectangular", "hexagonal"]
SEEDS = list(range(10))


def per_country_distances(W, X, countries):
    rows = []
    for name, x in zip(countries, X):
        bmu = find_bmu(W, x)
        d = float(np.linalg.norm(W[bmu] - x))
        rows.append({"country": name, "i": int(bmu[0]), "j": int(bmu[1]), "dist": d})
    return pd.DataFrame(rows)


def dead_count(asgn_df, K):
    used = set(zip(asgn_df["i"], asgn_df["j"]))
    return K * K - len(used)


def run_one(X, countries, eta0, grid, seed):
    config = {
        "K": K,
        "grilla": grid,
        "R_inicial": K,
        "R_modo": "adaptativo",
        "eta_inicial": eta0,
        "eta_modo": "adaptativo",
        "iteraciones_mult": 500,
        "seed": seed,
    }
    rng = np.random.default_rng(seed)
    W, total_iter = train(X, config, rng)
    asgn = per_country_distances(W, X, countries)
    dead = dead_count(asgn, K)
    qe = float(asgn["dist"].mean())
    return {
        "W": W,
        "asgn": asgn,
        "qe": qe,
        "dead_n": dead,
        "dead_frac": dead / (K * K),
        "total_iter": total_iter,
        "config": config,
    }


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
        json.dump(
            {
                "K": K,
                "grilla": run["config"]["grilla"],
                "eta_inicial": run["config"]["eta_inicial"],
                "variables": var_names,
                "iteraciones_corridas": run["total_iter"],
                "config": run["config"],
            }, f, indent=2,
        )


def pick_median_seed(runs):
    qes = np.array([r["qe"] for r in runs])
    median = np.median(qes)
    idx = int(np.argmin(np.abs(qes - median)))
    return runs[idx], idx


def label_for(eta, grid):
    return f"η={eta}, {grid}"


def short_id(eta, grid):
    return f"eta{eta}_{grid[:4]}"


def plot_comparacion(summary, out):
    labels = [label_for(r["eta_inicial"], r["grilla"]) for _, r in summary.iterrows()]
    qe = summary["qe_mean"].tolist()
    qe_std = summary["qe_std"].tolist()
    dead = (summary["dead_frac_mean"] * 100).tolist()
    dead_std = (summary["dead_frac_std"] * 100).tolist()
    activas = (K * K - summary["dead_n_mean"]).tolist()

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    x = range(len(labels))

    axes[0].bar(x, qe, yerr=qe_std, capsize=6, color="#4c72b0", alpha=0.85)
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("QE medio"); axes[0].set_title("Error de cuantizacion")

    axes[1].bar(x, dead, yerr=dead_std, capsize=6, color="#c44e52", alpha=0.85)
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_ylabel("% neuronas muertas")
    axes[1].set_title("Fraccion sin asignacion (de 9 celdas)")
    axes[1].set_ylim(0, 100)

    axes[2].bar(x, activas, color="#55a868", alpha=0.85)
    axes[2].set_xticks(x); axes[2].set_xticklabels(labels, rotation=20, ha="right")
    axes[2].set_ylabel("clusters efectivos")
    axes[2].set_title("Neuronas activas (= clusters)")
    axes[2].set_ylim(0, K * K)
    axes[2].axhline(2, color="gray", ls="--", lw=0.8)
    axes[2].text(0.02, 2.15, "baseline (η=0.5, rect): ~2-3", color="gray", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(out, "comparacion.png"), dpi=120)
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

    for eta in ETAS:
        for grid in GRIDS:
            key = (eta, grid)
            print(f"\n--- η={eta}, grilla={grid} ---")
            all_runs[key] = []
            for seed in SEEDS:
                run = run_one(X, countries, eta, grid, seed)
                all_runs[key].append(run)
                rows_summary.append({
                    "eta_inicial": eta,
                    "grilla": grid,
                    "seed": seed,
                    "qe": run["qe"],
                    "dead_n": run["dead_n"],
                    "dead_frac": run["dead_frac"],
                })
                for _, r in run["asgn"].iterrows():
                    rows_per_country.append({
                        "eta_inicial": eta, "grilla": grid, "seed": seed,
                        "country": r["country"],
                        "i": int(r["i"]), "j": int(r["j"]),
                        "dist": float(r["dist"]),
                    })
                print(f"  seed={seed}: QE={run['qe']:.3f}, dead={run['dead_n']}/9")

    runs_df = pd.DataFrame(rows_summary)
    per_country_df = pd.DataFrame(rows_per_country)
    runs_df.to_csv(os.path.join(HERE, "corridas.csv"), index=False)
    per_country_df.to_csv(os.path.join(HERE, "distancias_por_pais_full.csv"), index=False)

    summary = runs_df.groupby(["eta_inicial", "grilla"]).agg(
        qe_mean=("qe", "mean"),
        qe_std=("qe", "std"),
        dead_n_mean=("dead_n", "mean"),
        dead_frac_mean=("dead_frac", "mean"),
        dead_frac_std=("dead_frac", "std"),
        n_seeds=("seed", "count"),
    ).reset_index()
    summary.to_csv(os.path.join(HERE, "resumen.csv"), index=False)

    per_country_mean = per_country_df.groupby(["eta_inicial", "grilla", "country"]).agg(
        dist_mean=("dist", "mean"),
        dist_std=("dist", "std"),
    ).reset_index()
    per_country_mean.to_csv(os.path.join(HERE, "distancias_por_pais.csv"), index=False)

    plot_comparacion(summary, HERE)

    chosen_seeds = {}
    for eta in ETAS:
        for grid in GRIDS:
            key = (eta, grid)
            run, idx = pick_median_seed(all_runs[key])
            chosen_seeds[f"{eta}_{grid}"] = SEEDS[idx]
            sid = short_id(eta, grid)
            sub_out = os.path.join(HERE, f"{sid}_seed{SEEDS[idx]}")
            save_artifacts(run, sub_out, var_names)
            plot_heatmap(run["asgn"], K, sub_out)
            plot_u_matrix(run["W"], grid, sub_out)
            export_paises_por_neurona(run["asgn"], K, sub_out)
            for src, dst in [
                ("heatmap_registros.png", f"heatmap_{sid}.png"),
                ("matriz_u.png", f"matriz_u_{sid}.png"),
                ("paises_por_neurona.txt", f"paises_{sid}.txt"),
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
