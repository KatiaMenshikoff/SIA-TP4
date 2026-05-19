# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## NO PONER CLAUDE COAUTOR

Nunca agregar `Co-Authored-By: Claude` (ni ninguna variante) en los mensajes de commit. Los commits van **sin** trailer de co-autoría.

## Contexto del repo

Trabajo práctico **SIA-TP4 — Aprendizaje No Supervisado** (Sistemas de Inteligencia Artificial, 2026). Cuatro técnicas: **Kohonen (SOM)**, **PCA con librería**, **Regla de Oja a mano** y **Hopfield** (entrega posterior). Dataset principal: `SIA-PCA/europe.csv` (28 países × 7 variables: `Country, Area, GDP, Inflation, Life.expect, Military, Pop.growth, Unemployment`).

## Regla principal: no usar técnicas que no se vieron en clase

Lo único que me importa es que no metas métodos, fórmulas o trucos que no estén en el material de cátedra. Si una idea no aparece ahí, avisame antes de usarla. Para chequear qué se vio:

- `docs/resumen-todas-clases-TP4.md` — resumen indexado de las tres clases con citas del profesor. Suele alcanzar como referencia rápida.
- `docs/clases/aprendizaje-no-supervisado-kohonen/` — PDFs de la clase de Kohonen y transcript `kohonen.VTT`.
- `docs/clases/pca-oja/` — PDFs *Autovalores y Autovectores*, *PCA*, *Regla de Oja y Sanger* y transcript `pca_oja.VTT`.
- `docs/clases/presentacion-tp-consigna/presentacion_consigna.VTT` — transcript de la clase donde se presentó el TP.
- `docs/consigna.pdf` — enunciado oficial.
- `docs/apuntes_notas_clase.md` — apuntes sueltos míos (biplot, Oja, learning rates).

Más allá de eso, hay un puñado de cosas que el profesor remarcó y conviene tener presentes:

- **Estandarizar las entradas** (z-score) en Kohonen, PCA y Oja — `europe.csv` mezcla `Area` (~10⁵) con `Pop.growth` (~0.1).
- **PCA solo tiene sentido si hay correlación** entre las variables.
- **Oja converge al autovector de PC1, no a PC1**. La componente se arma después como combinación lineal con `a_i = w_i^final`.
- Comparando Oja vs PCA-librería, el autovector puede salir con **signo opuesto** y sigue siendo válido.
- Para Kohonen el profesor pide análisis variando `k`, radio `R`, tipo de grilla e inicialización, y reportar heatmap, matriz U y activación por variable.
- PCA va con librería; **Oja se implementa a mano**.

## Estructura

- `SIA-PCA/` — ejercicio PCA ya implementado. `pca_europe.py` es el script de cátedra-por-cátedra (sigue los 7 pasos de la slide 32). Genera `boxplot_*.png`, `pc1_por_pais.png` (slide 46), `biplot.png` (slide 45) y vuelca tablas a `Notas/matriz_correlaciones.md` y `Notas/autovalores_autovectores.md`. `Notas/analisis.md` es el documento de interpretación que acompaña la entrega.
- `kohonen/` — work-in-progress; sólo `kohonen.md` con la consigna y apuntes. La implementación todavía no existe.
- `docs/` — material de cátedra (ver sección anterior).
- `imagenes/` — capturas de slides referenciadas desde los `.md` con sintaxis Obsidian (`![[Pasted image ...]]`). Cuidar paths si se mueven.
- `.obsidian/` — el repo se edita como vault de Obsidian (ya en `.gitignore`).

## Comandos comunes

```bash
# PCA: regenerar todos los artefactos (boxplots, biplot, PC1 por país, notas)
cd SIA-PCA && python pca_europe.py

# Regenerar la presentación pptx del seguimiento de pasos
cd SIA-PCA && python generate_pptx.py
```

No hay test suite, ni lint configurado, ni build. Dependencias usadas hasta ahora: `pandas`, `numpy`, `matplotlib`, `python-pptx`. Instalarlas a demanda (no hay `requirements.txt`).

## Idioma y estilo

- El TP, los apuntes y la documentación están en **español**. Responder y comentar en español salvo pedido contrario.
- Los `.md` de análisis siguen un patrón: explican qué se hizo, referencian la slide de origen y citan al profesor cuando corresponde. Mantener ese estilo si se agregan nuevos análisis.
