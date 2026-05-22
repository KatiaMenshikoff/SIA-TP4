# Consigna
Implementar la red de Kohonen y aplicarla para resolver los siguientes problemas
- Asociar paıses que posean las mismas caracterısticas geopolıticas, economicas y sociales.
- Realizar al menos un grafico que muestre los resultados. 
- Realizar un grafico que muestre las distancias promedio entre neuronas vecinas. 
- Analizar la cantidad de elementos que fueron asociados a cada neurona.

# Apuntes de la clase
Para una muestra (fila del dataset) data, la neurona ganadora es la que tiene pesos mas similares a la fila de entrada.
El representante de una neurona es su vector weights.
Podemos experimentar con las distintas arquitecturas (rectangular-hexagonal-etc)
Podemos experimentar cambiando el radio R
El tamaño de la grilla K debería decidirse en función de la cantidad de filas del dataset.
### Inicializacion
Inicializacion uniforme puede causar "neuronas muertas", neuronas que nunca o casi nunca ganan. Podemos inicializar con alguna muestra del conjunto al azar. 

### Cantidad de iteraciones
Aca tmb podemos experimentar. Podemos empezar con la cantidad total de neuronas
### Visualizacion de resultados
Ver las diapos!! 
- Heatmap. Esta bueno tmb para ver neuronas muertas.
- Registros por neurona. Ejemplo interesante en la clase de que se ve una red que tiene K demasiado grande.
- Matriz U. Distancia promedio entre una neurona y sus vecinas.
- Graficar activacion de neuronas x variable.

# Proceso
Hacemos estandarización de los datos z-score.

## Inicializacion
![[Pasted image 20260519195822.png|589]]
### Arquitectura
Hexagonal vs grilla.
### Cantidad de neuronas de salida
N = 28
Podemos probar K = 2, 3, 4
Con k = 4 estamos border, KxK = 16.
K = 5 ya es extremo por que me queda KxK = 25 que es casi N = 28.
### Inicializar pesos
Vamos a hacer lo de los ejemplos al azar.
Tomar una muestra al azar del set para cada neurona sirve como mitigación de neuronas muertas, porque garantiza que los pesos iniciales estén dentro del rango/distribución de los datos.

  >"Si yo inicializo los pesos de forma random, quizás me quedan muy distintos a mis datos de entrada." → eso lleva a neuronas muertas (las que nunca se activan)
> 
> "Entonces una de las formas para mitigarlo es, en vez de inicializarlo random, directamente asignarle una muestra de mi conjunto de entrenamiento al azar." 
>
>"Algunos pesos van a quedar muy lejos de mi valor inicial, entonces nunca van a ganar. Si nunca ganan se dice que son neuronas muertas. Para evitar eso, puedo inicializar con muestras de mi conjunto de entrenamiento."
### Radio
El radio define el vecindario en cada iteración. La cátedra lo deja como hiperparámetro experimental, pero da dos formas válidas:

- **Radio iterativo**: arrancar con `R(0) = K` (el tamaño de la grilla) y decrementarlo a lo largo de las épocas hasta `R = 1`. Menos que 1 no tiene sentido porque ya no hay vecinas.
- **Radio constante**: dejarlo fijo durante todo el entrenamiento.

 La motivación de `R = K` es simplemente *"considerar todas las neuronas al arrancar"*, y después ir achicando el vecindario.
### Learning rate
Análogo al radio: η tiene que ser menor a 1, y puede ser **constante** o **adaptativo** (decrecer con las épocas).

> "La tasa de aprendizaje tiene que ser menor a 1."
>
> "Puedo tener el adaptive learning rate (...) variar el eta también en función de las épocas."

## Convergencia
En cada epoca:
Se elige una muestra Xp.
Se decide la neurona ganadora en base a la distancia minima entre la fila y la muestra Xp.
Se actualiza la neurona ganadora y sus vecinas en base a la regla de kohonen:
![[Pasted image 20260519203026.png|472]]
### Iteraciones
En cada iteración se toma una sola muestra del dataset.
Se define la cantidad de iteraciones, por ejemplo, En función de la cantidad de neuronas de entrada (N); 500*N.

# Script
Flags para archivo csv, archivo config.json. Parametros, hiperparametros en el config.json.
Hiperparametros:
- K
- R / R variable
- Learning rate
- Cantidad de iteraciones fija / Multiplicador de cantidad de iteraciones para hacer `cantidad*N`, N cantidad de muestras.

Estandarizacion z-score
```python
X_std = (X - X.mean()) / X.std()
```

Definicion modular de arquitectura para implementar hexagonal y grilla.
Los vectores representantes estan en una matriz KxK, la diferencia entre hexagonal vs grilla termina estando en como se calcula el radio.

Inicialización de los pesos: se toma una muestra al azar para cada neurona.

Funcion modularizada para calcular el radio, depende de si se esta usando grilla o hexagonal.

Convergencia/entrenamiento. Funcion para actualizacion de pesos basada en la funcion explicada en clase.

# Experimentos
## Analisis de K