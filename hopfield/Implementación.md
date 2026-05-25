# Hopfield — plan de implementación

Notas para resolver el ejercicio 2 (Hopfield) del TP4. Las decisiones siguen lo que dijeron Euge (clase teórica de Hopfield) y Santi (clase de ortogonalidad). Citas y referencias al final.

## Lo que pide la consigna

- Construir patrones de letras del abecedario en matrices **5×5** con valores `1` (pixel encendido) y `-1` (pixel apagado).
- Almacenar **4 patrones** en la red.
- Implementar Hopfield para asociar muestras ruidosas de 5×5 al patrón almacenado más cercano.
- Analizar **ortogonalidad**, **ruido**, **función de energía** y **estados espurios**.

Lo básico primero; después se puede explorar más (cambiar tamaño, agregar patrones, usar algo que no sean letras, etc.).

## Decisiones clave

### 1. Generación del abecedario

- Está en `letters.txt`, 26 letras A-Z dibujadas a mano. `*` = `1`, cualquier otro carácter = `-1`. Separador `=`.
- Cada letra se carga como `np.ndarray` de `(5, 5)`. Para la red usamos el flatten de 25 dimensiones.
- En la presentación **incluir el abecedario completo en un recuadro** (Santi lo pidió explícito).

### 2. Selección del grupo de 4 letras

- Hay C(26, 4) = 14.950 combinaciones de 4 letras posibles.
- Para cada grupo armamos `K = [v_A; v_B; v_C; v_D]` (matriz 4×25) y calculamos `K · K^T`. Fuera de la diagonal queda el producto interno entre cada par. En la diagonal queda 25, que ponemos en 0 para no contaminar el promedio.
- Ranking por dos métricas (ambas en valor absoluto):
  - **`|<,>| medio`**: promedio de los productos internos entre pares distintos. Queremos que sea **chico** → patrones más "ortogonales".
  - **`|<,>| max`** + count: máximo del producto interno entre pares y cuántas veces aparece ese máximo. Sirve porque el promedio solo pierde información: un grupo con un solo par muy parecido puede tener el mismo promedio que un grupo con varios pares medianamente parecidos.
- Decisión: **preferimos `|<,>| medio` menor**, y entre grupos empatados, menor `|<,>| max` y menor `count`. Santi dijo explícito que es preferible producto interno medio chico, pero hay que justificarlo experimentalmente.
- **Probar varios grupos de 4**, no quedarnos solo con uno. Mostrar al menos un grupo bueno (`|<,>| medio` chico), uno malo (`|<,>| medio` alto), y comparar comportamiento ante ruido.

Todo este análisis está en el notebook `ortogonalidad_letras.ipynb` (replica el que mostró Santi).

### 3. Red de Hopfield

Implementación a mano (un archivo `hopfield.py` con clase `Hopfield`):

- **Pesos**: `W = (1/N) · K · K^T` donde `K` tiene a cada patrón almacenado como columna. Notación de shape:
  - `N` = dimensión del patrón = 25 (5×5 aplanado, una entrada por neurona).
  - `p` = cantidad de patrones almacenados = 4.
  - `shape (N, p)` significa una matriz con `N` filas y `p` columnas, o sea `25 × 4`: cada columna es un patrón completo (25 píxeles) y hay 4 columnas (una por letra).
  - Entonces `K · K^T` tiene shape `(N, p) · (p, N) = (N, N) = 25 × 25`. Esa es la matriz de pesos: una fila/columna por neurona, con `W_ij` = peso de la conexión entre la neurona `i` y la neurona `j`.
  - Si preferís armar `K` con patrones por **fila** (shape `(p, N) = 4 × 25`, más natural en numpy), la fórmula equivalente es `W = (K_filas.T @ K_filas) / N`.
  - `W` se calcula **una sola vez**, antes de empezar a iterar.
- `W` sale **simétrica por construcción** (`W_ij = W_ji` porque `ξ_i·ξ_j = ξ_j·ξ_i`, o equivalente `(K·K^T)^T = K·K^T`). Lo único que hay que hacer a mano es `np.fill_diagonal(W, 0)`: sin esto la diagonal queda en 1, y el modelo no admite conexión de una neurona consigo misma.
- **Actualización síncrona** del estado: `S_{t+1} = sign(W · S_t)`, con la convención de que `sign(0) = S_t[i]` (mantener estado previo cuando `h_i = 0`).
- **Inicialización**: `S_0 = patrón_de_consulta` (puede ser uno ruidoso).
- **Condición de corte**: cuando `S_{t+1} == S_t` → estado estable. Guardar también el caso `S_{t+2} == S_t` para detectar **ciclos** (2-ciclos son los más típicos en sincronica).
- **Límite de iteraciones**: poner un tope (ej. 50) para no quedar en loop infinito.
- Devolver `(estado_final, lista_de_estados_intermedios, motivo_corte)` para poder graficar la trayectoria y evaluar qué pasó.

### 4. Análisis de ruido

Generar patrones ruidosos a partir de los almacenados:

- Función `noise_transform(pattern, noise_level)` que da vuelta cada pixel con probabilidad `noise_level` (0 a 1).
- Para cada nivel de ruido (ej. 0%, 5%, 10%, ..., 50%), correr varias muestras (ej. 50 por nivel, con seeds distintas) y medir métricas.

### 5. Métricas custom

Euge sugirió armar métricas tipo TP/FP/TN/FN, decididas por nosotros. Propuesta:

- **TP (acierto)**: le pasé una `A` con ruido y la red converge a la `A` almacenada.
- **FP (confusión)**: le pasé una `A` con ruido y la red converge a otro patrón almacenado (`B`, `C`, `D`).
- **Espurio**: converge a un estado estable que no es ninguno de los 4 almacenados (puede ser el complemento de uno almacenado, una mezcla, etc.).
- **Ciclo**: no converge, queda oscilando entre 2 (o más) estados.

Reportar la distribución de esos 4 outcomes para cada grupo de 4 y cada nivel de ruido. Esto es lo que permite comparar redes entre sí.

Decisión de implementación: la convención que adoptemos para los outcomes hay que **explicarla en la presentación** (Euge lo aclaró).

### 7. Experimentos a correr

- **Cantidad de patrones almacenados**: probar 3, 4, 5, 6 patrones. El límite teórico es ~`0.15 · N` ≈ 3.75, pero la práctica suele permitir más con buena ortogonalidad. Esperamos ver degradación a partir de 4 o 5.
- **Comparar grupos de 4 buenos vs malos**: el mejor grupo por `|<,>| medio` vs el peor. Esperamos mucha mejor tolerancia al ruido en el bueno.
- **Curva de tolerancia al ruido**: % de TP vs nivel de ruido, una curva por grupo.
- **Estados espurios**: armar un input bien ruidoso (50%+) y mostrar a qué espurio converge. Graficar la energía.

### 8. Gráficos requeridos

- Abecedario completo en un recuadro (presentación).
- Grupo elegido de 4 letras (visualizar las 4).
- Para algunas consultas representativas: secuencia de estados de la red (input ruidoso → S₁ → S₂ → ... → estado final) como tira de dibujitos 5×5.
- Píxeles errados entre patrón objetivo y salida de la red (heatmap del XOR para resaltar dónde falló).
- Función de energía vs iteración.
- Tabla/heatmap de outcomes (TP/FP/Espurio/Ciclo) por nivel de ruido.
- Tabla con los mejores y peores grupos de 4 según `|<,>| medio` y `|<,>| max` (sale del notebook de ortogonalidad).

## Estructura de archivos sugerida

```
hopfield/
  letters.txt                    # abecedario A-Z en 5×5
  ortogonalidad_letras.ipynb     # notebook de Santi (ya está)
  hopfield.py                    # clase Hopfield (TODO)
  utils.py                       # noise_transform, métricas, plots (TODO)
  experimentos.ipynb             # análisis principal (TODO)
  Implementación.md              # este archivo
```

## Limitaciones de Hopfield (para mencionar en el informe)

1. **Ortogonalidad**: los patrones deberían ser ortogonales (producto interno = 0). Cuanto más se aleje el producto interno de 0, más probable la convergencia a un espurio.
2. **Capacidad**: ~`0.15 · N` patrones máximo (con `N = 25` da ~3-4 patrones).
3. **Estados espurios**: la función de energía tiene otros mínimos además de los patrones almacenados. La red puede converger a esos.
4. **Ciclos**: con actualización síncrona se puede caer en un ciclo de período 2 (o más) entre dos estados.

## Referencias

- `docs/clases/hopfield/hopfield.VTT` — clase teórica de Euge. Algoritmo, fórmula de pesos, función de energía, demostración de que la energía decrece, limitaciones.
- `docs/clases/hopfield/hopfield_ortogonalidad_letras.VTT` — clase de Santi. Análisis de ortogonalidad sobre el abecedario, por qué preferir `|<,>| medio` menor, por qué mirar también el máximo.
- `docs/clases/hopfield/ortogonalidad/` — screenshots del notebook de Santi que replicamos en `ortogonalidad_letras.ipynb`.
- `docs/consigna.pdf` — enunciado del TP, ejercicio 2 (Hopfield).
