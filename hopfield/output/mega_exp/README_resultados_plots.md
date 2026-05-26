# Mega-experimento — plots y lectura de resultados

Plots generados por `hopfield/plot_mega_exp.py` desde los CSVs descritos
en [`README.md`](README.md). Todos viven en [`plots/`](plots/).

Para regenerarlos:

```bash
python3 hopfield/plot_mega_exp.py
```

Convención de paleta (consistente en todos los plots):

| outcome | color | qué pasó |
| --- | --- | --- |
| **TP** | verde | Recupera el target |
| **FP** | naranja | Cae en otro patrón almacenado |
| **COMPLEMENT** | violeta | Cae en el complemento de algún almacenado |
| **FN** | gris | Estable, espurio no-clasificable |
| **CICLO** | azul | No converge a punto fijo |

---

## 1. Comparación entre grupos

### Curvas tasa_TP vs ruido — [`tp_curves_by_group.png`](plots/tp_curves_by_group.png)

![](plots/tp_curves_by_group.png)

Las 5 curvas comparten la misma forma sigmoidea decreciente, pero el
**ranking se mantiene en todo el rango**: `JLRX` y `GRTV` (los grupos de
menor `|⟨,⟩| medio`) dominan a `BDOX` y `HMNW` (los grupos elegidos como
"malos") para cualquier nivel de ruido. La separación es máxima cerca de
ruido = 0.30, donde los grupos buenos están en ~70% TP y los malos en
~25%. A partir de ruido = 0.55 todos colapsan a casi 0%.

**Lectura clave para la presentación**: la ortogonalidad de los patrones
no solo desplaza la curva — la hace cuantitativamente mejor en *todo* el
régimen útil. La diferencia entre `JLRX` y `HMNW` a ruido 0.30 es de
~40 puntos porcentuales.

### Heatmap tasa_TP — [`heatmap_tp.png`](plots/heatmap_tp.png)

![](plots/heatmap_tp.png)

Misma información que las curvas pero en formato matricial con valores
anotados. Útil para citar números puntuales (`HMNW @ 0.30 = 0.18`,
`JLRX @ 0.20 = 0.93`).

### Heatmap tasa_COMPLEMENT — [`heatmap_complement.png`](plots/heatmap_complement.png)

![](plots/heatmap_complement.png)

El "espejo" del heatmap de TP: a medida que TP cae, COMPLEMENT crece.
Los grupos malos (`BDOX`, `HMNW`) tienen tasas de COMPLEMENT muy altas
incluso a ruido moderado (0.30-0.40), mientras que los grupos buenos
"resisten" la atracción al antipodal por más tiempo.

---

## 2. Distribución completa de outcomes

### Global — [`outcomes_stacked_global.png`](plots/outcomes_stacked_global.png)

![](plots/outcomes_stacked_global.png)

Barras apiladas con las 5 categorías para cada nivel de ruido,
agregando todos los grupos. A ruido bajo dominan TP y FP; el FP indica
que la red **sí está convergiendo a un patrón almacenado**, solo que no
es el target — un fallo "menos malo" que el espurio. A ruido alto
domina COMPLEMENT, no FN: la red sigue convergiendo a algo que se
parece estructuralmente a un almacenado (su antipodal), no a basura
total.

### Por grupo — [`outcomes_stacked_by_group.png`](plots/outcomes_stacked_by_group.png)

![](plots/outcomes_stacked_by_group.png)

Mismas barras apiladas pero descompuestas por grupo. Se ve claramente
que:

- `JLRX` casi nunca produce FP (los patrones son distinguibles).
- `HMNW` y `BDOX` empiezan a tener FP desde ruido bajo.
- `AJKU` es un caso interesante: relativamente pocos FP pero muchos FN
  (espurios mixtos) — sus patrones son distintos pero el paisaje de
  energía es rugoso.

---

## 3. Por grupo: outcomes por letra

Cada grupo tiene su propio plot mostrando las 4 letras almacenadas como
columnas, cada una con su barra apilada por ruido. Permite ver
**asimetrías dentro del grupo** — si una letra particular es más fácil
o más difícil de recuperar.

| grupo | plot |
| --- | --- |
| GRTV | [`GRTV_outcomes_by_letter.png`](plots/GRTV_outcomes_by_letter.png) |
| JLRX | [`JLRX_outcomes_by_letter.png`](plots/JLRX_outcomes_by_letter.png) |
| AJKU | [`AJKU_outcomes_by_letter.png`](plots/AJKU_outcomes_by_letter.png) |
| BDOX | [`BDOX_outcomes_by_letter.png`](plots/BDOX_outcomes_by_letter.png) |
| HMNW | [`HMNW_outcomes_by_letter.png`](plots/HMNW_outcomes_by_letter.png) |

Ej. en `HMNW` la letra `N` se recupera bastante mejor que `M`/`W`,
porque `N` es la que tiene producto interno más bajo con las otras tres.

---

## 4. Grillas de overlays input/output

Una imagen por grupo con las 4 letras × 9 niveles de ruido del trial
**representante** (sample_idx=0). Cada celda muestra el overlay del
input con el output:

- **Verde claro** = pixel `+1` en input y output (acierto en pixel encendido).
- **Blanco** = pixel `-1` en input y output (acierto en pixel apagado).
- **Rojo** = mismatch — la red flippeó ese pixel respecto al input.

Bajo cada celda se anota el outcome resultante (`TP`, `FP`, etc.) y el
patrón al que convergió (cuando aplica).

| grupo | plot |
| --- | --- |
| GRTV | [`GRTV_overlay_grid.png`](plots/GRTV_overlay_grid.png) |
| JLRX | [`JLRX_overlay_grid.png`](plots/JLRX_overlay_grid.png) |
| AJKU | [`AJKU_overlay_grid.png`](plots/AJKU_overlay_grid.png) |
| BDOX | [`BDOX_overlay_grid.png`](plots/BDOX_overlay_grid.png) |
| HMNW | [`HMNW_overlay_grid.png`](plots/HMNW_overlay_grid.png) |

**Atención**: estos son los representantes (un solo sample por config),
no la mayoría estadística. Sirven para *ilustrar* cómo se ve un trial
particular pero no son representativos del grupo en sentido estadístico
— para eso ver las distribuciones de outcomes de la sección anterior.

### Outcome de los 180 representantes

| grupo | TP | FP | COMPLEMENT | FN | CICLO |
| --- | ---: | ---: | ---: | ---: | ---: |
| AJKU | 12 | 0  | 6  | 16 | 2 |
| BDOX | 7  | 10 | 13 | 0  | 6 |
| GRTV | 10 | 9  | 12 | 2  | 3 |
| HMNW | 5  | 13 | 18 | 0  | 0 |
| JLRX | 15 | 0  | 12 | 4  | 5 |

---

## 5. Trayectorias de energía

[`energy_longest_per_group.png`](plots/energy_longest_per_group.png) —
para cada grupo elegí el representante que **más iteraciones tardó** en
estabilizarse, y grafico su `H(S)` vs iteración.

![](plots/energy_longest_per_group.png)

Sirve como ejemplo concreto del comportamiento "energía siempre
decrece" (en realidad: nunca crece) de Hopfield. Las curvas son
monótonas no-crecientes, llegando al mínimo local correspondiente al
atractor donde la red se asentó.

---

## Resumen: qué plots usar en la presentación

Priorizando por valor expositivo:

1. **`tp_curves_by_group.png`** — el plot money: muestra que la elección de
   grupo importa y que el ruido degrada gradualmente.
2. **`outcomes_stacked_by_group.png`** — narra la historia completa:
   por qué falla la red, no solo cuánto falla.
3. **Un `<grupo>_overlay_grid.png`** del peor grupo (`HMNW`) — visual,
   muestra el "flip al complemento" emergiendo a ruido alto.
4. **`heatmap_tp.png`** si necesitás citar números puntuales.
5. **`energy_longest_per_group.png`** si querés mostrar la propiedad de
   energía decreciente.

Los `<grupo>_outcomes_by_letter.png` son útiles si querés profundizar en
asimetrías intra-grupo durante el Q&A.
