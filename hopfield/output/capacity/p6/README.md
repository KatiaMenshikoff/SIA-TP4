# Capacidad p=6

```
p=6
grupo=JLRTVX
|<,>| medio=2.467
```

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — almacenados como input

Esperamos punto fijo en 1 iteración. Si alguno NO es estable, ya excedimos la capacidad incluso sin ruido.

| letra   |   iters | motivo   | outcome   | es_fijo   |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:----------|:----------|----------------:|------------------:|----------------:|
| J       |       1 | stable   | TP        | True      |               0 |            -11.36 |          -11.36 |
| L       |       1 | stable   | TP        | True      |               0 |            -10.4  |          -10.4  |
| R       |       1 | stable   | TP        | True      |               0 |             -9.92 |           -9.92 |
| T       |       1 | stable   | TP        | True      |               0 |            -11.36 |          -11.36 |
| V       |       1 | stable   | TP        | True      |               0 |            -10.56 |          -10.56 |
| X       |       1 | stable   | TP        | True      |               0 |            -10.08 |          -10.08 |

### J (almacenada)

![exp1 J](plots/exp1_J.png)

### L (almacenada)

![exp1 L](plots/exp1_L.png)

### R (almacenada)

![exp1 R](plots/exp1_R.png)

### T (almacenada)

![exp1 T](plots/exp1_T.png)

### V (almacenada)

![exp1 V](plots/exp1_V.png)

### X (almacenada)

![exp1 X](plots/exp1_X.png)

## Experimento 2 — ruido 10%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| J       |       2 | stable   | J             | TP        |                 1 |               0 |             -9.28 |          -11.36 |
| L       |       2 | stable   | L             | TP        |                 2 |               0 |             -6.24 |          -10.4  |
| R       |       2 | stable   | R             | TP        |                 1 |               0 |             -8.64 |           -9.92 |
| T       |       1 | stable   | T             | TP        |                 0 |               0 |            -11.36 |          -11.36 |
| V       |       2 | stable   | nan           | Espurio   |                 2 |               2 |             -7.84 |          -10.08 |
| X       |       5 | stable   | J             | FP        |                 6 |              12 |             -3.68 |          -11.36 |

### J con ruido 10% → TP (J)

![exp2 J n10](plots/exp2_J_n10.png)

![energía J n10](plots/energy_exp2_n10_J.png) ![estados J n10](plots/states_exp2_n10_J.png)

### L con ruido 10% → TP (L)

![exp2 L n10](plots/exp2_L_n10.png)

![energía L n10](plots/energy_exp2_n10_L.png) ![estados L n10](plots/states_exp2_n10_L.png)

### R con ruido 10% → TP (R)

![exp2 R n10](plots/exp2_R_n10.png)

![energía R n10](plots/energy_exp2_n10_R.png) ![estados R n10](plots/states_exp2_n10_R.png)

### T con ruido 10% → TP (T)

![exp2 T n10](plots/exp2_T_n10.png)

![energía T n10](plots/energy_exp2_n10_T.png) ![estados T n10](plots/states_exp2_n10_T.png)

### V con ruido 10% → Espurio

![exp2 V n10](plots/exp2_V_n10.png)

![energía V n10](plots/energy_exp2_n10_V.png) ![estados V n10](plots/states_exp2_n10_V.png)

### X con ruido 10% → FP (J)

![exp2 X n10](plots/exp2_X_n10.png)

![energía X n10](plots/energy_exp2_n10_X.png) ![estados X n10](plots/states_exp2_n10_X.png)

## Experimento 2 — ruido 20%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| J       |       2 | stable   | J             | TP        |                 5 |               0 |             -1.76 |          -11.36 |
| L       |       6 | stable   | L             | TP        |                 6 |               0 |             -3.04 |          -10.4  |
| R       |       2 | stable   | R             | TP        |                 4 |               0 |             -3.36 |           -9.92 |
| T       |       2 | stable   | T             | TP        |                 4 |               0 |             -3.68 |          -11.36 |
| V       |       5 | cycle    | nan           | Ciclo     |                 8 |               9 |             -0.64 |          -10.4  |
| X       |       8 | cycle    | nan           | Ciclo     |                10 |              11 |              2.08 |          -10.4  |

### J con ruido 20% → TP (J)

![exp2 J n20](plots/exp2_J_n20.png)

![energía J n20](plots/energy_exp2_n20_J.png) ![estados J n20](plots/states_exp2_n20_J.png)

### L con ruido 20% → TP (L)

![exp2 L n20](plots/exp2_L_n20.png)

![energía L n20](plots/energy_exp2_n20_L.png) ![estados L n20](plots/states_exp2_n20_L.png)

### R con ruido 20% → TP (R)

![exp2 R n20](plots/exp2_R_n20.png)

![energía R n20](plots/energy_exp2_n20_R.png) ![estados R n20](plots/states_exp2_n20_R.png)

### T con ruido 20% → TP (T)

![exp2 T n20](plots/exp2_T_n20.png)

![energía T n20](plots/energy_exp2_n20_T.png) ![estados T n20](plots/states_exp2_n20_T.png)

### V con ruido 20% → Ciclo

![exp2 V n20](plots/exp2_V_n20.png)

![energía V n20](plots/energy_exp2_n20_V.png) ![estados V n20](plots/states_exp2_n20_V.png)

### X con ruido 20% → Ciclo

![exp2 X n20](plots/exp2_X_n20.png)

![energía X n20](plots/energy_exp2_n20_X.png) ![estados X n20](plots/states_exp2_n20_X.png)
