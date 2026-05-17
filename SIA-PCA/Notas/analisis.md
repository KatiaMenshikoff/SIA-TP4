# Análisis PCA sobre europe.csv

Documento para entender qué se hizo, qué se obtuvo y cómo se interpreta.
Todo apoyado en lo visto en la clase (PDF "5 - PCA" y transcripción del audio).

---

## 1. Qué nos pidieron (slide 47)

Sobre el dataset `europe.csv` (28 países × 7 variables: Area, GDP, Inflation,
Life.expect, Military, Pop.growth, Unemployment), usar una librería para
**calcular las componentes principales** e **interpretar PC1 gráfica y teóricamente**.

## 2. Por qué tiene sentido aplicar PCA acá (slides 13, 16)

PCA sirve cuando hay **redundancia** entre variables, es decir, cuando varias
columnas se mueven juntas y cuentan parte de la misma historia. Si las variables
no estuvieran correlacionadas, no tendría sentido aplicar el método.

En `europe.csv` se ve fácil: países con GDP alto tienden a tener mayor
expectativa de vida, menos inflación, menos desempleo. Eso es redundancia.

## 3. Procedimiento aplicado (slide 32)

Se siguieron al pie de la letra los 7 pasos del procedimiento de cátedra:

1. **Construir la matriz X** con las 7 variables en columnas (28 filas, una por país).
2. **Estandarizar** cada columna: `(x − media) / desvío`.
3. **Calcular la matriz de correlaciones Sx**.
4. **Calcular autovalores y autovectores** de Sx.
5. **Ordenar los autovalores de mayor a menor**.
6. **Construir la matriz V** con los autovectores ordenados.
7. **Calcular las componentes Y** como combinación lineal de las variables originales.

### Por qué estandarizar (slides 24-27)

Las variables del dataset tienen escalas muy distintas: Area en cientos de miles
de km², GDP en decenas de miles de dólares, Inflation en porcentajes. Si no se
estandariza, las variables con magnitudes grandes (Area, GDP) **dominan la
varianza solo por su escala**, no por su variabilidad real.

Estandarizar equivale a aplicar PCA sobre la **matriz de correlaciones** en
lugar de la matriz de covarianzas. Es lo recomendado cuando las variables tienen
distintas unidades.

## 4. Lo que se obtuvo

### 4.1 Matriz de correlaciones Sx

Lo primero útil que sale es **leer la matriz Sx** (en `Notas/matriz_correlaciones.md`).
Los pares más fuertes (en módulo cerca de 1, slide 10):

| Par                       | r       | Lectura                                    |
|---------------------------|---------|--------------------------------------------|
| Life.expect ↔ Pop.growth  | +0.77   | mayor expectativa de vida ↔ mayor crecim.  |
| GDP ↔ Pop.growth          | +0.76   | mayor PBI ↔ mayor crecimiento              |
| GDP ↔ Life.expect         | +0.70   | mayor PBI ↔ mayor expectativa de vida      |
| Life.expect ↔ Inflation   | −0.68   | mayor expectativa de vida ↔ menor inflación |
| GDP ↔ Unemployment        | −0.53   | mayor PBI ↔ menor desempleo                |

Hay redundancia clara → PCA aplica.

### 4.2 Autovalores y proporción de varianza (slides 23, 31)

Cada autovalor es la **varianza de su componente**. La proporción explicada por
cada componente es `λᵢ / Σλᵢ`.

| Componente | λᵢ      | % varianza | % acumulado |
|------------|---------|------------|-------------|
| **PC1**    | 3.2272  | **46.10%** | 46.10%      |
| PC2        | 1.1871  | 16.96%     | 63.06%      |
| PC3        | 1.0632  | 15.19%     | 78.25%      |
| PC4        | 0.7704  | 11.01%     | 89.26%      |
| PC5        | 0.4578  | 6.54%      | 95.80%      |
| PC6        | 0.1687  | 2.41%      | 98.21%      |
| PC7        | 0.1256  | 1.79%      | 100.00%     |

**PC1 sola explica el 46% de la variabilidad del dataset**. Con PC1+PC2 se
alcanza el 63%, lo que justifica trabajar en pocas dimensiones.

### 4.3 Cargas de PC1 (primer autovector, slide 21)

```
Y1 = -0.125·Area + 0.500·GDP - 0.407·Inflation + 0.483·Life.expect
     - 0.188·Military + 0.476·Pop.growth - 0.272·Unemployment
```

- Cargas **positivas grandes**: GDP (+0.50), Life.expect (+0.48), Pop.growth (+0.48).
- Cargas **negativas notables**: Inflation (−0.41), Unemployment (−0.27).
- Cargas **chicas**: Area (−0.12), Military (−0.19) → casi no influyen en PC1.

### 4.4 Verificación de que se eliminó la redundancia (slide 14)

Calculamos la matriz de correlaciones **de las Y** y dio la identidad
(ceros fuera de la diagonal, con error numérico ~10⁻¹⁵). Eso confirma que las
nuevas variables son no correlacionadas entre sí, justo el objetivo principal
del método (slide 13).

## 5. Interpretación de PC1

### 5.1 Interpretación teórica (slides 21, 38)

PC1 es una **combinación lineal de las 7 variables originales** elegida para
capturar la mayor varianza posible.

Mirando los signos de las cargas (slide 38):

- Variables con **carga positiva** se correlacionan positivamente con PC1.
  → países con valores altos en GDP, Life.expect, Pop.growth tendrán Y1 alto.
- Variables con **carga negativa** se correlacionan negativamente con PC1.
  → países con Inflation y Unemployment altos tendrán Y1 bajo.

PC1 funciona como un **índice** (slide 38: *"la primera componente representa un
índice por el cual se pueden ordenar los registros"*). En el ejemplo de la
clase (slide 37) PC1 representaba "capacidad de gasto" de las provincias. En
nuestro caso, podemos interpretarlo como un **índice de nivel de desarrollo
socioeconómico**: un solo número que combina riqueza, calidad de vida y
estabilidad económica.

### 5.2 Interpretación gráfica (gráfico de barras de Y1, slide 46)

Al calcular Y1 para cada país y ordenarlos, el ranking queda:

| Top 5 (Y1 más alto)  | Y1    | Bottom 5 (Y1 más bajo)  | Y1     |
|----------------------|-------|-------------------------|--------|
| Luxembourg           | +3.42 | Ukraine                 | −4.50  |
| Switzerland          | +3.22 | Bulgaria                | −2.56  |
| Norway               | +2.07 | Estonia                 | −2.44  |
| Netherlands          | +1.81 | Latvia                  | −2.26  |
| Ireland              | +1.78 | Lithuania               | −1.50  |

La separación visual es clara:
- **Y1 positivo y grande** → países de Europa occidental y nórdica de altos
  ingresos.
- **Y1 cercano a 0** → países del sur (España, Italia, Portugal) y algunos del
  centro-este de la UE.
- **Y1 negativo y grande** → países del este post-soviético y Ucrania.

PC1 ordena los países, sin que se lo hayamos pedido explícitamente, en el mismo
sentido que cualquier ranking informal de "desarrollo en Europa".

### 5.3 Sobre el signo del autovector (slide 46)

En nuestro caso el autovector salió orientado de forma natural ("más
desarrollo = Y1 positivo"). Si la librería hubiera devuelto el autovector
opuesto, habría que **invertir el signo** y aclararlo, tal como hace la clase
en la slide 46 con la nota "autovector opuesto". Matemáticamente `v` y `−v`
son ambos autovectores válidos.

## 6. Casos puntuales que ayudan a entender PC1

**Finlandia (Y1 = +0.21)** queda casi en el centro, sorprendentemente baja
para ser nórdica. La razón es que PC1 no es "ser rico"; es una mezcla. En
Finlandia el GDP es modesto comparado con Luxemburgo o Noruega, y el
crecimiento poblacional es casi nulo (0.07), lo que pesa porque Pop.growth
tiene carga positiva grande. Esto ilustra el mensaje de slide 38: PC1 es un
índice combinado, y los resultados pueden contradecir la intuición sobre
variables aisladas.

## 7. Reducción de dimensión efectiva (slides 16, 23)

- Originalmente: 7 variables → 28×7 = 196 valores.
- Con solo PC1: 28×1 = 28 valores, y conservamos el 46% de la variabilidad.
- Con PC1 + PC2: 28×2 = 56 valores, y conservamos el 63%.

Hay una **pérdida de información** controlada (slide ~147 del transcript:
*"hay cierta pérdida de información (...) pero se puede medir y no es tan
relevante"*), pero a cambio se obtiene un dataset mucho más fácil de
visualizar e interpretar, sin la redundancia original.

## 8. Resumen ejecutivo (para arrancar la presentación)

- Aplicamos PCA sobre `europe.csv` (28 países × 7 variables).
- Estandarizamos las variables porque las escalas eran muy distintas.
- La matriz de correlaciones mostró redundancia clara (GDP, Life.expect y
  Pop.growth fuertemente correlacionadas entre sí).
- PC1 explica el **46.1%** de la varianza total.
- Las variables que más pesan en PC1 son GDP, Life.expect, Pop.growth (signo +)
  e Inflation, Unemployment (signo −).
- PC1 actúa como un índice de **nivel de desarrollo socioeconómico**: ordena los
  países desde Luxemburgo y Suiza (más desarrollados) hasta Ucrania (menos).
- Las componentes Y resultantes no están correlacionadas entre sí — se eliminó
  la redundancia del dataset original.

## 9. Archivos generados

| Archivo                                | Contenido                                  |
|----------------------------------------|--------------------------------------------|
| `pca_europe.py`                        | Script con todos los cálculos              |
| `boxplot_original.png`                 | Boxplot de las variables originales        |
| `boxplot_estandarizado.png`            | Boxplot tras estandarizar                  |
| `pc1_por_pais.png`                     | Gráfico de barras de Y1 por país (slide 46)|
| `biplot.png`                           | Biplot PC1 vs PC2 (slide 45)               |
| `Notas/matriz_correlaciones.md`        | Matriz Sx + cálculo de referencia s_11     |
| `Notas/autovalores_autovectores.md`    | Autovalores, V y componentes Y             |
| `PCA_europe_seguimiento.pptx`          | Presentación con el seguimiento de pasos   |
