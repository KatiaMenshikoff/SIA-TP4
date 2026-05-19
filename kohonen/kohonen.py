"""
Red de Kohonen (SOM) — clustering de paises.

Sigue el material de catedra:
- Estandarizacion z-score de las variables.
- Inicializacion de pesos con muestras al azar del set (mitiga neuronas muertas).
- Regla de Kohonen: W_j^{i+1} = W_j^i + eta(i) * (X^p - W_j^i) si j esta en el vecindario.
- Radio y learning rate: fijos o adaptativos (R va de K a 1; eta(i) = eta0/i).
- Cantidad de iteraciones: fija, o multiplicador * N (N = cantidad de muestras).
- Grilla rectangular o hexagonal (la diferencia es como se mide distancia entre neuronas).

Uso:
    python kohonen.py --csv ../SIA-PCA/europe.csv --config config.json
"""
import argparse
import json
import os

import numpy as np
import pandas as pd


def load_config(path):
    with open(path) as f:
        return json.load(f)


def standardize(X):
    return (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)


def init_weights(X, K, rng):
    n_samples, n_features = X.shape
    idx = rng.integers(0, n_samples, size=K * K)
    return X[idx].reshape(K, K, n_features).copy()


def neuron_distance(a, b, grid_type):
    ai, aj = a
    bi, bj = b
    if grid_type == "rectangular":
        return np.hypot(ai - bi, aj - bj)
    if grid_type == "hexagonal":
        # even-r offset: filas impares desplazadas 0.5 a la derecha,
        # altura vertical entre filas = sqrt(3)/2.
        ax = aj + 0.5 * (ai % 2)
        bx = bj + 0.5 * (bi % 2)
        ay = ai * np.sqrt(3) / 2
        by = bi * np.sqrt(3) / 2
        return np.hypot(ax - bx, ay - by)
    raise ValueError(f"grilla desconocida: {grid_type}")


def get_radius(i, total_iter, R0, mode):
    if mode == "fijo":
        return R0
    if mode == "adaptativo":
        if total_iter <= 1:
            return R0
        return max(1.0, R0 - (R0 - 1.0) * ((i - 1) / (total_iter - 1)))
    raise ValueError(f"R_modo desconocido: {mode}")


def get_eta(i, eta0, mode):
    if mode == "fijo":
        return eta0
    if mode == "adaptativo":
        return eta0 / i
    raise ValueError(f"eta_modo desconocido: {mode}")


def find_bmu(W, x):
    dists = np.linalg.norm(W - x, axis=2)
    return np.unravel_index(np.argmin(dists), dists.shape)


def train(X, config, rng):
    K = config["K"]
    R0 = config["R_inicial"]
    R_modo = config["R_modo"]
    eta0 = config["eta_inicial"]
    eta_modo = config["eta_modo"]
    grid_type = config["grilla"]

    n_samples = X.shape[0]
    if "iteraciones" in config:
        total_iter = int(config["iteraciones"])
    else:
        total_iter = int(config["iteraciones_mult"] * n_samples)

    W = init_weights(X, K, rng)

    # Pre-computamos la matriz de distancias entre neuronas (es fija).
    coords = [(i, j) for i in range(K) for j in range(K)]
    D = np.zeros((K, K, K, K))
    for (i, j) in coords:
        for (a, b) in coords:
            D[i, j, a, b] = neuron_distance((i, j), (a, b), grid_type)

    for i in range(1, total_iter + 1):
        p = rng.integers(0, n_samples)
        x = X[p]

        bmu = find_bmu(W, x)
        R = get_radius(i, total_iter, R0, R_modo)
        eta = get_eta(i, eta0, eta_modo)

        mask = D[bmu[0], bmu[1]] < R  # shape (K, K)
        # actualizacion vectorizada: solo donde mask=True
        W[mask] += eta * (x - W[mask])

    return W, total_iter


def assignments(W, X, country_names):
    rows = []
    for name, x in zip(country_names, X):
        bmu = find_bmu(W, x)
        dist = float(np.linalg.norm(W[bmu] - x))
        rows.append({"country": name, "i": int(bmu[0]), "j": int(bmu[1]), "dist": dist})
    return pd.DataFrame(rows)


def dump_weights(W, var_names, path):
    K = W.shape[0]
    rows = []
    for i in range(K):
        for j in range(K):
            row = {"i": i, "j": j}
            for k, var in enumerate(var_names):
                row[var] = float(W[i, j, k])
            rows.append(row)
    pd.DataFrame(rows).to_csv(path, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="dataset csv (1ra columna: nombre)")
    ap.add_argument("--config", required=True, help="archivo de hiperparametros")
    ap.add_argument("--out", default="resultados", help="directorio de salida")
    args = ap.parse_args()

    config = load_config(args.config)

    df = pd.read_csv(args.csv)
    name_col = df.columns[0]
    countries = df[name_col].values
    X_df = df.drop(columns=[name_col])
    var_names = X_df.columns.tolist()
    X = standardize(X_df.values.astype(float))

    rng = np.random.default_rng(config.get("seed", 42))
    W, total_iter = train(X, config, rng)

    os.makedirs(args.out, exist_ok=True)
    dump_weights(W, var_names, os.path.join(args.out, "weights.csv"))
    assignments(W, X, countries).to_csv(
        os.path.join(args.out, "assignments.csv"), index=False
    )
    with open(os.path.join(args.out, "metadata.json"), "w") as f:
        json.dump(
            {
                "K": config["K"],
                "grilla": config["grilla"],
                "variables": var_names,
                "iteraciones_corridas": total_iter,
                "n_muestras": int(X.shape[0]),
                "config": config,
            },
            f,
            indent=2,
        )

    print(f"Listo en {args.out}/")
    print(f"  weights.csv      ({config['K']**2} neuronas x {len(var_names)} vars)")
    print(f"  assignments.csv  ({len(countries)} paises)")
    print(f"  metadata.json    (iteraciones={total_iter})")


if __name__ == "__main__":
    main()
