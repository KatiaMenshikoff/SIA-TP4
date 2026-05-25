# Grupo JLRX

Letras almacenadas: **J, L, R, X**

Convención del overlay: verde claro = match `+1↔+1`, blanco = match `-1↔-1`, rojo = mismatch.

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — Patrones almacenados como input

Esperamos que cada patrón almacenado sea un punto fijo (convergencia en 1 iteración a sí mismo).

| letra   |   iters | motivo   | convergio_a   | outcome   | es_fijo   |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|:----------|------------------:|----------------:|
| J       |       1 | stable   | J             | TP        | True      |            -10.72 |          -10.72 |
| L       |       1 | stable   | L             | TP        | True      |            -10.72 |          -10.72 |
| R       |       1 | stable   | R             | TP        | True      |            -10.88 |          -10.88 |
| X       |       1 | stable   | X             | TP        | True      |            -10.56 |          -10.56 |

### J (almacenada)

![exp1 J](plots/exp1_J.png)

### L (almacenada)

![exp1 L](plots/exp1_L.png)

### R (almacenada)

![exp1 R](plots/exp1_R.png)

### X (almacenada)

![exp1 X](plots/exp1_X.png)

## Experimento 2 — Patrones almacenados con ruido

Niveles: 10%, 20%, 65%. Una muestra determinística por nivel (seed=1).

| letra_objetivo   |   ruido |   seed |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:-----------------|--------:|-------:|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| J                |    0.1  |      1 |       2 | stable   | J             | TP        |                 1 |               0 |             -9.12 |          -10.72 |
| J                |    0.2  |      1 |       2 | stable   | J             | TP        |                 5 |               0 |             -2.72 |          -10.72 |
| J                |    0.65 |      1 |       2 | stable   | R             | FP        |                14 |              11 |             -0.64 |          -10.88 |
| L                |    0.1  |      1 |       2 | stable   | L             | TP        |                 3 |               0 |             -5.6  |          -10.72 |
| L                |    0.2  |      1 |       2 | stable   | L             | TP        |                 3 |               0 |             -5.76 |          -10.72 |
| L                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                17 |              25 |              0.16 |          -10.72 |
| R                |    0.1  |      1 |       1 | stable   | R             | TP        |                 0 |               0 |            -10.88 |          -10.88 |
| R                |    0.2  |      1 |       2 | stable   | R             | TP        |                 4 |               0 |             -4.8  |          -10.88 |
| R                |    0.65 |      1 |       7 | stable   | nan           | Espurio   |                17 |              14 |             -2.56 |          -10.72 |
| X                |    0.1  |      1 |       2 | stable   | X             | TP        |                 4 |               0 |             -4.48 |          -10.56 |
| X                |    0.2  |      1 |       2 | stable   | nan           | Espurio   |                 8 |               7 |             -2.24 |           -8.32 |
| X                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                16 |              25 |              0.64 |          -10.56 |

### J con ruido 10% → TP (J)

![exp2 J n10](plots/exp2_J_n10.png)

![energía exp2 J n10](plots/energy_exp2_n10_J.png) ![estados exp2 J n10](plots/states_exp2_n10_J.png)

### J con ruido 20% → TP (J)

![exp2 J n20](plots/exp2_J_n20.png)

![energía exp2 J n20](plots/energy_exp2_n20_J.png) ![estados exp2 J n20](plots/states_exp2_n20_J.png)

### J con ruido 65% → FP (R)

![exp2 J n65](plots/exp2_J_n65.png)

![energía exp2 J n65](plots/energy_exp2_n65_J.png) ![estados exp2 J n65](plots/states_exp2_n65_J.png)

### L con ruido 10% → TP (L)

![exp2 L n10](plots/exp2_L_n10.png)

![energía exp2 L n10](plots/energy_exp2_n10_L.png) ![estados exp2 L n10](plots/states_exp2_n10_L.png)

### L con ruido 20% → TP (L)

![exp2 L n20](plots/exp2_L_n20.png)

![energía exp2 L n20](plots/energy_exp2_n20_L.png) ![estados exp2 L n20](plots/states_exp2_n20_L.png)

### L con ruido 65% → Espurio

![exp2 L n65](plots/exp2_L_n65.png)

![energía exp2 L n65](plots/energy_exp2_n65_L.png) ![estados exp2 L n65](plots/states_exp2_n65_L.png)

### R con ruido 10% → TP (R)

![exp2 R n10](plots/exp2_R_n10.png)

![energía exp2 R n10](plots/energy_exp2_n10_R.png) ![estados exp2 R n10](plots/states_exp2_n10_R.png)

### R con ruido 20% → TP (R)

![exp2 R n20](plots/exp2_R_n20.png)

![energía exp2 R n20](plots/energy_exp2_n20_R.png) ![estados exp2 R n20](plots/states_exp2_n20_R.png)

### R con ruido 65% → Espurio

![exp2 R n65](plots/exp2_R_n65.png)

![energía exp2 R n65](plots/energy_exp2_n65_R.png) ![estados exp2 R n65](plots/states_exp2_n65_R.png)

### X con ruido 10% → TP (X)

![exp2 X n10](plots/exp2_X_n10.png)

![energía exp2 X n10](plots/energy_exp2_n10_X.png) ![estados exp2 X n10](plots/states_exp2_n10_X.png)

### X con ruido 20% → Espurio

![exp2 X n20](plots/exp2_X_n20.png)

![energía exp2 X n20](plots/energy_exp2_n20_X.png) ![estados exp2 X n20](plots/states_exp2_n20_X.png)

### X con ruido 65% → Espurio

![exp2 X n65](plots/exp2_X_n65.png)

![energía exp2 X n65](plots/energy_exp2_n65_X.png) ![estados exp2 X n65](plots/states_exp2_n65_X.png)

## Experimento 3 — Letras no almacenadas

Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados (similares), 3 con menor (distintas).

| letra_query   | tipo     |   max_inner_product | mas_parecida_a   |   iters | motivo   | convergio_a   | outcome         |   energia_inicial |   energia_final |
|:--------------|:---------|--------------------:|:-----------------|--------:|:---------|:--------------|:----------------|------------------:|----------------:|
| P             | similar  |                  21 | R                |       2 | stable   | R             | MatchAlmacenado |             -7.68 |          -10.88 |
| A             | similar  |                  17 | R                |       3 | stable   | R             | MatchAlmacenado |             -5.92 |          -10.88 |
| S             | distinta |                   7 | X                |       5 | stable   | nan           | Espurio         |              0.32 |          -10.56 |
| I             | distinta |                   5 | J                |       5 | stable   | J             | MatchAlmacenado |              0.96 |          -10.72 |
| V             | distinta |                   5 | L                |       6 | stable   | nan           | Espurio         |              0.96 |           -8.16 |

### P (similar, max_ip=21 con R) → MatchAlmacenado (R)

![exp3 P](plots/exp3_P.png)

![energía exp3 P](plots/energy_exp3_P.png) ![estados exp3 P](plots/states_exp3_P.png)

### A (similar, max_ip=17 con R) → MatchAlmacenado (R)

![exp3 A](plots/exp3_A.png)

![energía exp3 A](plots/energy_exp3_A.png) ![estados exp3 A](plots/states_exp3_A.png)

### S (distinta, max_ip=7 con X) → Espurio

![exp3 S](plots/exp3_S.png)

![energía exp3 S](plots/energy_exp3_S.png) ![estados exp3 S](plots/states_exp3_S.png)

### I (distinta, max_ip=5 con J) → MatchAlmacenado (J)

![exp3 I](plots/exp3_I.png)

![energía exp3 I](plots/energy_exp3_I.png) ![estados exp3 I](plots/states_exp3_I.png)

### V (distinta, max_ip=5 con L) → Espurio

![exp3 V](plots/exp3_V.png)

![energía exp3 V](plots/energy_exp3_V.png) ![estados exp3 V](plots/states_exp3_V.png)
