"""Perceptrón de Oja para PC1 sobre europe.csv.

Implementa la regla de Oja tal como se vio en clase (slides 6 y 7 del
PDF "Regla de Oja y Sanger"):

    y     = w · x
    Δw    = η · y · (x − y · w)
    w    ← w + Δw

sobre datos estandarizados (z-score, media 0). El vector de pesos w
converge al **autovector** asociado al mayor autovalor de la matriz de
correlaciones (la primera componente principal). Con ese w_final se
construye PC1 = Σ_i w_i_final · x_i sobre los datos estandarizados.

Características:
    - No supervisado: no se usa ningún target.
    - Sin bias: los datos ya tienen media 0 por la estandarización.
    - Activación lineal (y = w·x, sin θ).
    - Inicialización w ~ Uniforme[0, 1]^n (slide 15).
    - Modo online: una actualización por muestra dentro de cada época.
    - Learning rate configurable: fijo, o variable según schedule
      ("1/t", "1/sqrt_t", "constant").

Pipeline:
    1. Carga CSV y config JSON.
    2. Estandariza features (z-score sobre TODAS las muestras: no hay
       train/test porque no es supervisado).
    3. Inicializa w ~ Uniforme[0, 1]^n.
    4. Entrena online: por época recorre las M muestras una por una y
       actualiza w con la regla de Oja.
    5. Escribe en output/<model_name>_<timestamp>/:
         - convergence.csv      (||w||, ||Δw_epoch|| y η por época)
         - weights_history.csv  (w por época)
         - final_weights.csv    (w_final vs autovector PC1 de numpy.linalg.eig)
         - pc1_per_sample.csv   (proyección PC1 = w_final · x para cada muestra)

Uso:
    python linear_perceptron.py \\
        --config configs/oja_europe.json \\
        --csv ../SIA-PCA/europe.csv \\
        [--output-dir output]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


# ----------------------------- Config & loading ----------------------------- #

REQUIRED_CONFIG_KEYS = {
    "model_name", "id_col", "exclude_features",
    "random_seed", "training", "normalization",
}
REQUIRED_TRAINING_KEYS = {"learning_rate", "epochs", "epsilon"}
VALID_LR_MODES = {"fixed", "variable"}
VALID_LR_SCHEDULES = {"1/t", "1/sqrt_t", "constant"}


def load_config(path: Path) -> dict:
    with open(path) as f:
        config = json.load(f)

    missing = REQUIRED_CONFIG_KEYS - set(config)
    if missing:
        raise ValueError(f"Config inválido: faltan campos {sorted(missing)}")

    missing_t = REQUIRED_TRAINING_KEYS - set(config["training"])
    if missing_t:
        raise ValueError(f"Config.training: faltan campos {sorted(missing_t)}")

    lr = config["training"]["learning_rate"]
    if not isinstance(lr, dict) or "mode" not in lr:
        raise ValueError(
            "Config.training.learning_rate debe ser un dict con clave 'mode'."
        )
    if lr["mode"] not in VALID_LR_MODES:
        raise ValueError(
            f"learning_rate.mode='{lr['mode']}' inválido. "
            f"Usá uno de: {sorted(VALID_LR_MODES)}"
        )
    if lr["mode"] == "fixed":
        if "value" not in lr:
            raise ValueError("learning_rate.mode='fixed' requiere 'value'.")
    else:  # variable
        if "eta_0" not in lr:
            raise ValueError("learning_rate.mode='variable' requiere 'eta_0'.")
        schedule = lr.get("schedule", "1/t")
        if schedule not in VALID_LR_SCHEDULES:
            raise ValueError(
                f"learning_rate.schedule='{schedule}' inválido. "
                f"Usá uno de: {sorted(VALID_LR_SCHEDULES)}"
            )

    if config["normalization"] != "zscore":
        raise NotImplementedError(
            f"normalization='{config['normalization']}' no implementado. "
            "Sólo 'zscore' está soportado (la regla de Oja asume media 0)."
        )

    return config


def load_csv(csv_path: Path, config: dict) -> tuple[pd.DataFrame, list[str]]:
    """Carga el CSV y devuelve (df, feature_cols).

    feature_cols = todas las columnas numéricas excepto id_col y las
    listadas en exclude_features.
    """
    df = pd.read_csv(csv_path)

    id_col = config["id_col"]
    exclude = set(config["exclude_features"])

    if id_col not in df.columns:
        raise ValueError(f"id_col='{id_col}' no está en el CSV.")

    missing_excludes = exclude - set(df.columns)
    if missing_excludes:
        print(
            f"WARNING: exclude_features ignoradas (no están en el CSV): "
            f"{sorted(missing_excludes)}",
            file=sys.stderr,
        )

    reserved = {id_col} | exclude
    feature_cols = [c for c in df.columns if c not in reserved]

    non_numeric = [
        c for c in feature_cols if not pd.api.types.is_numeric_dtype(df[c])
    ]
    if non_numeric:
        raise ValueError(
            f"Features no numéricas: {non_numeric}. "
            "Excluilas vía 'exclude_features' o preprocesalas antes."
        )

    return df, feature_cols


# ----------------------------- Normalization -------------------------------- #

def standardize(X: np.ndarray) -> np.ndarray:
    """Z-score por columna con ddof=1 (varianza muestral, divide por n-1).

    Usamos ddof=1 para que la matriz de correlación X.T @ X / (n-1)
    coincida EXACTAMENTE con la que calcula pandas `.corr()` en
    SIA-PCA/pca_europe.py, y los autovalores de referencia sean los
    mismos que en SIA-PCA/Notas/autovalores_autovectores.md.

    (Difiere de kohonen/kohonen.py:28 que usa ddof=0, divisor n.)
    """
    return (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)


# ----------------------------- Learning rate schedule ----------------------- #

def make_eta_fn(lr_config: dict):
    """Devuelve una función eta(epoch) según la config."""
    mode = lr_config["mode"]
    if mode == "fixed":
        value = float(lr_config["value"])
        return lambda epoch: value

    eta_0 = float(lr_config["eta_0"])
    schedule = lr_config.get("schedule", "1/t")
    if schedule == "1/t":
        return lambda epoch: eta_0 / (1.0 + epoch)
    if schedule == "1/sqrt_t":
        return lambda epoch: eta_0 / np.sqrt(1.0 + epoch)
    if schedule == "constant":
        return lambda epoch: eta_0
    raise ValueError(f"schedule inválido: {schedule}")


# ----------------------------- Oja training --------------------------------- #

def train_oja(
    X: np.ndarray, lr_config: dict, epochs: int, epsilon: float, seed: int,
) -> tuple[np.ndarray, list[dict], list[np.ndarray]]:
    """Entrena la red de Oja online.

    Args:
        X: (M, n) datos estandarizados (media 0).
        lr_config: dict con la config de learning rate.
        epochs: máximo de épocas.
        epsilon: umbral de convergencia sobre ||w_{t+1} − w_t||.
        seed: semilla para la inicialización uniforme [0, 1].

    Returns:
        w_final: (n,) vector final de pesos (≈ autovector PC1).
        convergence: lista de dicts {epoch, eta, w_norm, delta_w_norm}.
        weights_history: lista de w por época (incluye w_inicial en idx 0).
    """
    M, n = X.shape
    rng = np.random.default_rng(seed)
    w = rng.uniform(0.0, 1.0, size=n)  # Slide 15: w ~ Uniforme[0, 1]

    eta_fn = make_eta_fn(lr_config)

    convergence = []
    weights_history = [w.copy()]

    for epoch in range(epochs):
        w_before = w.copy()
        eta = eta_fn(epoch)

        # Online: una actualización por muestra. y se calcula UNA vez por
        # muestra con w actual; los n pesos se actualizan en paralelo.
        for mu in range(M):
            x_mu = X[mu]
            y = float(w @ x_mu)               # escalar
            w = w + eta * y * (x_mu - y * w)  # actualización vectorial

        delta = float(np.linalg.norm(w - w_before))
        w_norm = float(np.linalg.norm(w))

        convergence.append({
            "epoch": epoch,
            "eta": eta,
            "w_norm": w_norm,
            "delta_w_norm": delta,
        })
        weights_history.append(w.copy())

        if delta < epsilon:
            print(
                f"  Convergió en época {epoch}: "
                f"||Δw||={delta:.2e} < ε={epsilon:.0e}"
            )
            break

    return w, convergence, weights_history


# ----------------------------- Reference PCA -------------------------------- #

def pca_reference(X: np.ndarray) -> tuple[float, np.ndarray]:
    """PC1 de referencia con numpy.linalg.eigh sobre la matriz de correlación.

    X ya viene estandarizado, así que XᵀX/(M-1) es la matriz de correlaciones.
    Devuelve (autovalor_max, autovector_max). Signo arbitrario.
    """
    M = X.shape[0]
    R = (X.T @ X) / (M - 1)
    eigvals, eigvecs = np.linalg.eigh(R)  # ascendente
    idx_max = int(np.argmax(eigvals))
    return float(eigvals[idx_max]), eigvecs[:, idx_max]


# ----------------------------- Main ----------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("output"), type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    df, feature_cols = load_csv(args.csv, config)

    print(f"Modelo: {config['model_name']}")
    print(f"Features ({len(feature_cols)}): {feature_cols}")
    print(f"Muestras: {len(df)}")
    lr = config["training"]["learning_rate"]
    if lr["mode"] == "fixed":
        print(f"Learning rate: fijo η = {lr['value']}")
    else:
        print(
            f"Learning rate: variable η₀ = {lr['eta_0']}, "
            f"schedule = '{lr.get('schedule', '1/t')}'"
        )
    print(
        f"Training: epochs={config['training']['epochs']}, "
        f"epsilon={config['training']['epsilon']}, "
        f"seed={config['random_seed']}"
    )
    print()

    # 1. Estandarizar (misma convención que kohonen/kohonen.py)
    X = standardize(df[feature_cols].to_numpy(dtype=float))

    # 2. Entrenar Oja
    w_final, convergence, weights_history = train_oja(
        X,
        lr_config=lr,
        epochs=config["training"]["epochs"],
        epsilon=config["training"]["epsilon"],
        seed=config["random_seed"],
    )

    # 3. Referencia PCA (autovector de la matriz de correlación)
    lambda_max, v_pca = pca_reference(X)

    # Alinear signos para comparación (el autovector de Oja puede salir
    # con signo opuesto y sigue siendo válido).
    sign_aligned = 1.0 if (w_final @ v_pca) >= 0 else -1.0
    v_pca_aligned = sign_aligned * v_pca

    cos_sim = float(
        (w_final @ v_pca) / (np.linalg.norm(w_final) * np.linalg.norm(v_pca))
    )

    print()
    print(f"||w_final|| = {np.linalg.norm(w_final):.6f}  (esperado ≈ 1)")
    print(f"λ_max (PCA librería) = {lambda_max:.6f}")
    print(f"cos(w_final, v_PCA) = {cos_sim:.6f}  (|.| esperado ≈ 1)")
    print()

    # 4. Outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = args.output_dir / f"{config['model_name']}_{timestamp}"
    os.makedirs(run_dir, exist_ok=True)

    # convergence.csv
    convergence_df = pd.DataFrame(convergence)
    convergence_df.to_csv(run_dir / "convergence.csv", index=False)

    # weights_history.csv: una fila por época con todos los pesos
    wh_rows = []
    for epoch_idx, w in enumerate(weights_history):
        row = {"epoch": epoch_idx - 1 if epoch_idx > 0 else "init"}
        for fname, wi in zip(feature_cols, w):
            row[fname] = float(wi)
        wh_rows.append(row)
    pd.DataFrame(wh_rows).to_csv(run_dir / "weights_history.csv", index=False)

    # final_weights.csv: w_oja vs autovector PCA (alineado en signo)
    fw_rows = [
        {"source": "oja", **{f: float(v) for f, v in zip(feature_cols, w_final)}},
        {"source": "pca_eigvec", **{f: float(v) for f, v in zip(feature_cols, v_pca_aligned)}},
        {"source": "diff", **{f: float(a - b) for f, a, b in zip(feature_cols, w_final, v_pca_aligned)}},
    ]
    pd.DataFrame(fw_rows).to_csv(run_dir / "final_weights.csv", index=False)

    # pc1_per_sample.csv: PC1 = w_final · x_estandarizado
    pc1_oja = X @ w_final
    pc1_pca = X @ v_pca_aligned
    id_col = config["id_col"]
    pc1_df = pd.DataFrame({
        id_col: df[id_col].to_numpy(),
        "pc1_oja": pc1_oja,
        "pc1_pca_lib": pc1_pca,
        "diff": pc1_oja - pc1_pca,
    })
    pc1_df.to_csv(run_dir / "pc1_per_sample.csv", index=False)

    # Copia del config (reproducibilidad)
    with open(run_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Resumen final por consola
    print("=== w_final vs autovector PC1 (numpy.linalg.eigh) ===")
    cmp_df = pd.DataFrame({
        "feature": feature_cols,
        "w_oja": w_final,
        "v_pca": v_pca_aligned,
        "diff": w_final - v_pca_aligned,
    })
    print(cmp_df.to_string(index=False))
    print()
    print(f"Outputs en: {run_dir}")


if __name__ == "__main__":
    main()
