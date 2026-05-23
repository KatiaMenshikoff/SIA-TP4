# Explicación — Métricas de validación y por qué `‖w‖ → 1`

Dos preguntas que aparecieron al revisar la validación del script de Oja:

1. ¿Qué miden exactamente el **coseno** y la **diff por componente** que
   se reportan en cada corrida? ¿Cercanía entre qué cosas?
2. ¿Por qué la regla de Oja garantiza que **`‖w‖ → 1`**? ¿Qué dijo la
   profe en clase y qué es razonamiento propio?

---

## 1. Coseno + diff por componente: cercanía entre qué

Estamos comparando **dos vectores en $\mathbb{R}^7$** (7 features de
`europe.csv`: `Area`, `GDP`, `Inflation`, `Life.expect`, `Military`,
`Pop.growth`, `Unemployment`):

- $w_{\text{final}}$ → el vector de pesos al que llegó **Oja** después
  de entrenar.
- $v_{\text{PCA}}$ → el **autovector** asociado al mayor autovalor de la
  matriz de correlación, calculado con `numpy.linalg.eigh`.

Si Oja funciona como dice la teoría, estos dos vectores tienen que ser
**el mismo** (o el opuesto en signo — admisible según la profe, transcript
L1445 y L223 del resumen: *"tiene que dar lo mismo o el autovector opuesto"*).

### Coseno (mide solo dirección)

$$\cos(w, v) = \frac{w \cdot v}{\|w\| \cdot \|v\|} = \frac{\sum_i w_i\, v_i}{\|w\|\,\|v\|}$$

Vale entre $-1$ y $+1$:

| Valor               | Interpretación                                   |
| ------------------- | ------------------------------------------------ |
| $+1$                | Vectores **paralelos** (idénticos en dirección). |
| $-1$                | **Opuestos** (signo invertido; admisible).       |
| $0$                 | **Perpendiculares** (caso peor, no convergió).   |
| $\|\cos\|\approx 1$ | Lo que queremos.                                 |

En la corrida `oja_var_eta02`: $\cos = 0{,}999999$ → casi colineales
perfectos.

**Ventaja**: ignora la magnitud, solo mira si los vectores "apuntan en la
misma dirección" — y para Oja eso es lo que importa, porque el autovector
es una **dirección**, no una longitud específica.

### Diff por componente

$$\text{diff}_i = w_i^{\text{oja}} - v_i^{\text{PCA}} \quad \text{para cada } i = 1 \dots 7$$

Es literalmente restar par a par. Ejemplo de la corrida `oja_var_eta02`:

| feature      | $w_{\text{oja}}$ | $v_{\text{PCA}}$ | diff           |
| ------------ | ---------------: | ---------------: | -------------: |
| Area         |        −0.125629 |        −0.124874 | **−0.000755** |
| GDP          |        +0.500433 |        +0.500506 |     −0.000073 |
| Inflation    |        −0.407256 |        −0.406518 | **−0.000738** |
| Life.expect  |        +0.483027 |        +0.482873 |     +0.000154 |
| Military     |        −0.187477 |        −0.188112 |     +0.000634 |
| Pop.growth   |        +0.475544 |        +0.475704 |     −0.000160 |
| Unemployment |        −0.271282 |        −0.271656 |     +0.000374 |

**Ventaja sobre el coseno**: te dice **qué componente se aproximó peor**
(acá las peores son `Area` e `Inflation`, con ~$10^{-4}$ de error). El
coseno te da un solo número global; la diff por componente te da el
**perfil del error**.

**Desventaja**: depende también de la norma — si $\|w_{\text{oja}}\| = 1{,}01$
y $\|v_{\text{PCA}}\| = 1{,}00$ pero apuntan exactamente igual, la diff no
va a ser cero aunque la dirección sea idéntica. Por eso en el script
**primero se alinean los signos** antes de restar (para no confundir
"vector opuesto válido" con "error grande").

### Resumen

| Métrica | Qué responde |
|---|---|
| $\cos(w, v_{\text{PCA}})$ | "¿Coincide la **dirección**?" — un número global. |
| diff por componente | "¿En qué **variable** está el error más grande?" — desglose. |
| $\|w_{\text{final}}\|$ | "¿La **magnitud** quedó donde la teoría dice?" — chequeo de salud. |

Las tres juntas confirman que el algoritmo convergió al lugar correcto.

---

## 2. Por qué `‖w‖ → 1`

### Lo que dijo la profe (literal)

En clase **no dio la demostración**. Solo dijo (transcript `pca_oja.VTT` L2305):
> *"lo que demuestra Oja es que simplemente se puede actualizar de esta
> forma y ya está, y no diverge. Fíjense que **acá está restando**.
> Entonces, en este caso no va a haber overflow, que es lo que pasaba antes."*

Y en el slide 12 figura la propiedad, sin justificarla:
> *"|w| se mantiene acotado. Tiende a 1"*

Mencionó también (L2309) que Oja lo deriva *"por estimarlo con polinomio
de Taylor"* — pero no hizo la cuenta en clase.

> ⚠️ **Lo de abajo es razonamiento propio**, no de cátedra. Lo incluyo
> porque ayuda a entender el "por qué".

### La intuición (dos términos compitiendo)

Mirando la regla:

$$\Delta w = \eta \cdot y \cdot (x - y \cdot w), \qquad y = w \cdot x$$

Se ven dos términos compitiendo:

| Término | Efecto sobre $\|w\|$ |
|---|---|
| $+\eta \cdot y \cdot x$ (Hebbiano puro) | Empuja $w$ en la dirección de $x$, **hace crecer** $\|w\|$. Crece linealmente con $\|w\|$ (porque $y = w \cdot x$). |
| $-\eta \cdot y^2 \cdot w$ (corrección de Oja, viene del Taylor) | Empuja $w$ **en contra de sí mismo**, lo **encoge**. Crece como $y^2$, o sea como $\|w\|^2$. |

Comparación de magnitudes:

- Si $\|w\|$ es **chica** → $y$ chico → $y^2$ es **mucho** más chico que $y$ → **domina el Hebbiano** → $\|w\|$ crece.
- Si $\|w\|$ es **grande** → $y$ grande → $y^2$ es **enorme** → **domina la corrección** → $\|w\|$ se achica.

El equilibrio (los dos se cancelan) ocurre exactamente cuando $\|w\| = 1$.
**Esa es la razón intuitiva del slide 12.**

### La cuenta formal (extra, no estrictamente necesaria)

En equilibrio, $E[\Delta w] = 0$ tomando esperanza sobre los datos $x$. Con
$C = E[xx^\top]$ (la matriz de correlación, porque $x$ está estandarizado):

$$E[\Delta w] = \eta \big( C w - (w^\top C w)\,w \big) = 0$$

$$\Rightarrow C w = (w^\top C w)\, w$$

Eso es la **definición de autovector**: $w$ es autovector de $C$ con
autovalor $\lambda = w^\top C w$.

Ahora, si escribimos $w = \alpha \cdot v$ con $v$ un autovector **unitario**
de $C$ (autovalor $\lambda_v$):

- $C w = \alpha \lambda_v v$
- $w^\top C w = \alpha^2 \lambda_v$
- La condición $C w = (w^\top C w) w$ queda:
  $$\alpha \lambda_v v = \alpha^2 \lambda_v \cdot \alpha v = \alpha^3 \lambda_v v$$
- $\Rightarrow \alpha = \alpha^3 \Rightarrow \alpha^2 = 1 \Rightarrow \alpha = \pm 1$

Por lo tanto $\|w\| = |\alpha| \cdot \|v\| = 1 \cdot 1 = \boxed{1}$.

**Nota lateral**: la solución $\alpha = -1$ es la que justifica que Oja
pueda converger al autovector **opuesto** y siga siendo válido (es el
mismo punto fijo del sistema dinámico, con signo invertido).

---

## TL;DR

- El **coseno** mide si $w_{\text{oja}}$ apunta en la misma dirección que
  el autovector PC1 calculado por la librería. La **diff por componente**
  desglosa el error por variable. La norma `‖w‖` chequea que la magnitud
  haya llegado donde la teoría dice.
- La profe dijo *"tiende a 1, no diverge porque está restando"* y mostró
  que se sigue de Taylor — la justificación formal no la hizo en clase.
  La intuición útil es: los dos términos de la regla (Hebbiano y
  corrección) compiten y solo se cancelan exactamente en $\|w\| = 1$.
