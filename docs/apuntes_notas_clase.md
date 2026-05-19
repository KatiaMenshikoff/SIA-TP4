# Kohonen
Para una muestra (fila del dataset) data, la neurona ganadora es la que tiene pesos mas similares a la fila de entrada.
El representante de una neurona es su vector weights.
Podemos experimentar con las distintas arquitecturas (rectangular-hexagonal-etc)
Podemos experimentar cambiando el radio R
El tamaño de la grilla K debería decidirse en función de la cantidad de filas del dataset.

## Inicializacion
Inicializacion uniforme puede causar "neuronas muertas", neuronas que nunca o casi nunca ganan. Podemos inicializar con alguna muestra del conjunto al azar. 

## Radio - Adaptive ratio 
Podemos definir r = K , y luego ir decrementando r; La idea de r = K es para tener de vecinos a todos cuando empezamos inicializando con muestras ranodm. 
Tmb hay adaptive learning rate.

## Cantidad de iteraciones
Aca tmb podemos experimentar. Podemos empezar con la cantidad total de neuronas

## Visualizacion de resultados
Ver las diapos!! 
- Heatmap. Esta bueno tmb para ver neuronas muertas.
- Registros por neurona. Ejemplo interesante en la clase de que se ve una red que tiene K demasiado grande.
- Matriz U. Distancia promedio entre una neurona y sus vecinas.
- Graficar activacion de neuronas x variable.

# PCA
##Biplot
Grafico que pone la componente principal en el eje X, contra la PC2 en el eje Y.
La magnitud de cada vector es su valor en el vector a. A mayor magnitud, mas peso tiene en el dataset.
Vectores que estan alineados en el biplot estan mas correlacionados.
Los puntos en el biplot, las muestras individuales, quedan alineadas con algunos vectores y desalineados con otros. Esto nos dice visualmente donde queda parada cada muestra con respecto a cada feature. Podrías decir que variables muy correlacionadas traen redundancia. Notar que podemos estar alineados en la direccion, pero no en el sentido. Literalmente una muestra puede estar alineada OPUESTA a algun vector.
A partir del biplot podemos generar clusters con las muestras. Agrupas a partir de como se alinean conjuntos de muestras a partir de ciertos vectores.

# Regla de oja
Es un perceptron lineal con otra funcion de actualizacion de pesos, que converge en el vector de la PC1.
Sanity check: graficar y ver que la dirección de mayor varianza se alinea con el valor final del perceptron (regla de oja slide 13)
## Learning rate
Estandarizar todas las variables de entradas y empezar con eta < 0.5  ( o incluso menos, slide 14)
Podemos usar eta adaptativo que se va reduciendo o uno muy chico, slide 15.
## Regla de sanger
Es como la regla de oja pero consigue todos los autovectores.
