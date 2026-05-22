"""
Barrido de K en {2, 3, 4} para elegir el tamano de grilla del SOM.

Por cada (K, semilla) se entrena un SOM con el resto de hiperparametros fijos:
- grilla rectangular
- R adaptativo de K a 1
- eta adaptativo eta0/i con eta0 = 0.5
- 500 * N iteraciones
- inicializacion de pesos por muestras del set

Por cada corrida se guardan:
- distancia BMU por pais (no solo el promedio)
- % de neuronas muertas
- weights, assignments

Y se generan plots:
- qe_y_dead_vs_k.png       : barras de QE media y % muertas vs K (con bandas std)
- distancias_por_pais.png  : heatmap pais x K con distancia promediada sobre semillas
- heatmap_registros_K{K}.png  : conteo de paises por neurona (seed mediana)
- matriz_u_K{K}.png            : matriz U (seed mediana)
- paises_K{K}.txt              : que paises caen en cada neurona (seed mediana)

Uso:
    python3 barrido_k.py
"""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from kohonen import (
    standardize,
    init_weights,
    find_bmu,
    train,
)
from visualizar import plot_heatmap, plot_u_matrix, export_paises_por_neurona


CSV = "../SIA-PCA/europe.csv"
OUT = "barrido"
K_LIST = [2, 3, 4]
SEEDS = list(range(10))  # 10 semillas por K

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
    total = K * K
    dead = total - len(used)
    return dead, dead / total


def run_one(X, countries, K, seed):
    config = dict(BASE_CONFIG)
    config["K"] = K
    config["R_inicial"] = K
    config["seed"] = seed
    rng = np.random.default_rng(seed)
    W, total_iter = train(X, config, rng)
    asgn = per_country_distances(W, X, countries)
    dead_n, dead_frac = dead_neurons(asgn, K)
    qe = float(asgn["dist"].mean())
    return {
        "W": W,
        "asgn": asgn,
        "qe": qe,
        "dead_n": dead_n,
        "dead_frac": dead_frac,
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


def plot_qe_dead_vs_k(summary, out):
    Ks = summary["K"].tolist()
    qe_mean = summary["qe_mean"].tolist()
    qe_std = summary["qe_std"].tolist()
    dead_mean = (summary["dead_frac_mean"] * 100).tolist()
    dead_std = (summary["dead_frac_std"] * 100).tolist()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

    ax1.bar(Ks, qe_mean, yerr=qe_std, capsize=6, color="#4c72b0", alpha=0.85)
    ax1.set_xlabel("K")
    ax1.set_ylabel("Error de cuantizacion medio")
    ax1.set_title("QE = distancia media pais -> BMU")
    ax1.set_xticks(Ks)

    ax2.bar(Ks, dead_mean, yerr=dead_std, capsize=6, color="#c44e52", alpha=0.85)
    ax2.set_xlabel("K")
    ax2.set_ylabel("% neuronas muertas")
    ax2.set_title("Fraccion de neuronas sin asignacion")
    ax2.set_xticks(Ks)

    plt.tight_layout()
    plt.savefig(os.path.join(out, "qe_y_dead_vs_k.png"), dpi=120)
    plt.close()


def plot_distancias_por_pais(per_country, countries, out):
    # per_country: DataFrame con columnas country, K, dist_mean
    pivot = per_country.pivot(index="country", columns="K", values="dist_mean")
    pivot = pivot.reindex(countries)  # orden estable

    fig, ax = plt.subplots(figsize=(6, max(6, len(countries) * 0.28)))
    im = ax.imshow(pivot.values, cmap="magma", aspect="auto")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"K={k}" for k in pivot.columns])
    ax.set_title("Distancia promedio pais -> BMU\n(promediada sobre semillas)")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j]:.2f}", ha="center", va="center",
                    color="white", fontsize=8)
    plt.colorbar(im, ax=ax, label="distancia euclidea")
    plt.tight_layout()
    plt.savefig(os.path.join(out, "distancias_por_pais.png"), dpi=120)
    plt.close()


def pick_median_seed(runs_for_k):
    """Devuelve el run cuyo QE es el mas cercano al QE mediano del grupo."""
    qes = np.array([r["qe"] for r in runs_for_k])
    median = np.median(qes)
    idx = int(np.argmin(np.abs(qes - median)))
    return runs_for_k[idx], idx


def main():
    os.makedirs(OUT, exist_ok=True)

    df = pd.read_csv(CSV)
    name_col = df.columns[0]
    countries = df[name_col].tolist()
    X_df = df.drop(columns=[name_col])
    var_names = X_df.columns.tolist()
    X = standardize(X_df.values.astype(float))

    # --- correr todas las combinaciones ---
    all_runs = {}
    rows_per_country = []   # K, seed, country, i, j, dist
    rows_summary = []       # K, seed, qe, dead_n, dead_frac

    for K in K_LIST:
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

    per_country_df = pd.DataFrame(rows_per_country)
    runs_df = pd.DataFrame(rows_summary)

    per_country_df.to_csv(os.path.join(OUT, "distancias_por_pais_full.csv"), index=False)
    runs_df.to_csv(os.path.join(OUT, "corridas.csv"), index=False)

    # --- resumen por K ---
    summary = runs_df.groupby("K").agg(
        qe_mean=("qe", "mean"),
        qe_std=("qe", "std"),
        dead_n_mean=("dead_n", "mean"),
        dead_frac_mean=("dead_frac", "mean"),
        dead_frac_std=("dead_frac", "std"),
        n_seeds=("seed", "count"),
    ).reset_index()
    summary["total_neuronas"] = summary["K"] ** 2
    summary.to_csv(os.path.join(OUT, "resumen_por_K.csv"), index=False)

    # --- distancia por pais promediada sobre semillas, por K ---
    per_country_mean = per_country_df.groupby(["K", "country"]).agg(
        dist_mean=("dist", "mean"),
        dist_std=("dist", "std"),
    ).reset_index()
    per_country_mean.to_csv(os.path.join(OUT, "distancias_por_pais.csv"), index=False)

    # --- plots resumen ---
    plot_qe_dead_vs_k(summary, OUT)
    plot_distancias_por_pais(per_country_mean, countries, OUT)

    # --- artefactos de la seed mediana por K ---
    chosen_seeds = {}
    for K in K_LIST:
        run, idx = pick_median_seed(all_runs[K])
        chosen_seeds[K] = SEEDS[idx]
        sub_out = os.path.join(OUT, f"K{K}_seed{SEEDS[idx]}")
        save_run_artifacts(run, sub_out, var_names)
        # plots reutilizando visualizar.py
        plot_heatmap(run["asgn"], K, sub_out)
        plot_u_matrix(run["W"], run["config"]["grilla"], sub_out)
        export_paises_por_neurona(run["asgn"], K, sub_out)
        # copia "presentable" en el dir raiz del barrido
        for src_name, dst_name in [
            ("heatmap_registros.png", f"heatmap_registros_K{K}.png"),
            ("matriz_u.png", f"matriz_u_K{K}.png"),
            ("paises_por_neurona.txt", f"paises_K{K}.txt"),
        ]:
            with open(os.path.join(sub_out, src_name), "rb") as fin, \
                 open(os.path.join(OUT, dst_name), "wb") as fout:
                fout.write(fin.read())

    with open(os.path.join(OUT, "seeds_elegidas.json"), "w") as f:
        json.dump(chosen_seeds, f, indent=2)

    # --- resumen a stdout ---
    print("\n=== Resumen por K ===")
    print(summary.to_string(index=False))
    print(f"\nSeeds 'mediana' elegidas para los plots representativos: {chosen_seeds}")
    print(f"\nSalidas en {OUT}/")


if __name__ == "__main__":
    main()
