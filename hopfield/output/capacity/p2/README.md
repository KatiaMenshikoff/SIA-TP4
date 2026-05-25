# Capacidad p=2

```
p=2
grupo=AL
|<,>| medio=1.000
```

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — almacenados como input

Esperamos punto fijo en 1 iteración. Si alguno NO es estable, ya excedimos la capacidad incluso sin ruido.

| letra   |   iters | motivo   | outcome   | es_fijo   |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:----------|:----------|----------------:|------------------:|----------------:|
| A       |       1 | stable   | TP        | True      |               0 |            -11.52 |          -11.52 |
| L       |       1 | stable   | TP        | True      |               0 |            -11.52 |          -11.52 |

### A (almacenada)

![exp1 A](plots/exp1_A.png)

### L (almacenada)

![exp1 L](plots/exp1_L.png)

## Experimento 2 — ruido 10%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| A       |       2 | stable   | A             | TP        |                 1 |               0 |             -9.6  |          -11.52 |
| L       |       2 | stable   | L             | TP        |                 2 |               0 |             -7.84 |          -11.52 |

### A con ruido 10% → TP (A)

![exp2 A n10](plots/exp2_A_n10.png)

![energía A n10](plots/energy_exp2_n10_A.png) ![estados A n10](plots/states_exp2_n10_A.png)

### L con ruido 10% → TP (L)

![exp2 L n10](plots/exp2_L_n10.png)

![energía L n10](plots/energy_exp2_n10_L.png) ![estados L n10](plots/states_exp2_n10_L.png)

## Experimento 2 — ruido 20%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| A       |       2 | stable   | A             | TP        |                 5 |               0 |              -4   |          -11.52 |
| L       |       2 | stable   | L             | TP        |                 6 |               0 |              -2.4 |          -11.52 |

### A con ruido 20% → TP (A)

![exp2 A n20](plots/exp2_A_n20.png)

![energía A n20](plots/energy_exp2_n20_A.png) ![estados A n20](plots/states_exp2_n20_A.png)

### L con ruido 20% → TP (L)

![exp2 L n20](plots/exp2_L_n20.png)

![energía L n20](plots/energy_exp2_n20_L.png) ![estados L n20](plots/states_exp2_n20_L.png)
