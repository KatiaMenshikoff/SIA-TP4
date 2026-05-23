# Oja — Notas de implementación

Implementación del perceptrón de Oja para obtener PC1 sobre `europe.csv`
(28 países × 7 variables: `Area`, `GDP`, `Inflation`, `Life.expect`,
`Military`, `Pop.growth`, `Unemployment`). Script: `linear_perceptron.py`.

---

## 1. Decisiones que vienen directo de cátedra

Todo lo de abajo está en los slides (PDF *Regla de Oja y Sanger*, slides
7–16) o explícito en el transcript `docs/clases/pca-oja/pca_oja.VTT`.

| Decisión                    | Valor                                                                                                            | Fuente                                                                                                                                   |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Estandarización de entradas | z-score por columna                                                                                              | Slide 14: *"estandarizar todas las variables de entrada"* — y la profe lo repite varias veces.                                           |
| Arquitectura                | Perceptrón simple, **una capa de salida**, **activación lineal** ($y = w^\top x$, sin $\theta$)                  | Slide 7 (definición), slide 15 (*"Es un perceptrón simple con una capa de salida"*), transcript L2301: *"un perceptrón simple, lineal"*. |
| Bias                        | **Sin bias**                                                                                                     | Las entradas tienen media 0 después de la estandarización, así que no hace falta — y el pseudocódigo del slide 16 no lo incluye.         |
| Inicialización de pesos     | $w \sim \text{Uniforme}[0, 1]^n$                                                                                 | Slide 15: *"Distribución uniforme entre 0 y 1"*.                                                                                         |
| Modo de actualización       | **Online** (una actualización por muestra)                                                                       | Slide 16: el `+=` ocurre **dentro** del `for i=1..N` de muestras.                                                                        |
| Regla de Oja (post-Taylor)  | $\Delta w = \eta \cdot y \cdot (x - y \cdot w)$                                                                  | Slide 12 (forma final) y slide 16 (pseudocódigo).                                                                                        |
| Salida del entrenamiento    | $w_{\text{final}} \approx$ autovector de PC1; PC1 = $\sum_i w_i^{\text{final}} \cdot x_i$ con $x$ estandarizadas | Slide 12 y transcript L2385.                                                                                                             |

Notar la clave de implementación que repite la profe (transcript L2301):
> *"básicamente ya tienen el código del perceptrón simple lineal. Lo único que hay que hacer es cambiar cómo se actualizan los pesos."*

---

## 2. Learning rate (sí está en cátedra)

### Cota teórica (slide 14)
$$\eta_0 = \frac{1}{1{,}2\,\lambda_1}$$

Como $\lambda_1$ no se conoce a priori, el slide recomienda **estandarizar las
entradas y arrancar con $\eta_0 \le 0{,}5$**. La profe añadió verbalmente
(transcript L2345): *"un poco menos recomendaría, pero pruébenlo."*

### Esquemas propuestos por cátedra (slide 15)
- **Variable**: $\eta(0) = 0{,}5$ decreciente a lo largo de las épocas.
- **Fijo chico**: $\eta = 10^{-3}$.

### Implementado
El script soporta los dos modos vía `config.json`:

```json
"learning_rate": {"mode": "fixed", "value": 0.001}
```
```json
"learning_rate": {"mode": "variable", "eta_0": 0.5, "schedule": "1/t"}
```

Schedules disponibles: `"1/t"` ($\eta_0 / (1+\text{epoch})$),
`"1/sqrt_t"` ($\eta_0 / \sqrt{1+\text{epoch}}$) y `"constant"`.

> Nota: el slide dice "0.5 decreciente a lo largo de las épocas" sin
> especificar la fórmula del decay. Elegimos $\eta_0/(1+t)$ porque es el
> decay más estándar para regla de Robbins–Monro. **Esto es decisión propia
> (la fórmula concreta del decay, no la idea de que sea decreciente).**

---

## 3. Criterio de corte (⚠️ decisión propia, no viene de cátedra)

**En clase no se definió ningún criterio de parada.** La profe sólo dijo
(transcript L2269, L2325):
> *"después de varias iteraciones, el método va a converger al autovector
> correspondiente al mayor autovalor."*

Y el pseudocódigo del slide 16 simplemente corre `for epoch in #epochs`
y devuelve $w$ — épocas fijas, sin stop condition.

### Lo que se implementó
Criterio sobre la norma del cambio de pesos entre épocas:
$$\| w_{\text{epoch}+1} - w_{\text{epoch}} \| < \varepsilon$$
con $\varepsilon$ configurable (default $10^{-8}$), tope de `epochs`.

### Por qué se eligió este
- Es la métrica más simple de implementar.
- Se condice directamente con la idea de "se estabilizó".
- Permite parar antes en runs largos (p. ej. $\eta = 10^{-3}$ paró en época 280).

### Caveat importante
Con $\eta$ **fijo**, $\|\Delta w\|$ **no decae a 0** sino a un piso de
"ruido residual" proporcional a $\eta$ (cada muestra empuja un poco a $w$
aunque ya esté en la dirección correcta). El umbral $\varepsilon$ tiene
que ser razonable respecto de ese piso. Con $\eta$ variable ($1/t$), sí
$\|\Delta w\| \to 0$ porque el propio $\eta$ se achica.

---

## 4. Estructura del código

```
oja/
├── linear_perceptron.py        # entry point
├── configs/
│   ├── oja_var_eta05.json      # η₀ = 0.5 variable
│   ├── oja_var_eta02.json      # η₀ = 0.2 variable
│   └── oja_fix_1e-3.json       # η = 10⁻³ fijo
└── output/<model>_<timestamp>/
    ├── config.json              # copia del config (reproducibilidad)
    ├── convergence.csv          # epoch, eta, ‖w‖, ‖Δw‖
    ├── weights_history.csv      # w por época (init + 1..N)
    ├── final_weights.csv        # w_oja vs autovector PCA-lib (signo alineado)
    └── pc1_per_sample.csv       # PC1 = w · x  por país, vs PCA-lib
```

### Estandarización
Z-score con `ddof=1` (varianza muestral, divisor $n-1$), para que la
matriz de correlación y $\lambda_{\max}$ coincidan exactamente con los
de `SIA-PCA/pca_europe.py`. Detalle en `explicacion_ddof_y_divergencia.md`.

```python
def standardize(X):
    return (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
```

Esto difiere de `kohonen/kohonen.py:28` (que usa `ddof=0`); es una
decisión consciente para alinear el script de Oja con el entregable PCA.

### Núcleo del entrenamiento
```python
w = rng.uniform(0.0, 1.0, size=n)                    # Slide 15
for epoch in range(epochs):
    w_before = w.copy()
    eta = eta_fn(epoch)
    for mu in range(M):                              # online
        x_mu = X[mu]
        y = float(w @ x_mu)                          # escalar, una vez por muestra
        w = w + eta * y * (x_mu - y * w)             # actualización vectorial
    if np.linalg.norm(w - w_before) < epsilon:
        break
```

### Validación
El script calcula además el autovector de PC1 vía `numpy.linalg.eigh` sobre
la matriz de correlaciones $X^\top X / (M-1)$ y reporta:
- $\|w_{\text{final}}\|$ (esperado $\approx 1$).
- $\cos(w_{\text{final}}, v_{\text{PCA}})$ (esperado $|\cdot| \approx 1$).
- Diff por componente entre $w_{\text{oja}}$ y $v_{\text{PCA}}$.

Los signos se alinean antes de comparar (Oja puede converger al autovector
opuesto y sigue siendo válido, como advierte la profe en transcript L1445).

---

## 5. Ejecuciones

### Cómo se llegó a estos $\eta_0$ (relato empírico)

La cátedra dice (slide 14):
> *"como no conocemos el autovalor es mejor estandarizar todas las
> variables de entradas y comenzar con $\eta_0 \le 0{,}5$."*

Y la profe verbalmente *"un poco menos recomendaría, pero pruébenlo"*.
**No conocemos $\lambda_1$ a priori** (en la vida real no calcularíamos
PCA para después correr Oja — eso anula el sentido del algoritmo), así
que la elección se hace por **prueba y error**:

1. **Arrancamos con $\eta_0 = 0{,}5$** (el techo del slide). Resultado:
   `RuntimeWarning: overflow encountered in multiply` en la primera
   época, $\|w\|$ → NaN. **Diverge.**
2. **Bajamos a $\eta_0 = 0{,}3$**. Otra vez NaN.
3. **$\eta_0 = 0{,}25$**. Sigue divergiendo.
4. **$\eta_0 = 0{,}2$**. ✅ Converge a una dirección estable, $\|w\| \approx 1$.
5. (Validación adicional probada y descartada por ser redundante: 0.15,
   0.1 también convergen).

Entonces $\eta_0 = 0{,}2$ es el valor más grande del rango probado que
**no diverge** con el seed elegido. Para el η fijo seguimos la sugerencia
literal del slide 15 ($10^{-3}$).

> *Nota a posteriori*: una vez convergido el algoritmo, sí podemos
> mirar el $\lambda_1$ que sale del PCA-librería ($\lambda_1 \approx 3{,}23$)
> y verificar que coincide con la cota del slide:
> $1/(1{,}2 \cdot 3{,}23) \approx 0{,}258$, justo entre 0.25 (diverge) y
> 0.2 (converge). La cota teórica funciona, pero **no la usamos para
> decidir** $\eta_0$ — solo para entender por qué la frontera empírica
> estaba donde estaba. Detalle en `explicacion_ddof_y_divergencia.md`.

### Las tres corridas finales

| Config          | Modo             | η inicial | Epochs máx | ε    |
| --------------- | ---------------- | --------- | ---------- | ---- |
| `oja_var_eta05` | variable (`1/t`) | 0.5       | 2000       | 10⁻⁸ |
| `oja_var_eta02` | variable (`1/t`) | 0.2       | 2000       | 10⁻⁸ |
| `oja_fix_1e-3`  | fijo             | 10⁻³      | 2000       | 10⁻⁸ |

Se deja la corrida divergente $\eta_0 = 0{,}5$ como evidencia del proceso
de búsqueda (no se "esconde" la divergencia: forma parte del relato).
Semilla: `random_seed = 42` en las tres.

### Resultados

| Config          | Convergencia                                         | $\|w_{\text{final}}\|$ | $\cos(w, v_{\text{PCA}})$ |
| --------------- | ---------------------------------------------------- | ---------------------- | ------------------------- |
| `oja_var_eta05` | **diverge** (overflow → NaN) en época 0              | NaN                    | NaN                       |
| `oja_var_eta02` | 2000 épocas (no dispara $\varepsilon$)               | **1.000136**           | **0.999999**              |
| `oja_fix_1e-3`  | **converge en época 289** ($\|\Delta w\| < 10^{-8}$) | 1.001370               | 0.999929                  |

### Comparación con PCA-librería (`numpy.linalg.eigh`)

$\lambda_{\max} = 3.227166$ (idéntico a `SIA-PCA/Notas/autovalores_autovectores.md`
gracias al cambio a `ddof=1` — ver `explicacion_ddof_y_divergencia.md`).
Autovector PC1 (signo alineado):

| feature | $v_{\text{PCA}}$ | $w_{\text{oja}}$ (η var 0.2) | $w_{\text{oja}}$ (η fijo 10⁻³) |
|---|---:|---:|---:|
| Area         | −0.124874 | −0.125629 | −0.131830 |
| GDP          | +0.500506 | +0.500433 | +0.499861 |
| Inflation    | −0.406518 | −0.407256 | −0.413333 |
| Life.expect  | +0.482873 | +0.483027 | +0.484318 |
| Military     | −0.188112 | −0.187477 | −0.182369 |
| Pop.growth   | +0.475704 | +0.475544 | +0.474207 |
| Unemployment | −0.271656 | −0.271282 | −0.268260 |

Las diferencias son del orden $10^{-4}$ con η variable 0.2 y de $10^{-3}$
con η fijo (peores en `Area` e `Inflation` para η fijo). La interpretación
de PC1 que ya está en `SIA-PCA/Notas/analisis.md` se mantiene: PC1 separa
países "ricos y estables" (GDP, Life.expect, Pop.growth positivos) de
"pobres / inflados" (Inflation, Unemployment, Area negativos).

### Discusión

1. **η inicial 0.5 diverge.** En la primera época, $\|w\|$ crece tan
   rápido que `float64` levanta `RuntimeWarning: overflow` y los pesos
   pasan a NaN. Es exactamente el escenario que la profe advierte ("un
   poco menos de 0.5 recomendaría, pero pruébenlo") — el techo del slide
   14 es **el límite donde puede romperse**, no un valor seguro.
2. **η inicial 0.2 con decay `1/t`** es la corrida más "limpia": converge
   a una dirección prácticamente idéntica al autovector de la librería
   ($\cos \approx 0{,}999999$), con $\|w\|$ pegado a 1 (1.000136). No
   dispara el criterio de corte porque al final de las 2000 épocas el η
   ya es $0{,}2/2000 = 10^{-4}$ y $\|\Delta w\|$ aún es $> 10^{-8}$, pero
   la dirección ya está perfectamente estabilizada.
3. **η fijo 10⁻³** también converge bien y, además, es el único que
   **dispara el criterio $\varepsilon$**: como $\eta$ no se achica, el
   "ruido residual" llega a un piso muy bajo y $\|\Delta w\|$ termina
   cayendo por debajo de $10^{-8}$ en época 289. El autovector queda un
   poco peor que con η variable (diff ~$10^{-3}$ vs ~$10^{-4}$),
   probablemente porque el η fijo no permite refinar tanto como un
   decreciente.

### Conclusión práctica
Para reportar PC1 vía Oja con `europe.csv`: **η variable, $\eta_0 = 0{,}2$,
schedule $1/t$** es el setting más fiel al autovector real (el más grande
de los probados que no rompe el algoritmo). El η fijo $10^{-3}$ funciona
y converge antes (289 épocas vs 2000), pero a costa de una pequeña
pérdida de precisión.
