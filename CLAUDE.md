# CLAUDE.md

Guidance for Claude Code (claude.ai/code) on this repo.

## NO PONER CLAUDE COAUTOR

Nunca agregar `Co-Authored-By: Claude` (ni ninguna variante) en los mensajes de commit. Los commits van **sin** trailer de co-autoría.

## Contexto del repo

Trabajo práctico **SIA-TP4 — Aprendizaje No Supervisado** (Sistemas de Inteligencia Artificial, 2026). Cuatro ejercicios:

1. **PCA** sobre `europe.csv` (28 países × 7 variables), con librería.
2. **Kohonen (SOM)** sobre el mismo dataset, implementado a mano.
3. **Regla de Oja**, implementada a mano, comparada contra PCA.
4. **Hopfield** (memoria asociativa) sobre el abecedario 5×5.

Dataset principal del bloque (1)–(3): `SIA-PCA/europe.csv` (`Country, Area, GDP, Inflation, Life.expect, Military, Pop.growth, Unemployment`).
Dataset del bloque (4): `hopfield/letters.txt` (A–Z en grillas 5×5 con `*`/`-`).

## Regla principal: no usar técnicas que no se vieron en clase

Lo único que importa es que no metas métodos, fórmulas o trucos que no estén en el material de cátedra. Si una idea no aparece ahí, avisame antes de usarla. Para chequear qué se vio:

- `docs/resumen-todas-clases-TP4.md` — resumen indexado de las clases con citas del profesor. Suele alcanzar como referencia rápida.
- `docs/clases/aprendizaje-no-supervisado-kohonen/` — PDFs + transcript `kohonen.VTT`.
- `docs/clases/pca-oja/` — PDFs *Autovalores y Autovectores*, *PCA*, *Regla de Oja y Sanger* + transcript `pca_oja.VTT`.
- `docs/clases/hopfield/` — clase de Euge (`hopfield.VTT`) + clase de Santi sobre ortogonalidad de letras (`hopfield_ortogonalidad_letras.VTT`) + screenshots en `ortogonalidad/`.
- `docs/clases/presentacion-tp-consigna/presentacion_consigna.VTT` — clase donde se presentó el TP.
- `docs/consigna.pdf` — enunciado oficial.
- `docs/apuntes_notas_clase.md` — apuntes sueltos (biplot, Oja, learning rates).

Cosas que el profesor remarcó:

- **Estandarizar las entradas** (z-score) en Kohonen, PCA y Oja — `europe.csv` mezcla `Area` (~10⁵) con `Pop.growth` (~0.1).
- **PCA solo tiene sentido si hay correlación** entre las variables.
- **Oja converge al autovector de PC1, no a PC1**. La componente se arma después como combinación lineal con `a_i = w_i^final`.
- Comparando Oja vs PCA-librería, el autovector puede salir con **signo opuesto** y sigue siendo válido.
- Para Kohonen: análisis variando `k`, radio `R`, tipo de grilla e inicialización, reportando heatmap, matriz U y activación por variable.
- PCA va con librería; **Oja se implementa a mano**.
- Para Hopfield: clase de Euge da el algoritmo y la energía; clase de Santi explica por qué preferir grupos de patrones de **`|⟨,⟩| medio` chico**.

## Estructura — qué archivo va con qué ejercicio

### 1) PCA — `SIA-PCA/`

PCA usando librería (sklearn / numpy). Sigue los 7 pasos de la slide 32 de la teórica.

- `europe.csv` — el dataset (28 países × 7 features).
- `pca_europe.py` — script principal "cátedra-por-cátedra": estandariza, calcula matriz de correlaciones, descompone, proyecta a PC1, arma biplot.
- `generate_pptx.py` — regenera `PCA_europe_seguimiento.pptx` (presentación con los 7 pasos como slides).
- `PCA_europe_seguimiento.pptx` — presentación de seguimiento.
- `boxplot_original.png`, `boxplot_estandarizado.png` — boxplots antes/después de z-score.
- `biplot.png` — biplot de PC1 vs PC2 con las flechas de cargas (slide 45).
- `pc1_por_pais.png` — ranking de países por PC1 (slide 46).
- `analisis.pdf` — informe final entregable del ejercicio.
- `audio_transcript.VTT` — transcript de la clase asociada.
- `Pasted image 20260513*.png` — capturas de slides referenciadas desde notas.
- `Notas/` — análisis interpretativo en Markdown:
  - `analisis.md` — documento principal de interpretación (qué dice cada componente, cluster de países).
  - `matriz_correlaciones.md` — tabla auto-generada por `pca_europe.py`.
  - `autovalores_autovectores.md` — tabla auto-generada por `pca_europe.py`.

### 2) Kohonen (SOM) — `kohonen/`

SOM implementado a mano sobre `europe.csv`.

- `kohonen.md` — consigna + apuntes del ejercicio.
- `kohonen.py` — implementación del SOM (entrenamiento, BMU, vecindad gaussiana, decay de η y R).
- `config.json` — hiperparámetros default (`k`, η inicial, R inicial, iteraciones, etc.).
- `barrido_k.py` — script que corre múltiples configuraciones variando `k` para el análisis.
- `visualizar.py` — genera heatmap de activación, U-matrix, y mapas de activación por variable.
- `experimentos.md` — bitácora de los experimentos corridos, con interpretación.
- `experimentos/` — outputs de cada corrida (organizadas por configuración):
  - `barrido K grande/`, `barrido K primer intento/`
  - `config nueva K3 K5/`
  - `eta y grilla K3/`
  - `evolucion K3/`

### 3) Regla de Oja — `oja/`

Oja a mano (no librería), comparado contra PCA.

- `linear_perceptron.py` — implementación del perceptrón lineal con regla de Oja (`Δw = η·y·(x − y·w)`).
- `step_perceptron.py` — perceptrón con función paso (referencia / comparación; NO se usa en la entrega final de Oja).
- `implementacion y resultados.md` — informe del ejercicio.
- `Explicacion coseno y norma.md` — nota técnica: por qué se mide convergencia con similitud coseno y norma del vector de pesos.
- `Explicacion ddof y divergencia.md` — nota sobre `ddof=0` vs `ddof=1` en la estandarización y su impacto en la comparación con `sklearn.PCA`.
- `configs/` — archivos `.json` con hiperparámetros de distintas corridas.
- `output/` — resultados (CSVs de evolución de pesos, plots de convergencia).
- `imagenes/` — capturas usadas en `implementacion y resultados.md`.

### 4) Hopfield — `hopfield/`

Hopfield desde cero. Memoria asociativa con letras 5×5.

**Núcleo (modelo y datos):**
- `letters.txt` — abecedario A–Z dibujado a mano (formato `*`/`-`, separador `=`).
- `hopfield.py` — clase `Hopfield` (pesos por Hebb, actualización síncrona, energía). Funciones auxiliares: `load_letters`, `add_noise`, `ascii_letter`. Tiene un CLI demo en `main()`.
- `Implementación.md` — decisiones de diseño (regla `sign(0)=previous`, condición de corte para ciclos, etc.).
- `README.md` — overview del directorio.

**Selección de grupos:**
- `Seleccion patrones letras.md` — análisis de ortogonalidad: por qué los 5 grupos elegidos (`GRTV`, `JLRX`, `AJKU`, `BDOX`, `HMNW`) y los 4 de capacidad (`AL`, `FUY`, `GMPVZ`, `JLRTVX`).
- `ortogonalidad_letras.ipynb` — notebook tipo Santi: calcula `|⟨ξ_i, ξ_j⟩|` medio y máximo para todas las combinaciones de 4 letras.

**Experimentos canónicos (5 grupos × 4 letras):**
- `run_experiments.py` — corre 3 experimentos por grupo:
  - `exp1` — almacenado limpio como input (debe ser punto fijo).
  - `exp2` — ruido 10/20/65% (un sample por nivel).
  - `exp3` — letras no almacenadas (2 similares + 3 distintas) como input.
  - Output en `output/<grupo>/*.csv`.
- `plot_experiments.py` — genera los plots y `README.md` per-grupo en `output/<grupo>/plots/`.

**Experimento de capacidad chico:**
- `capacity_experiments.py` — para `p ∈ {2,3,5,6}`: elige el "mejor grupo" por ortogonalidad y mide si los almacenados son punto fijo + recuperación a 10%/20% de ruido (1 sample). Output en `output/capacity/p<P>/`.
- `plot_capacity.py` — plots del experimento de capacidad chico.

**Mega-experimento de barrido fino de ruido (5 grupos × 4 letras):**
- `noise_sweep_experiment.py` — barrido base: 9 niveles de ruido (`[0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]`), 30 samples por config. Clasifica cada trial en **TP / FP / FN / COMPLEMENT / CICLO**. Output en `output/mega_exp/`.
- `extend_noise_experiment.py` — extiende con 4 niveles más (`0.05, 0.15, 0.25, 0.35`), idempotente. Deja el dataset en 13 niveles, **7800 trials**.
- `test_noise_sweep.py` — pytest con 14 tests para `classify_trial`, `resolve_convergio_a`, `_write_stats`.

**Mega-experimento de capacidad (p ∈ {2,3,5,6}):**
- `noise_sweep_capacity_experiment.py` — replica el barrido fino sobre los grupos `AL`, `FUY`, `GMPVZ`, `JLRTVX`. Output en `output/mega_exp_capacity/`. **6240 trials** ((2+3+5+6) × 13 × 30).

**Plots de los mega-experimentos:**
- `plot_mega_exp.py` — genera 18 plots a partir de los CSVs (curvas TP, heatmaps, stacked bars, overlays por grupo, tabla coloreada, etc.). Derive `GROUPS` y `NOISE_LEVELS` del propio `trials.csv`, así que sirve para ambos mega-experimentos vía `--input`.
- `plot_capacity_comparison.py` — comparación cross-experimento (los 4 grupos capacity + los 5 baseline juntos): ranking, curvas overlay, agregado por p, TP a ruido fijo. Output en `output/mega_exp_capacity/plots/comparison_*.png`.

**Outputs (`hopfield/output/`):**
- `<grupo>/` (5 carpetas: `GRTV`, `JLRX`, `AJKU`, `BDOX`, `HMNW`) — outputs de `run_experiments.py` + `plot_experiments.py` (un grupo por carpeta, con su `README.md`).
- `capacity/` — outputs de `capacity_experiments.py` (carpetas `p2/`, `p3/`, `p5/`, `p6/` con su README global).
- `mega_exp/` — outputs del mega-experimento base (CSVs + plots + 2 READMEs: `README.md` y `README_resultados_plots.md`).
- `mega_exp_capacity/` — outputs del mega-experimento capacity (mismo formato + plots de comparación).

**Otros:**
- `hopfield_word.ipynb` — notebook que renderiza palabras usando las letras 5×5 (actualmente: GRACIAS).
- `Estados espurios.md` — nota teórica sobre estados espurios.
- `simetria/` — análisis matemático de la simetría patrón/complemento (LaTeX + figuras: `complementos.md`, `simetria_complementos.tex`, `simetria_complementos.pdf`, `proyeccion_2d_GR.png`, `interpolacion_1d.png`).

### Material de cátedra y documentación — `docs/`

- `consigna.pdf` — enunciado oficial del TP.
- `resumen-todas-clases-TP4.md` — resumen indexado de las clases con citas del profesor.
- `apuntes_notas_clase.md` — apuntes sueltos.
- `presentacion_PCA_europe.pdf` — slides de la presentación de PCA.
- `clases/` — material original por tema (`aprendizaje-no-supervisado-kohonen/`, `pca-oja/`, `hopfield/`, `presentacion-tp-consigna/`). Cada uno con sus PDFs y transcript `.VTT`.
- `superpowers/` — specs y planes para tareas grandes (formato `YYYY-MM-DD-<topic>.md`):
  - `specs/` — diseños consensuados (lo que vamos a construir).
  - `plans/` — planes paso a paso (cómo lo vamos a construir).

### Otros archivos en la raíz

- `Analisis dataset.md` — análisis exploratorio del `europe.csv`.
- `README.md` — placeholder casi vacío (no usar como referencia).
- `index.html` — HTML standalone que renderiza el material del TP (probablemente para presentación).
- `imagenes/` — capturas de slides referenciadas desde los `.md` con sintaxis Obsidian (`![[Pasted image ...]]`). Cuidar paths si se mueven.
- `requirements.txt` — dependencias mínimas (`pandas`, `numpy`, `matplotlib`, `python-pptx`, `pytest`).
- `.obsidian/` — el repo se edita como vault de Obsidian (en `.gitignore`).

## Comandos comunes

```bash
# PCA: regenerar artefactos (boxplots, biplot, PC1 por país, notas)
cd SIA-PCA && python pca_europe.py
cd SIA-PCA && python generate_pptx.py

# Kohonen: correr el SOM con la config default
cd kohonen && python kohonen.py
# Barrido de k
cd kohonen && python barrido_k.py
# Visualizaciones
cd kohonen && python visualizar.py

# Oja: corrida individual (lee de configs/)
cd oja && python linear_perceptron.py

# Hopfield — demo CLI
cd hopfield && python hopfield.py --group GRTV --query G --noise 0.15

# Hopfield — experimentos canónicos por grupo + plots
PYTHONPATH=hopfield python3 hopfield/run_experiments.py
python3 hopfield/plot_experiments.py

# Hopfield — experimento de capacidad chico
PYTHONPATH=hopfield python3 hopfield/capacity_experiments.py
python3 hopfield/plot_capacity.py

# Hopfield — mega-experimento (5 grupos × 4 letras × 13 niveles × 30 samples)
PYTHONPATH=hopfield python3 hopfield/noise_sweep_experiment.py     # 9 niveles base
PYTHONPATH=hopfield python3 hopfield/extend_noise_experiment.py    # +4 niveles, total 13
python3 hopfield/plot_mega_exp.py

# Hopfield — mega-experimento capacity (4 grupos AL/FUY/GMPVZ/JLRTVX × 13 niveles × 30 samples)
PYTHONPATH=hopfield python3 hopfield/noise_sweep_capacity_experiment.py
python3 hopfield/plot_mega_exp.py --input hopfield/output/mega_exp_capacity
python3 hopfield/plot_capacity_comparison.py

# Tests (solo Hopfield, lo demás no tiene)
python3 -m pytest hopfield/test_noise_sweep.py -v
```

## Idioma y estilo

- El TP, los apuntes y la documentación están en **español**. Responder y comentar en español salvo pedido contrario.
- Los `.md` de análisis siguen un patrón: explican qué se hizo, referencian la slide de origen y citan al profesor cuando corresponde. Mantener ese estilo si se agregan nuevos análisis.
- Para Hopfield específicamente: si un script genera CSVs, hay otro script que los grafica (separación deliberada). El plotter siempre debe poder rehacerse desde los CSVs versionados.

## Pitfalls / cosas a recordar

- Los scripts de `hopfield/` importan unos a otros con paths relativos. **Hay que correrlos con `PYTHONPATH=hopfield`** (o desde dentro de `hopfield/`). Solo los scripts de `plot_*` se pueden correr desde la raíz sin PYTHONPATH (no hacen import cruzado).
- `python` en este sistema apunta a Python 2.7. **Usar `python3`** siempre.
- Cuando extiendas un mega-experimento, no toques `NOISE_LEVELS` en `noise_sweep_experiment.py` — agregá los niveles nuevos en `extend_noise_experiment.py::NEW_NOISE_LEVELS`. `plot_mega_exp.py` deriva los niveles del CSV, no hace falta tocarlo.
