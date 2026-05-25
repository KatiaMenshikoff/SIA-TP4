# Capacidad p=5

```
p=5
grupo=GMPVZ
|<,>| medio=2.200
```

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — almacenados como input

Esperamos punto fijo en 1 iteración. Si alguno NO es estable, ya excedimos la capacidad incluso sin ruido.

| letra   |   iters | motivo   | outcome   | es_fijo   |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:----------|:----------|----------------:|------------------:|----------------:|
| G       |       1 | stable   | TP        | True      |               0 |            -10.24 |          -10.24 |
| M       |       1 | stable   | TP        | True      |               0 |            -10.88 |          -10.88 |
| P       |       1 | stable   | TP        | True      |               0 |            -10.24 |          -10.24 |
| V       |       1 | stable   | TP        | True      |               0 |            -10.72 |          -10.72 |
| Z       |       1 | stable   | TP        | True      |               0 |            -10.56 |          -10.56 |

### G (almacenada)

![exp1 G](plots/exp1_G.png)

### M (almacenada)

![exp1 M](plots/exp1_M.png)

### P (almacenada)

![exp1 P](plots/exp1_P.png)

### V (almacenada)

![exp1 V](plots/exp1_V.png)

### Z (almacenada)

![exp1 Z](plots/exp1_Z.png)

## Experimento 2 — ruido 10%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| G       |       2 | stable   | G             | TP        |                 1 |               0 |             -8.32 |          -10.24 |
| M       |       2 | stable   | M             | TP        |                 2 |               0 |             -7.2  |          -10.88 |
| P       |       2 | stable   | P             | TP        |                 1 |               0 |             -8.8  |          -10.24 |
| V       |       1 | stable   | V             | TP        |                 0 |               0 |            -10.72 |          -10.72 |
| Z       |       2 | stable   | Z             | TP        |                 2 |               0 |             -7.68 |          -10.56 |

### G con ruido 10% → TP (G)

![exp2 G n10](plots/exp2_G_n10.png)

![energía G n10](plots/energy_exp2_n10_G.png) ![estados G n10](plots/states_exp2_n10_G.png)

### M con ruido 10% → TP (M)

![exp2 M n10](plots/exp2_M_n10.png)

![energía M n10](plots/energy_exp2_n10_M.png) ![estados M n10](plots/states_exp2_n10_M.png)

### P con ruido 10% → TP (P)

![exp2 P n10](plots/exp2_P_n10.png)

![energía P n10](plots/energy_exp2_n10_P.png) ![estados P n10](plots/states_exp2_n10_P.png)

### V con ruido 10% → TP (V)

![exp2 V n10](plots/exp2_V_n10.png)

![energía V n10](plots/energy_exp2_n10_V.png) ![estados V n10](plots/states_exp2_n10_V.png)

### Z con ruido 10% → TP (Z)

![exp2 Z n10](plots/exp2_Z_n10.png)

![energía Z n10](plots/energy_exp2_n10_Z.png) ![estados Z n10](plots/states_exp2_n10_Z.png)

## Experimento 2 — ruido 20%

Una muestra determinística por letra (seed=1).

| letra   |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| G       |       2 | stable   | G             | TP        |                 5 |               0 |             -2.56 |          -10.24 |
| M       |       6 | stable   | nan           | Espurio   |                 6 |               5 |             -3.2  |           -9.92 |
| P       |       2 | stable   | P             | TP        |                 4 |               0 |             -3.84 |          -10.24 |
| V       |       3 | stable   | V             | TP        |                 4 |               0 |             -4.8  |          -10.72 |
| Z       |       3 | stable   | Z             | TP        |                 8 |               0 |              0.16 |          -10.56 |

### G con ruido 20% → TP (G)

![exp2 G n20](plots/exp2_G_n20.png)

![energía G n20](plots/energy_exp2_n20_G.png) ![estados G n20](plots/states_exp2_n20_G.png)

### M con ruido 20% → Espurio

![exp2 M n20](plots/exp2_M_n20.png)

![energía M n20](plots/energy_exp2_n20_M.png) ![estados M n20](plots/states_exp2_n20_M.png)

### P con ruido 20% → TP (P)

![exp2 P n20](plots/exp2_P_n20.png)

![energía P n20](plots/energy_exp2_n20_P.png) ![estados P n20](plots/states_exp2_n20_P.png)

### V con ruido 20% → TP (V)

![exp2 V n20](plots/exp2_V_n20.png)

![energía V n20](plots/energy_exp2_n20_V.png) ![estados V n20](plots/states_exp2_n20_V.png)

### Z con ruido 20% → TP (Z)

![exp2 Z n20](plots/exp2_Z_n20.png)

![energía Z n20](plots/energy_exp2_n20_Z.png) ![estados Z n20](plots/states_exp2_n20_Z.png)
