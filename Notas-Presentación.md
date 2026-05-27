# Kohonen
## LR learning rate
Con n = n0/i, decae como 1/i.
Inicialmente vale n0 y despues decae rapidamente
![[Pasted image 20260527154435.png|175]]
## Radio
### R₀ = K

> "Si mi grilla es de K por K y arranco con mi radio igual a K, entonces todos van a ser mis vecinos. Es una forma de arrancar para considerar todas las neuronas, y después le resto uno a lo largo de las épocas hasta llegar a 1, porque menos que 1 no puede ser mi radio."

O sea: el caso `R₀ = K` con decay lineal hasta 1 lo presentó como **una de las formas válidas de arrancar** (no como única receta — también dijo "lo pueden definir ustedes"). Encaja exactamente con lo que tenemos en.
### Fórmula de radio variable
La fórmula

R(i) = max(1, R₀ − (R₀ − 1) · (i − 1)/(T − 1))

con `T = #iteraciones = 500 * N = 14.000`

es la traducción literal de lo que dijo Euge en clase, generalizada a iteraciones en vez de épocas:

1. **Empieza en R₀ y termina en 1.** Euge: *"arranco con mi radio igual a K […] y le resto uno a lo largo de las épocas hasta llegar a 1"*. Eso es exactamente una **interpolación lineal de R₀ a 1**: en `i=1` da R₀, en `i=T` da 1.

2. **Piso en 1 (`max(1, ·)`).** Euge: *"menos que 1 no puede ser mi radio, como mínimo tengo que tener arriba, abajo, izquierda y derecha como vecinas"*. El `max` solo importa por seguridad numérica (con `total_iter > 1` la expresión nunca baja de 1, pero el clamp lo deja explícito).

3. **Por qué lineal en `i` y no "−1 por época".** En el código no trabajamos por épocas completas sino por **muestreo random de 14 000 iteraciones** (= 500·N). Si hiciéramos "restar 1 por época", con `R₀ = K = 3` llegaríamos a `R=1` en 2 épocas (~56 iter) y las 13 944 iteraciones restantes serían con vecindario mínimo. Repartir el decay linealmente sobre las T iteraciones mantiene el espíritu de la receta de cátedra (R₀ → 1 a lo largo del entrenamiento) y deja que el SOM use el vecindario amplio durante una fracción razonable de la corrida.