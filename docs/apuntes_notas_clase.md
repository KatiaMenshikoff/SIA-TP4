
# PCA
## Biplot
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
