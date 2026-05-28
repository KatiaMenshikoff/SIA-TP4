# SIA-TP4 — Aprendizaje No Supervisado

Trabajo práctico 4 de Sistemas de Inteligencia Artificial (ITBA, 2026). Cuatro ejercicios sobre métodos de aprendizaje no supervisado.

## Ejercicios

1. **PCA** sobre `europe.csv` (28 países × 7 variables), con librería — `SIA-PCA/`.
2. **Kohonen (SOM)** sobre el mismo dataset, implementado a mano — `kohonen/`.
3. **Regla de Oja**, implementada a mano, comparada contra PCA — `oja/`.
4. **Hopfield** (memoria asociativa) sobre el abecedario 5×5 — `hopfield/`.

## Datasets

- `SIA-PCA/europe.csv` — 28 países europeos con `Area, GDP, Inflation, Life.expect, Military, Pop.growth, Unemployment`. Usado en (1), (2) y (3).
- `hopfield/letters.txt` — abecedario A–Z dibujado a mano en grillas 5×5 (`*` / `-`, separador `=`). Usado en (4).

## Instalación

Requiere Python 3 (el `python` del sistema apunta a Python 2.7, usar `python3`).

```bash
pip install -r requirements.txt
```

## Comandos principales

```bash
# 1) PCA
cd SIA-PCA && python3 pca_europe.py

# 2) Kohonen
cd kohonen && python3 kohonen.py --csv ../SIA-PCA/europe.csv --config config.json

# 3) Oja
cd oja && python3 linear_perceptron.py

# 4) Hopfield — demo CLI
cd hopfield && python3 hopfield.py --group GRTV --query G --noise 0.15

# 4) Hopfield — experimentos completos
PYTHONPATH=hopfield python3 hopfield/run_experiments.py
python3 hopfield/plot_experiments.py
```

Los scripts de `hopfield/` que importan entre sí necesitan `PYTHONPATH=hopfield` (o correrlos desde dentro del directorio).

## Documentación

- `docs/consigna.pdf` — enunciado oficial del TP.
- `docs/resumen-todas-clases-TP4.md` — resumen indexado de las clases.
- `docs/clases/` — material original por tema (PDFs + transcripts).
- `CLAUDE.md` — guía detallada de la estructura del repo y de cada ejercicio.

Los informes específicos de cada ejercicio están en sus respectivos directorios (`SIA-PCA/analisis.pdf`, `kohonen/experimentos.md`, `oja/implementacion y resultados.md`, `hopfield/Implementación.md`).
