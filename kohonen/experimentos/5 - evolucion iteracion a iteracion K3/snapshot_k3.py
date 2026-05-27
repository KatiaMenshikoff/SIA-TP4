"""
Entrena un SOM K=3 sobre europe.csv y graba en cada iteracion el estado
de los pesos y las asignaciones BMU.

Salidas en este directorio:
- weights_evolution.csv     : formato largo, columnas iter, i, j, var1..var7
- assignments_evolution.csv : formato largo, columnas iter, country, i, j, dist
- som_data.js               : datos sub-sampleados (denso al inicio) para visor.html

La idea: validar la hipotesis de que las neuronas muertas son neuronas cuyos
pesos quedaron atrapados en el centro de la nube de datos y nunca ganan.

Uso: python3 snapshot_k3.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
# kohonen.py vive dos niveles arriba (en kohonen/)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from kohonen import standardize, init_weights, find_bmu, neuron_distance  # noqa: E402

CSV = os.path.abspath(os.path.join(HERE, "..", "..", "..", "SIA-PCA", "europe.csv"))

# --- hiperparametros (fijos al setup del barrido) ---
K = 3
R0 = K
ETA0 = 0.5
ITER_MULT = 500
SEED = 2  # seed "mediana" del barrido K=3


def get_radius(i, total, R0):
    if total <= 1:
        return R0
    return max(1.0, R0 - (R0 - 1.0) * ((i - 1) / (total - 1)))


def get_eta(i, eta0):
    return eta0 / i


def precompute_D(K, grid_type="rectangular"):
    D = np.zeros((K, K, K, K))
    for i in range(K):
        for j in range(K):
            for a in range(K):
                for b in range(K):
                    D[i, j, a, b] = neuron_distance((i, j), (a, b), grid_type)
    return D


def compute_assignments(W, X, names):
    out = []
    for n, x in zip(names, X):
        bmu = find_bmu(W, x)
        d = float(np.linalg.norm(W[bmu] - x))
        out.append({"country": n, "i": int(bmu[0]), "j": int(bmu[1]), "dist": d})
    return out


def compute_umatrix(W, K):
    U = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            vecinos = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                a, b = i + di, j + dj
                if 0 <= a < K and 0 <= b < K:
                    vecinos.append(float(np.linalg.norm(W[i, j] - W[a, b])))
            if vecinos:
                U[i, j] = float(np.mean(vecinos))
    return U


def build_sample_iters(total):
    """Sub-sampleo para el visor: denso al inicio, ralo al final."""
    s = set()
    for it in range(0, 51):           # 0..50 todo
        s.add(it)
    for it in range(50, 501, 5):      # cada 5 hasta 500
        s.add(it)
    for it in range(500, 5001, 50):   # cada 50 hasta 5000
        s.add(it)
    for it in range(5000, total + 1, 200):  # cada 200 hasta el final
        s.add(it)
    return s


def main():
    df = pd.read_csv(CSV)
    name_col = df.columns[0]
    countries = df[name_col].tolist()
    X_df = df.drop(columns=[name_col])
    var_names = X_df.columns.tolist()
    X = standardize(X_df.values.astype(float))
    N = X.shape[0]
    total_iter = ITER_MULT * N  # 14000

    rng = np.random.default_rng(SEED)
    W = init_weights(X, K, rng)
    D = precompute_D(K)

    weights_rows = []   # long: iter, i, j, var1..var7
    asgn_rows = []      # long: iter, country, i, j, dist
    frames = []         # subsample para el visor

    sample_iters = build_sample_iters(total_iter)

    def snapshot(it, samples_to_visor):
        # weights largo (TODAS las iter)
        for i in range(K):
            for j in range(K):
                row = {"iter": it, "i": i, "j": j}
                for k, v in enumerate(var_names):
                    row[v] = float(W[i, j, k])
                weights_rows.append(row)
        # assignments largo (TODAS las iter)
        asgn = compute_assignments(W, X, countries)
        for r in asgn:
            asgn_rows.append({"iter": it, **r})
        # frame para visor (sub-sample)
        if samples_to_visor:
            counts = np.zeros((K, K), dtype=int)
            for a in asgn:
                counts[a["i"], a["j"]] += 1
            U = compute_umatrix(W, K)
            frames.append({
                "iter": it,
                "counts": counts.tolist(),
                "umatrix": U.tolist(),
                "qe": float(np.mean([a["dist"] for a in asgn])),
                "dead": int((counts == 0).sum()),
                "assignments": asgn,
            })

    # iter 0: estado inicial (sin updates)
    snapshot(0, 0 in sample_iters)

    for i in range(1, total_iter + 1):
        p = rng.integers(0, N)
        x = X[p]
        bmu = find_bmu(W, x)
        R = get_radius(i, total_iter, R0)
        eta = get_eta(i, ETA0)
        mask = D[bmu[0], bmu[1]] < R
        W[mask] += eta * (x - W[mask])
        snapshot(i, i in sample_iters)

    pd.DataFrame(weights_rows).to_csv(
        os.path.join(HERE, "weights_evolution.csv"), index=False
    )
    pd.DataFrame(asgn_rows).to_csv(
        os.path.join(HERE, "assignments_evolution.csv"), index=False
    )

    js_data = {
        "K": K,
        "variables": var_names,
        "total_iter": total_iter,
        "seed": SEED,
        "R0": R0,
        "eta0": ETA0,
        "frames": frames,
    }
    with open(os.path.join(HERE, "som_data.js"), "w") as f:
        f.write("// Datos del SOM K=3, evolucion por iteracion.\n")
        f.write("// Generado por snapshot_k3.py — sub-sample denso al inicio.\n")
        f.write("var SOM_DATA = " + json.dumps(js_data) + ";\n")

    print(f"Snapshots crudos: {len(weights_rows) // (K * K)} iteraciones")
    print(f"Frames para visor: {len(frames)}")
    print(f"  weights_evolution.csv   ({len(weights_rows):,} filas)")
    print(f"  assignments_evolution.csv  ({len(asgn_rows):,} filas)")
    print(f"  som_data.js")


if __name__ == "__main__":
    main()
