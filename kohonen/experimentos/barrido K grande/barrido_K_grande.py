"""
Barrido de K en {5, 8, 15, 20} — grillas grandes para un dataset chico.

Pregunta: con N=28 paises, ¿que pasa cuando K^2 >> N? El profesor advirtio
que con K=5 ya estamos al limite (25 celdas / 28 paises); K=15 y K=20 son
casos extremos (225 y 400 celdas) que deberian quedar dominados por
neuronas muertas.

Mantenemos el resto del setup como en el primer barrido:
- grilla rectangular
- R adaptativo de K a 1
- eta adaptativo eta0/i con eta0 = 0.5
- 500 * N = 14 000 iteraciones (no escalamos con K; las grillas grandes
  quedan severamente sub-entrenadas, eso es parte del punto)
- inicializacion de pesos por muestras del set
- 5 semillas por K (menos que en el primer barrido por costo computacional)

Salidas en este directorio.

Uso:
    python3 barrido_K_grande.py
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
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from visualizar import plot_heatmap, plot_u_matrix, export_paises_por_neurona  # noqa: E402


CSV = os.path.abspath(os.path.join(HERE, "..", "..", "..", "SIA-PCA", "europe.csv"))
K_LIST = [5, 8, 15, 20]
SEEDS = list(range(5))

BASE_CONFIG = {
    "grilla": "rectangular",
    "R_modo": "adaptativo",
    "eta_inicial": 0.5,
    "eta_modo": "adaptativo",
    "iteraciones_mult": 500,
}


def per_country_distances(W, X, countries):
    rows = []
    for name, x in zip(countries, X):
        bmu = find_bmu(W, x)
        dist = float(np.linalg.norm(W[bmu] - x))
        rows.append({"country": name, "i": int(bmu[0]), "j": int(bmu[1]), "dist": dist})
    return pd.DataFrame(rows)


def dead_neurons(asgn_df, K):
    used = set(zip(asgn_df["i"], asgn_df["j"]))
    return K * K - len(used)


def run_one(X, countries, K, seed):
    config = dict(BASE_CONFIG)
    config["K"] = K
    config["R_inicial"] = K
    config["seed"] = seed
    rng = np.random.default_rng(seed)
    W, total_iter = train(X, config, rng)
    asgn = per_country_distances(W, X, countries)
    dead_n = dead_neurons(asgn, K)
    qe = float(asgn["dist"].mean())
    return {
        "W": W,
        "asgn": asgn,
        "qe": qe,
        "dead_n": dead_n,
        "dead_frac": dead_n / (K * K),
        "total_iter": total_iter,
        "config": config,
    }


def save_run_artifacts(run, out_dir, var_names):
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
                "variables": var_names,
                "iteraciones_corridas": run["total_iter"],
                "config": run["config"],
            },
            f,
            indent=2,
        )


def plot_qe_dead_vs_k(summary, out, k_first=None):
    Ks = summary["K"].tolist()
    qe_mean = summary["qe_mean"].tolist()
    qe_std = summary["qe_std"].tolist()
    dead_mean = (summary["dead_frac_mean"] * 100).tolist()
    dead_std = (summary["dead_frac_std"] * 100).tolist()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.bar(range(len(Ks)), qe_mean, yerr=qe_std, capsize=6,
            color="#4c72b0", alpha=0.85)
    ax1.set_xticks(range(len(Ks)))
    ax1.set_xticklabels([f"K={k}\n({k*k} cells)" for k in Ks])
    ax1.set_ylabel("QE medio")
    ax1.set_title("Error de cuantizacion vs K")

    ax2.bar(range(len(Ks)), dead_mean, yerr=dead_std, capsize=6,
            color="#c44e52", alpha=0.85)
    ax2.set_xticks(range(len(Ks)))
    ax2.set_xticklabels([f"K={k}\n({k*k} cells)" for k in Ks])
    ax2.set_ylabel("% neuronas muertas")
    ax2.set_title("Fraccion sin asignacion")
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(os.path.join(out, "qe_y_dead_vs_k.png"), dpi=120)
    plt.close()


def pick_median_seed(runs_for_k):
    qes = np.array([r["qe"] for r in runs_for_k])
    median = np.median(qes)
    idx = int(np.argmin(np.abs(qes - median)))
    return runs_for_k[idx], idx


def main():
    df = pd.read_csv(CSV)
    name_col = df.columns[0]
    countries = df[name_col].tolist()
    X_df = df.drop(columns=[name_col])
    var_names = X_df.columns.tolist()
    X = standardize(X_df.values.astype(float))

    all_runs = {}
    rows_per_country = []
    rows_summary = []

    for K in K_LIST:
        print(f"K={K} ({K*K} celdas) — {len(SEEDS)} semillas...")
        all_runs[K] = []
        for seed in SEEDS:
            run = run_one(X, countries, K, seed)
            all_runs[K].append(run)
            for _, r in run["asgn"].iterrows():
                rows_per_country.append({
                    "K": K, "seed": seed, "country": r["country"],
                    "i": int(r["i"]), "j": int(r["j"]), "dist": float(r["dist"]),
                })
            rows_summary.append({
                "K": K, "seed": seed, "qe": run["qe"],
                "dead_n": run["dead_n"], "dead_frac": run["dead_frac"],
            })
            print(f"  seed={seed}: QE={run['qe']:.3f}, dead={run['dead_n']}/{K*K}"
                  f" ({100*run['dead_frac']:.1f}%)")

    per_country_df = pd.DataFrame(rows_per_country)
    runs_df = pd.DataFrame(rows_summary)
    per_country_df.to_csv(os.path.join(HERE, "distancias_por_pais_full.csv"), index=False)
    runs_df.to_csv(os.path.join(HERE, "corridas.csv"), index=False)

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

    plot_qe_dead_vs_k(summary, HERE)

    chosen_seeds = {}
    for K in K_LIST:
        run, idx = pick_median_seed(all_runs[K])
        chosen_seeds[K] = SEEDS[idx]
        sub_out = os.path.join(HERE, f"K{K}_seed{SEEDS[idx]}")
        save_run_artifacts(run, sub_out, var_names)
        plot_heatmap(run["asgn"], K, sub_out)
        plot_u_matrix(run["W"], run["config"]["grilla"], sub_out)
        export_paises_por_neurona(run["asgn"], K, sub_out)
        for src_name, dst_name in [
            ("heatmap_registros.png", f"heatmap_registros_K{K}.png"),
            ("matriz_u.png", f"matriz_u_K{K}.png"),
            ("paises_por_neurona.txt", f"paises_K{K}.txt"),
        ]:
            with open(os.path.join(sub_out, src_name), "rb") as fin, \
                 open(os.path.join(HERE, dst_name), "wb") as fout:
                fout.write(fin.read())

    with open(os.path.join(HERE, "seeds_elegidas.json"), "w") as f:
        json.dump(chosen_seeds, f, indent=2)

    print("\n=== Resumen por K ===")
    print(summary.to_string(index=False))
    print(f"\nSeeds elegidas: {chosen_seeds}")


if __name__ == "__main__":
    main()
