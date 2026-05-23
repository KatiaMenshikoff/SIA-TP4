# Resumen — SIA TP4: Aprendizaje No Supervisado

*Sistemas de Inteligencia Artificial — 2026*

---

## 1. Introducción al Aprendizaje No Supervisado

### Supervisado vs. no supervisado

- **Supervisado**: el agente tiene acceso a **etiquetas**; conoce la variable de respuesta. Tareas bien definidas: clasificación y regresión.
- **No supervisado**: la **variable de respuesta no está disponible**. Permite resolver problemas menos definidos. Tres grandes problemas: *clustering*, *asociación* y *reducción de dimensionalidad*.

> 💬 **Profesor:** *"Lo más más importante es esto: no tengo etiquetas, no tengo la variable respuesta."*

### ¿Qué es?
No se conoce el valor de verdad. Se construyen modelos de predicción y estrategias para obtener características o patrones y sacar conclusiones. Pregunta clave: *¿cómo sabemos si los resultados son significativos?*

### Tres problemas que resuelve
- **Clustering**: agrupar observaciones de forma que la similitud dentro del grupo sea lo más fuerte posible. Implica *definir similitud*. Ej.: medicina, detección de anomalías (outliers), marketing.
- **Asociación**: encontrar relaciones entre atributos. *Memorias asociativas* (ej. modelo de Hopfield), sistemas de recomendación.
- **Reducción de dimensión**: proyectar en un espacio menor descartando características poco relevantes. Ej.: PCA, autoencoders.

### Por qué importa
Etiquetar es costoso; muchas *features* dificultan la aproximación; los *outliers*, si se ignoran, contaminan el aprendizaje. El no supervisado aborda los tres.

### Redes que se ven en la materia
Kohonen, Hopfield, Oja y Sanger.

---

## 2. Modelo de Kohonen (SOM)

Publicado por T. Kohonen (1982). Durante el aprendizaje la red descubre por sí misma regularidades (patrones) en los datos. SOM = *Self-Organizing Map*.

### Arquitectura
Una sola capa con forma de grilla bidimensional *k × k*. Cada neurona está conectada a todas las componentes del vector de entrada *n*-dimensional. Cada neurona *j* tiene un vector de pesos $W_j = (w_{j1}, \dots, w_{jn})$ **de la misma dimensión que la entrada**: es el "representante" de la neurona. Pasa de un espacio multidimensional a uno bidimensional.

### Aprendizaje competitivo
Las neuronas compiten; finalmente sólo una se activa (**neurona ganadora**); las demás quedan en valores mínimos. Entradas similares activan la misma neurona ⇒ clasificación / agrupamiento.

### Vecindario
Radio *R*. Grilla rectangular: 4-vecinos (*R = 1*), 8-vecinos (*R = √2*). También existe grilla hexagonal. Neuronas vecinas contienen datos con cierto grado de similitud.

### Estandarización (paso previo obligatorio)
- Min-max: $X' = \frac{X - X_{\min}}{X_{\max} - X_{\min}}(b - a) + a$
- Z-score: $\tilde X_i = (X_i - \overline{X_i})/s_i$
- Unit length: $X' = X / \lVert X \rVert$

> 💬 **Profesor:** *"Es muy importante estandarizar todos los vectores"* — si no, una variable de mayor rango (p. ej. presión) domina sobre las demás (p. ej. edad).

### Algoritmo
1. **Inicialización**: registros $X^p$, definir *k × k*, inicializar $W_j$ con distribución uniforme *o* con muestras del training set, fijar *R(0)* y *η(0) < 1*.
2. **Iteración *i***: seleccionar $X^p$; hallar la neurona ganadora $\hat k$ tal que $W_{\hat k} = \arg\min_j d(X^p - W_j)$; actualizar las neuronas vecinas con la **regla de Kohonen**.

### Regla de Kohonen
Vecindario $N_{\hat k}(i) = \{n : \lVert n - n_{\hat k} \rVert < R(i)\}$.

$$
W_j^{i+1} = \begin{cases} W_j^i + \eta(i)(X^p - W_j^i) & \text{si } j \in N_{\hat k}(i) \\ W_j^i & \text{si } j \notin N_{\hat k}(i) \end{cases}
$$

Con *η(i) → 0* (p. ej. *η(i) = 1/i*). *R(i) → 1* cuando *i → ∞* (también puede mantenerse constante).

### Convergencia
$\lVert W_{\hat k}^{i+1} - X^p \rVert \le \lVert W_{\hat k}^i - X^p \rVert$: los pesos se "parecen" a los datos de entrada.

### Similitud
Distancia euclídea o exponencial $e^{-\lVert X_p - W_j \rVert^2}$. *Importante: estandarizar todos los vectores.*

### Inicialización: cuidado con unidades muertas
Iniciar los pesos al azar puede dejar neuronas que nunca ganan (**unidades muertas**); para evitarlo conviene inicializar con muestras del conjunto de entrada. Iteraciones: por ejemplo *500·N*. *R(0)* puede ser el tamaño total de la grilla, decreciendo hasta 1, o constante.

### Visualización de resultados
- Conteo de registros por neurona (*heatmap* de entradas por neurona).
- **Matriz U** (*Unified Distance Matrix*): para cada neurona, promedio de distancia euclídea entre su vector de pesos y los de sus vecinas. Si el método funciona, las distancias deben ser pequeñas.
- Observar el valor promedio de *una sola* variable en cada neurona.

### Ventajas / desventajas
**Ventajas**: puede ser más rápida que el MLP; aplica a datos sin etiquetas; reduce a 2D.
**Desventajas**: si hay muchas variables es difícil mapear a 2D; sólo variables numéricas; no hay criterio demostrado para fijar el tamaño de la grilla.

---

## 3. Autovalores y Autovectores

### Combinación lineal
$\bar w = \alpha_1 \bar v_1 + \dots + \alpha_n \bar v_n$, con $\alpha_i \in \mathbb{K}$.

### Definición
El **autovector** es el vector que mantiene su dirección al aplicarse una transformación; el **autovalor** es el factor por el cual se escala:

$$A\bar v = \lambda \bar v, \quad \bar v \neq 0.$$

Equivalente a $(A - \lambda \mathbb{I})\bar v = 0$, con solución no trivial cuando el **polinomio característico** $P(\lambda) = \det(A - \lambda \mathbb{I}) = 0$. Las raíces son los autovalores; los autovectores se obtienen resolviendo $(A - \lambda \mathbb{I})\bar v = 0$ para cada *λ*.

> 💬 **Profesor:** *"Lo clave: el vector que mantiene la dirección (autovector) y el factor por el cual se escala (autovalor). El rojo es el que tiene más módulo, eso es importante."*

---

## 4. Análisis de Componentes Principales (PCA)

### Medidas descriptivas
- Media: $\overline X = \frac{1}{n} \sum x_i$
- Varianza muestral: $s^2 = \frac{1}{n-1} \sum (x_i - \overline X)^2$
- Covarianza muestral entre $X_i, X_k$:

$$s_{ik} = \frac{1}{n} \sum_{j=1}^m (x_{ji} - \overline{x_i})(x_{jk} - \overline{x_k})$$

La matriz de covarianzas *S* es **simétrica definida positiva**. Interpretación: $s_{ik} > 0$ asociación lineal positiva, $< 0$ negativa, $= 0$ independientes. Correlación: $r_{ik} = s_{ik}/\sqrt{s_{ii}s_{kk}}$ (covarianza con variables estandarizadas).

### Idea
Si las variables están muy correlacionadas hay información redundante. PCA **elimina la redundancia**: transforma el conjunto original en otro de variables que son *combinaciones lineales* de las originales pero **no están correlacionadas entre sí**.

> 💬 **Profesor:** *"Ojo, como paréntesis: si no están correlacionadas, entonces ya no tiene sentido hacer PCA."*

### Variabilidad
Se toma la característica que **maximiza la variabilidad**; es un buen factor para diferenciar objetos. Historia: Hotelling (1933); ajustes ortogonales por cuadrados mínimos de Pearson (1901).

### La primera componente

$$y_1 = \sum_{j=1}^p a_{1j}(x_j - \overline{x_j})$$

Los $a_{ji}$ son las **cargas (loadings)**. Si las variables están estandarizadas no hace falta restar la media. Se busca $\bar a_1 / \lVert \bar a_1 \rVert = 1$ tal que $\text{Var}(y_1)$ sea máxima.

### Cómo se obtienen las cargas
*Las cargas son los autovectores de la matriz de covarianzas (o correlaciones).* Se resuelve $\det(S_x - \lambda_i \mathbb{I}) = 0$ y $S_x \bar v_i = \lambda_i \bar v_i$. La componente *i*-ésima:

$$y_i = v_{1i}x_1 + \dots + v_{ni}x_n$$

El autovalor $\lambda_i$ es la **varianza** de la componente *i*. Ordenando *λ* de mayor a menor y tomando los primeros *q* autovectores se reduce la dimensionalidad reteniendo la mayor variabilidad.

### Covarianza vs. correlación
Si las escalas de medida son muy distintas, la maximización de la varianza **depende decisivamente de las escalas**. Para evitarlo se **estandarizan** las variables, lo que equivale a usar la **matriz de correlaciones** en lugar de la de covarianzas. Si las variables están en las mismas unidades, ambas alternativas son válidas.

### Procedimiento
1. Armar *X* con variables en columnas.
2. **Estandarizar** las variables.
3. Calcular la matriz de correlaciones $S_x$.
4. Calcular autovalores y autovectores.
5. Ordenar autovalores de mayor a menor.
6. Construir *V* con los autovectores asociados a los mayores autovalores.
7. Calcular *Y* como combinación lineal de las originales.

### Interpretación de PC1
Si la carga de una variable en PC1 es positiva ⇒ correlación positiva con la componente; si es negativa ⇒ correlación negativa. PC1 funciona como un **índice** por el cual se pueden ordenar los registros (p. ej. "capacidad de gasto" en encuestas de presupuestos familiares).

> 💬 **Profesor:** *"Esa distinción se entendió porque esto suele pasar: en distintos grupos quedan distintos autovectores, por ahí a alguno le queda el opuesto."* (Es válido; cambia el signo del índice, no la interpretación.)

---

## 5. Regla de Oja y Sanger

### Motivación
Algunos modelos de redes neuronales permiten calcular las componentes principales de forma *iterativa*.
- **Ventaja**: menor costo computacional para datasets grandes.
- **Desventaja**: si el dataset tiene muchas variables, reducir a una sola componente puede perder información.

### Perceptrón lineal simple

$$O^\mu = \theta\left(\sum_{i=1}^n x_i^\mu w_i^\mu\right), \qquad \Delta w = \eta(\zeta^\mu - O^\mu)x^\mu$$

### Aprendizaje hebbiano (no supervisado)
Como no hay "valor de verdad":

$$\Delta w = \eta \, O^\mu x^\mu$$

**Oja demostró** que si esta red convergiera, $w^{\text{final}}$ apuntaría a la *dirección de máxima variación* (la PC1). *Problema*: no converge porque *Δw* crece en cada paso y se vuelve inestable.

### Regla de Oja
(Dr. Erkki Oja, Helsinki). Se normaliza el peso:

$$w_j^{n+1} = \frac{w_j^n + \Delta w}{\left(\sum_{j=1}^N (w_j^n + \Delta w)^2\right)^{1/2}}$$

Aplicando Taylor:

$$\boxed{\Delta w = \eta\,(O\,x_i^n - O^2 w_i^n)}$$

$\lVert w \rVert$ queda acotado, tiende a 1. Tras varias iteraciones converge al **autovector asociado al mayor autovalor** de la matriz de correlaciones de los datos. Con ese $w^{\text{final}}$ se construye la PC1: $y_1 = a_1 x_1 + \dots + a_n x_n$, con $a_i = w_i^{\text{final}}$.

> 💬 **Profesor:** *"Ojo: acá no es que converge a la PC1, sino que converge el autovector asociado a la PC1; después yo puedo calcular la componente."*

### Tasa de aprendizaje
Cota teórica de convergencia: $\eta_0 = 1/(1{,}2\lambda_1)$. Como $\lambda_1$ no se conoce, se **estandarizan** las entradas y se arranca con $\eta_0 \le 0{,}5$ (la profe sugiere verbalmente *"un poco menos"* de 0,5). Dos esquemas válidos:

- **η adaptativo**: $\eta(0) = 0{,}5$ decreciente a lo largo de las épocas.
- **η fijo chico**: $\eta = 10^{-3}$.

> 💬 **Profesor:** *"Como no conozco el autovalor, lo que se hace es estandarizar todas las variables de entrada, correr la red con un η menor a 0,5, incluso un poco menos recomendaría, pero pruébenlo."*

Se espera probar varios valores y reportar el comportamiento.

### Implementación
- **Arquitectura**: perceptrón simple, una sola salida, **función de activación lineal** ($y = w^\top x$, sin $\theta$ no-lineal).
- **Inicialización**: $w$ con distribución uniforme en $[0, 1]$.
- **Entradas**: estandarizadas (media 0, desvío 1) — requisito explícito del slide del algoritmo.
- **Modo**: *online* (un patrón por iteración, no batch). Por época se recorren las $M$ muestras una por una, actualizando $w$ después de cada muestra.
- **Actualización** (regla de Oja, forma post-Taylor):

$$\Delta w = \eta \cdot y \cdot (x - y \cdot w) \quad \equiv \quad \eta(O\,x_i^n - O^2\,w_i^n)$$

- **Convergencia esperada**: $\lVert w \rVert \to 1$ y dirección estable entre épocas.
- **Salida**: $w^{\text{final}} \approx$ autovector de PC1; la componente se reconstruye como $\text{PC1} = \sum_i w_i^{\text{final}} \cdot x_i$ (con $x$ estandarizadas). Puede salir con **signo opuesto** al de la librería — sigue siendo válido.

> 💬 **Profesor:** *"La red de Oja es un perceptrón simple lineal con esta actualización de pesos. Básicamente ya tienen el código del perceptrón simple lineal: lo único que hay que hacer es cambiar cómo se actualizan los pesos."*

### Algoritmo (Oja)

**Notación** (cuidado con el cruce de letras entre el slide 16 y el slide 7):

- $M$ = cantidad de **muestras / patrones** (en `europe.csv`, los 28 países). En el slide aparece como `N`, pero conviene renombrar para evitar confusión.
- $n$ = **dimensión de cada $x^\mu$** = nº de variables = nº de pesos (en `europe.csv`, 7: `Area`, `GDP`, `Inflation`, `Life.expect`, `Military`, `Pop.growth`, `Unemployment`).

#### Versión vectorial (recomendada para implementar)

```
input: X (M muestras, n variables, estandarizadas), eta, w ~ Uniforme[0,1]^n
for epoch in #epochs:
    for mu = 1..M:                      # una muestra/país por iteración
        y = w · x[mu]                   # escalar (producto interno)
        w += eta * y * (x[mu] - y * w)  # actualización VECTORIAL de los n pesos
return w
```

#### Versión escalar equivalente (componente a componente)

```
for epoch in #epochs:
    for mu = 1..M:
        y = sum_j (w_j * x[mu]_j)       # un solo escalar por muestra
        for j = 1..n:
            w_j += eta * y * (x[mu]_j - y * w_j)
```

**Las dos formas son idénticas**: la línea `w += eta * y * (x - y*w)` ya hace el `for j` implícito con vectores.

#### Lo importante: `y` se calcula UNA vez por muestra

- ✅ **Correcto**: calcular $y = w \cdot x^\mu$ una vez con el $w$ actual, y después actualizar **todos los $w_j$ en paralelo** usando ese mismo $y$.
- ❌ **Incorrecto**: actualizar $w_1$, recalcular $y$ con el nuevo $w_1$, después $w_2$, recalcular $y$ de nuevo, etc.

Por eso conviene implementarlo vectorizado con `numpy`: garantiza que todos los $w_j$ ven el mismo $y$.

#### Frecuencia de actualizaciones por época (ejemplo `europe.csv`: $M=28$, $n=7$)

| Operación | Veces por época |
|---|---|
| Cálculo de $y$ (forward) | 28 (una por país) |
| Actualización vectorial de $w$ | 28 |
| Actualización escalar de un $w_j$ individual | $28 \times 7 = 196$ |
| Pasadas completas por el dataset | 1 |

Es **online / SGD por muestra**, no batch. El `+=` ocurre **dentro** del `for mu`, no después.

### Regla de Sanger
Extensión de Oja. Converge a la **matriz de autovectores** de la matriz de covarianzas; permite encontrar las *k* componentes principales. *No se pide implementarla en el TP.*

> 💬 **Profesor:** *"Esto (Sanger) no lo van a tener que implementar; se los comento porque Oja me da la primera componente."*

---

## 6. Enunciado del TP4 y notas importantes del profesor

El enunciado se trabaja sobre el dataset `europe.csv` (28 países, variables: `Country`, `Area`, `GDP`, `Inflation`, `Life.expect`, `Military`, `Pop.growth`, `Unemployment`).

### Ejercicios obligatorios
1. **Kohonen**: agrupar los países con una red SOM, analizando heatmap de entradas, matriz U e interpretación de las neuronas.
2. **PCA con librería**: calcular las componentes principales, interpretar PC1 gráfica y teóricamente (entrega previa).
3. **Oja**: implementar a mano la red de Oja (sin librerías) y obtener la PC1.
4. **Comparar** el resultado de Oja contra el de PCA por librería.
5. **Hopfield**: se suma en una semana posterior.

### Cosas a tener en cuenta (énfasis del profesor)

- *"La idea es que hagan un análisis exhaustivo sobre Kohonen."* Variar *k* (tamaño de grilla), radio *R* del vecindario, tipo de grilla (cuadrada o hexagonal), forma de actualizar, manejo de neuronas muertas, interpretación de los vecinos y de la neurona ganadora.
- *"Ver el heatmap de Kohonen y la matriz U y poder interpretarlo"*; analizar cuántos países fueron asociados a cada neurona.
- *"Hay muchas formas de resolver un mismo problema. La idea es que se lleven varias técnicas"* — el mismo problema se resuelve con Kohonen y con Oja/PCA.
- **Pre-entrega** del ejercicio PCA con librería el **jueves siguiente**, antes de las 9:00, por campus, y luego defensa en clase. *"Aprovechen para equivocarse y sacarse las dudas: si tienen mal eso, después no van a poder comparar con Oja."*
- Para comparar Oja con PCA: *"tiene que dar lo mismo o el autovector opuesto"* (signo opuesto es admisible).
- En el análisis de PCA: interpretar el **biplot**, interpretar el **índice** de PC1, qué significan las **cargas**, cómo se calculan autovalores y autovectores (lo hace la librería, pero hay que entenderlo).
- Antes de hacer PCA: chequear que las variables *estén correlacionadas*; si no lo están, no tiene sentido.
- *"Es muy importante estandarizar todos los vectores"*: aplica tanto a Kohonen como a PCA/Oja — variables como `Area` y `GDP` tienen escalas órdenes de magnitud distintas a `Inflation` o `Pop.growth`.
- Cronograma: Kohonen primero, luego PCA/Oja, luego Hopfield ⇒ los temas quedan distribuidos en el tiempo; *"todos deberían saber de todas las redes."*
- Asistencia a la pre-entrega: si alguien del grupo no puede ir, *"puede representar tu grupo"* otro integrante.
