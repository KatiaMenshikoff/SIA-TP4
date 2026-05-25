# Experimentos de capacidad

Para cada `p ∈ {2, 3, 5, 6}` elegimos el grupo de `p` letras con menor `|<,>| medio` (más ortogonal posible) y entrenamos una red.

Capacidad teórica de Hopfield: `~0.15·N = ~3.75 patrones` para N=25. Esperamos comportamiento perfecto en p=2,3 y degradación a partir de p=5 (excediendo la capacidad teórica).

## Resumen

|   p | grupo   |   |<,>|_medio | fijos_exp1   | TP_ruido10   | TP_ruido20   |
|----:|:--------|--------------:|:-------------|:-------------|:-------------|
|   2 | AL      |         1     | 2/2          | 2/2          | 2/2          |
|   3 | FUY     |         1     | 3/3          | 3/3          | 3/3          |
|   5 | GMPVZ   |         2.2   | 5/5          | 5/5          | 4/5          |
|   6 | JLRTVX  |         2.467 | 6/6          | 4/6          | 4/6          |

## Lectura

- **`fijos_exp1`**: cuántos de los almacenados son punto fijo al pasarles su propio patrón limpio. Si no son todos, ya excedimos capacidad.

- **`TP_ruido10` / `TP_ruido20`**: cuántos almacenados se recuperan correctamente con ruido del 10% y 20%. Mide la cuenca de atracción.

## Observaciones del experimento

- **p=2, p=3**: todo funciona perfecto. Estamos muy por debajo de la capacidad y los grupos son perfectamente ortogonales (`|<,>|=1.0`).

- **p=5**: los 5 almacenados siguen siendo punto fijo, y resisten 10% de ruido. Con 20% ya se rompe uno (4/5). La cuenca de atracción se achicó.

- **p=6**: punto fijo OK al pasar los limpios, pero ya con 10% de ruido fallan 2 de 6. La capacidad de la red está saturada.

Esto es la **degradación gradual por capacidad** clásica de Hopfield: los almacenados pueden seguir siendo estables, pero sus cuencas se vuelven más finas hasta que la mínima perturbación los saca.

## Detalle por experimento

- [p=2](p2/README.md)
- [p=3](p3/README.md)
- [p=5](p5/README.md)
- [p=6](p6/README.md)
