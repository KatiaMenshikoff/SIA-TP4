# Explicación — `ddof=1`, matriz de correlación y criterio de divergencia

Dos preguntas técnicas que aparecieron al alinear el script de Oja con el
entregable de PCA (`SIA-PCA/pca_europe.py`):

1. ¿Qué es **`ddof`** y por qué cambiarlo de 0 a 1 cambia el autovalor?
2. ¿Cómo decidimos cuándo una corrida **divergió**? ¿De dónde sale la cota
   teórica $\eta_0 < 1/(1{,}2\,\lambda_1)$ del slide 14?

---

## 1. Qué es `ddof` y por qué importa

### Definición

`ddof` = *delta degrees of freedom* = corrección al divisor de la varianza.

| `ddof` | Fórmula de la varianza                                  | Nombre                                       | Cuándo se usa                                                     |
| ------ | ------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| `0`    | $\sigma^2 = \dfrac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^2$ | Varianza **poblacional**                     | Cuando los datos son la población completa.                       |
| `1`    | $s^2 = \dfrac{1}{n-1}\sum_{i=1}^n (x_i - \bar{x})^2$    | Varianza **muestral** (corrección de Bessel) | Cuando los datos son una **muestra** de una población más grande. |

Las dos convenciones difieren por un factor $n/(n-1)$. Con `europe.csv`
($n=28$): el factor es $28/27 \approx 1{,}0370$ (~3.7% de diferencia).

### Dónde aparece en este proyecto

| Archivo | Llamada | `ddof` |
|---|---|---|
| `SIA-PCA/pca_europe.py:28` | `X.std()` de pandas | **`ddof=1`** (default de pandas) |
| `SIA-PCA/pca_europe.py:73` | `X.corr()` de pandas | usa $n-1$ internamente |
| `kohonen/kohonen.py:28` | `X.std(axis=0, ddof=0)` | **`ddof=0`** (poblacional) |
| `oja/linear_perceptron.py::standardize` | `np.std(axis=0, ddof=1)` | **`ddof=1`** ← *cambiado* |

### Por qué el script de Oja ahora usa `ddof=1`

**Antes** (ddof=0, copiado de `kohonen.py`):
- $\lambda_{\max}$ que reportaba el script: **3.3467**
- $\lambda_{\max}$ de `SIA-PCA/Notas/autovalores_autovectores.md`: **3.2272**
- No coincidían (diferían exactamente por el factor $28/27$).

**Ahora** (ddof=1, matcheando SIA-PCA):
- $\lambda_{\max}$ del script de Oja: **3.227166**
- $\lambda_{\max}$ de SIA-PCA: **3.2272**
- ✅ Coinciden.

### Por qué los autovectores **no** se ven afectados

La matriz de correlación que sale con ddof=1 es la misma que con ddof=0
**multiplicada por un escalar** ($n/(n-1)$). Y los autovectores de
$\alpha \cdot C$ son los mismos que los de $C$ — solo cambian los autovalores
(se multiplican también por $\alpha$). Por eso los autovectores siempre
coincidieron entre el script de Oja y SIA-PCA, incluso antes del cambio.

### Trade-off del cambio

| Pro | Con |
|---|---|
| $\lambda_{\max}$ del script de Oja **coincide exacto** con SIA-PCA. | Ya no usa la misma `standardize()` que `kohonen.py` (que está en ddof=0). |
| El `pc1_per_sample.csv` del script da los mismos Y₁ que `SIA-PCA/Notas/autovalores_autovectores.md` hasta el 5to decimal. | Hay que recordar que kohonen y oja estandarizan con divisor distinto. |
| La cota teórica $\eta_0 < 1/(1{,}2\,\lambda_1)$ se aplica al $\lambda_1$ correcto (el del entregable PCA). | — |

Decisión: prevalece el match con SIA-PCA (es el entregable de comparación
que pide la consigna).

---

## 2. Cómo decidimos que una corrida divergió

### En el código

El script usa estos chequeos para detectar divergencia, en orden de
severidad:

1. **Overflow numérico** — la línea
   ```python
   w = w + eta * y * (x_mu - y * w)
   ```
   levanta `RuntimeWarning: overflow encountered in multiply` cuando $w$
   crece tanto que $y^2 w$ supera el rango de `float64`. A partir de ahí
   $w$ se vuelve `inf` y un paso después `NaN`.

2. **`‖w_final‖` = NaN** — chequeo final reportado por pantalla. Si la
   norma es `NaN`, el algoritmo no converge.

3. **`cos(w_final, v_PCA)` = NaN** — corolario del anterior.

### Cómo se eligió $\eta_0$ en este TP (relato empírico)

La razón de existir de Oja es **evitar tener que calcular PCA**. Si ya
conociéramos $\lambda_1$ (= calculamos el PCA completo), no tendría
sentido correr Oja. La propia profe lo dice (slide 14):

> *"como no conocemos el autovalor es mejor estandarizar todas las
> variables de entradas y comenzar con $\eta_0 \le 0{,}5$."*

Y agrega verbalmente *"un poco menos recomendaría, pero pruébenlo"*. O
sea, la cátedra propone una **heurística empírica**: estandarizar y
arrancar con 0.5 (o algo menor), después ajustar a ojo.

Eso es lo que hicimos. Con `random_seed = 42`:

| $\eta_0$ | Comportamiento real | ¿Acción? |
|---:|---|---|
| 0.50 | diverge → NaN (overflow en época 0) | bajar |
| 0.30 | diverge → NaN | bajar más |
| 0.25 | diverge → NaN | bajar más |
| **0.20** | **converge**, cos = 0.999999 | ✅ aceptamos |
| 0.15 | converge, cos = −0.999999 | (autovector opuesto, válido) |
| 0.10 | converge, cos = 1.000000 | muy estable, pero más lento |

Resultado: $\eta_0 = 0{,}2$ es el **valor más grande del rango probado
que no rompe el algoritmo** con este seed.

### La cota teórica (slide 14): solo como verificación a posteriori

Como contexto, el slide 14 da también una cota *teórica*:

$$\boxed{\eta_0 < \dfrac{1}{1{,}2\,\lambda_1}}$$

(Linealizando $E[\Delta w] = \eta(Cw - (w^\top Cw)w)$ alrededor del
autovector dominante, el sistema dinámico tiene autovalores
$\propto 1 - \eta\,\lambda_1$, y para estabilidad numérica se necesita
$\eta \lambda_1$ chico. El 1.2 es margen empírico de cátedra.)

**Acá no la usamos para decidir** (no conocíamos $\lambda_1$ cuando
elegimos $\eta_0$). Pero una vez que el algoritmo convergió, podemos
verificarla *a posteriori*:

$$\lambda_{\max} = 3.2272 \quad\Rightarrow\quad \eta_0^{\text{cota}} = \frac{1}{1{,}2 \cdot 3{,}2272} \approx 0{,}258$$

Y efectivamente la frontera empírica (entre 0.25 que diverge y 0.20 que
converge) cae justo donde la cota teórica predice. La teoría "explica"
los resultados, pero no los **guió**.

### Por qué $\eta_0 = 0{,}5$ del slide igual rompe

El propio slide 14 dice $\eta_0 \le 0{,}5$, no $\eta_0 = 0{,}5$. La profe
remata: *"un poco menos recomendaría"*. El 0.5 es **el techo donde puede
romperse**, no un valor seguro — y para `europe.csv` rompe directamente.
Esto es lo que motiva el "pruébenlo" verbal: depende del dataset y del
seed.

### Configs actuales

| Config | $\eta$ | Rol pedagógico |
|---|---|---|
| `oja_var_eta05` | variable, $\eta_0 = 0{,}5$ (`1/t`) | **diverge** — ilustra el límite |
| `oja_var_eta02` | variable, $\eta_0 = 0{,}2$ (`1/t`) | converge limpio (cos ≈ 1) |
| `oja_fix_1e-3` | fijo, $\eta = 10^{-3}$ | converge, dispara $\varepsilon$ |

---

## TL;DR

- **`ddof`** es el divisor de la varianza ($n$ o $n-1$). Cambiarlo escala
  la matriz de correlación por un factor $n/(n-1)$ y, por tanto, escala
  los autovalores. **No afecta a los autovectores**.
- El script ahora usa `ddof=1` para que $\lambda_{\max}$ y los $Y_1$ por
  país coincidan exactamente con `SIA-PCA/Notas/autovalores_autovectores.md`.
- **Divergencia** = el script reporta `‖w_final‖ = NaN` y `cos = NaN`. Bajo
  el capó es un overflow en `float64` por la fórmula $-\eta y^2 w$ cuando
  $\|w\|$ explota.
- **No usamos la cota teórica** $\eta_0 < 1/(1{,}2\,\lambda_1)$ del slide
  14 para decidir $\eta_0$ — eso requeriría conocer $\lambda_1$, y si
  ya lo conociéramos no necesitaríamos Oja. La elección es **empírica**:
  arrancamos en 0.5, vimos divergencia, fuimos bajando hasta 0.2.
  La cota sirve a posteriori como **verificación** ($\approx 0{,}258$
  para `europe.csv`): predice exactamente la frontera empírica observada.
