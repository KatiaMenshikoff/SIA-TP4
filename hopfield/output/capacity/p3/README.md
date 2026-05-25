# Capacidad p=3

```
p=3
grupo=FUY
|<,>| medio=1.000
```

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — almacenados como input

Esperamos punto fijo en 1 iteración. Si alguno NO es estable, ya excedimos la capacidad incluso sin ruido.

| letra   |   iters | motivo   | outcome   | es_fijo   |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:----------|:----------|----------------:|------------------:|----------------:|
| F       |       1 | stable   | TP        | True      |               0 |            -11.04 |          -11.04 |
| U       |       1 | stable   | TP        | True      |               0 |            -11.04 |          -11.04 |
| Y       |       1 | stable   | TP        | True      |               0 |            -11.04 |          -11.04 |

### F (almacenada)

![exp1 F](plots/exp1_F.png)

### U (almacenada)

![exp1 U](plots/exp1_U.png)

### Y (almacenada)

![exp1 Y](plots/exp1_Y.png)

## Experimento 2 — ruido 10%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| F       |       2 | stable   | F             | TP        |                 1 |               0 |             -9.28 |          -11.04 |
| U       |       2 | stable   | U             | TP        |                 2 |               0 |             -7.36 |          -11.04 |
| Y       |       2 | stable   | Y             | TP        |                 1 |               0 |             -9.12 |          -11.04 |

### F con ruido 10% → TP (F)

![exp2 F n10](plots/exp2_F_n10.png)

![energía F n10](plots/energy_exp2_n10_F.png) ![estados F n10](plots/states_exp2_n10_F.png)

### U con ruido 10% → TP (U)

![exp2 U n10](plots/exp2_U_n10.png)

![energía U n10](plots/energy_exp2_n10_U.png) ![estados U n10](plots/states_exp2_n10_U.png)

### Y con ruido 10% → TP (Y)

![exp2 Y n10](plots/exp2_Y_n10.png)

![energía Y n10](plots/energy_exp2_n10_Y.png) ![estados Y n10](plots/states_exp2_n10_Y.png)

## Experimento 2 — ruido 20%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| F       |       2 | stable   | F             | TP        |                 5 |               0 |             -3.52 |          -11.04 |
| U       |       2 | stable   | U             | TP        |                 6 |               0 |             -2.4  |          -11.04 |
| Y       |       2 | stable   | Y             | TP        |                 4 |               0 |             -4.48 |          -11.04 |

### F con ruido 20% → TP (F)

![exp2 F n20](plots/exp2_F_n20.png)

![energía F n20](plots/energy_exp2_n20_F.png) ![estados F n20](plots/states_exp2_n20_F.png)

### U con ruido 20% → TP (U)

![exp2 U n20](plots/exp2_U_n20.png)

![energía U n20](plots/energy_exp2_n20_U.png) ![estados U n20](plots/states_exp2_n20_U.png)

### Y con ruido 20% → TP (Y)

![exp2 Y n20](plots/exp2_Y_n20.png)

![energía Y n20](plots/energy_exp2_n20_Y.png) ![estados Y n20](plots/states_exp2_n20_Y.png)
