# Grupo AJKU
| 2.00 | ('A', 'J', 'K', 'U') |
| ---- | -------------------- |

Letras almacenadas: **A, J, K, U**

Convención del overlay: verde claro = match `+1↔+1`, blanco = match `-1↔-1`, rojo = mismatch.

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — Patrones almacenados como input

Esperamos que cada patrón almacenado sea un punto fijo (convergencia en 1 iteración a sí mismo).

| letra   |   iters | motivo   | convergio_a   | outcome   | es_fijo   |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|:----------|------------------:|----------------:|
| A       |       1 | stable   | A             | TP        | True      |            -11.2  |          -11.2  |
| J       |       1 | stable   | J             | TP        | True      |            -11.04 |          -11.04 |
| K       |       1 | stable   | K             | TP        | True      |            -10.72 |          -10.72 |
| U       |       1 | stable   | U             | TP        | True      |            -10.56 |          -10.56 |

### A (almacenada)

![exp1 A](plots/exp1_A.png)

### J (almacenada)

![exp1 J](plots/exp1_J.png)

### K (almacenada)

![exp1 K](plots/exp1_K.png)

### U (almacenada)

![exp1 U](plots/exp1_U.png)

## Experimento 2 — Patrones almacenados con ruido

Niveles: 10%, 20%, 65%. Una muestra determinística por nivel (seed=1).

| letra_objetivo   |   ruido |   seed |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:-----------------|--------:|-------:|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| A                |    0.1  |      1 |       2 | stable   | A             | TP        |                 1 |               0 |             -9.44 |          -11.2  |
| A                |    0.2  |      1 |       2 | stable   | A             | TP        |                 5 |               0 |             -3.52 |          -11.2  |
| A                |    0.65 |      1 |       2 | stable   | nan           | Espurio   |                14 |              14 |             -1.92 |          -10.72 |
| J                |    0.1  |      1 |       2 | stable   | J             | TP        |                 3 |               0 |             -5.44 |          -11.04 |
| J                |    0.2  |      1 |       2 | stable   | J             | TP        |                 3 |               0 |             -6.72 |          -11.04 |
| J                |    0.65 |      1 |       4 | stable   | nan           | Espurio   |                17 |              25 |             -0.32 |          -11.04 |
| K                |    0.1  |      1 |       1 | stable   | K             | TP        |                 0 |               0 |            -10.72 |          -10.72 |
| K                |    0.2  |      1 |       4 | stable   | K             | TP        |                 4 |               0 |             -5.44 |          -10.72 |
| K                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                17 |              25 |             -1.12 |          -10.72 |
| U                |    0.1  |      1 |       2 | stable   | U             | TP        |                 4 |               0 |             -3.84 |          -10.56 |
| U                |    0.2  |      1 |       3 | stable   | nan           | Espurio   |                 8 |               9 |             -3.04 |           -8.8  |
| U                |    0.65 |      1 |       5 | stable   | nan           | Espurio   |                16 |              18 |             -0.64 |          -10.4  |

### A con ruido 10% → TP (A)

![exp2 A n10](plots/exp2_A_n10.png)

![energía exp2 A n10](plots/energy_exp2_n10_A.png) ![estados exp2 A n10](plots/states_exp2_n10_A.png)

### A con ruido 20% → TP (A)

![exp2 A n20](plots/exp2_A_n20.png)

![energía exp2 A n20](plots/energy_exp2_n20_A.png) ![estados exp2 A n20](plots/states_exp2_n20_A.png)

### A con ruido 65% → Espurio

![exp2 A n65](plots/exp2_A_n65.png)

![energía exp2 A n65](plots/energy_exp2_n65_A.png) ![estados exp2 A n65](plots/states_exp2_n65_A.png)

### J con ruido 10% → TP (J)

![exp2 J n10](plots/exp2_J_n10.png)

![energía exp2 J n10](plots/energy_exp2_n10_J.png) ![estados exp2 J n10](plots/states_exp2_n10_J.png)

### J con ruido 20% → TP (J)

![exp2 J n20](plots/exp2_J_n20.png)

![energía exp2 J n20](plots/energy_exp2_n20_J.png) ![estados exp2 J n20](plots/states_exp2_n20_J.png)

### J con ruido 65% → Espurio

![exp2 J n65](plots/exp2_J_n65.png)

![energía exp2 J n65](plots/energy_exp2_n65_J.png) ![estados exp2 J n65](plots/states_exp2_n65_J.png)

### K con ruido 10% → TP (K)

![exp2 K n10](plots/exp2_K_n10.png)

![energía exp2 K n10](plots/energy_exp2_n10_K.png) ![estados exp2 K n10](plots/states_exp2_n10_K.png)

### K con ruido 20% → TP (K)

![exp2 K n20](plots/exp2_K_n20.png)

![energía exp2 K n20](plots/energy_exp2_n20_K.png) ![estados exp2 K n20](plots/states_exp2_n20_K.png)

### K con ruido 65% → Espurio

![exp2 K n65](plots/exp2_K_n65.png)

![energía exp2 K n65](plots/energy_exp2_n65_K.png) ![estados exp2 K n65](plots/states_exp2_n65_K.png)

### U con ruido 10% → TP (U)

![exp2 U n10](plots/exp2_U_n10.png)

![energía exp2 U n10](plots/energy_exp2_n10_U.png) ![estados exp2 U n10](plots/states_exp2_n10_U.png)

### U con ruido 20% → Espurio

![exp2 U n20](plots/exp2_U_n20.png)

![energía exp2 U n20](plots/energy_exp2_n20_U.png) ![estados exp2 U n20](plots/states_exp2_n20_U.png)

### U con ruido 65% → Espurio

![exp2 U n65](plots/exp2_U_n65.png)

![energía exp2 U n65](plots/energy_exp2_n65_U.png) ![estados exp2 U n65](plots/states_exp2_n65_U.png)

## Experimento 3 — Letras no almacenadas

Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados (similares), 3 con menor (distintas).

| letra_query   | tipo     |   max_inner_product | mas_parecida_a   |   iters | motivo   | convergio_a   | outcome         |   energia_inicial |   energia_final |
|:--------------|:---------|--------------------:|:-----------------|--------:|:---------|:--------------|:----------------|------------------:|----------------:|
| P             | similar  |                  17 | A                |       2 | stable   | A             | MatchAlmacenado |             -4.96 |          -11.2  |
| R             | similar  |                  17 | A                |       3 | stable   | A             | MatchAlmacenado |             -6.88 |          -11.2  |
| Z             | distinta |                   9 | J                |       4 | stable   | J             | MatchAlmacenado |             -0.32 |          -11.04 |
| S             | distinta |                   7 | A                |       4 | stable   | A             | MatchAlmacenado |              0.32 |          -11.2  |
| I             | distinta |                   5 | A                |       3 | stable   | nan           | Espurio         |              0.64 |          -10.56 |

### P (similar, max_ip=17 con A) → MatchAlmacenado (A)

![exp3 P](plots/exp3_P.png)

![energía exp3 P](plots/energy_exp3_P.png) ![estados exp3 P](plots/states_exp3_P.png)

### R (similar, max_ip=17 con A) → MatchAlmacenado (A)

![exp3 R](plots/exp3_R.png)

![energía exp3 R](plots/energy_exp3_R.png) ![estados exp3 R](plots/states_exp3_R.png)

### Z (distinta, max_ip=9 con J) → MatchAlmacenado (J)

![exp3 Z](plots/exp3_Z.png)

![energía exp3 Z](plots/energy_exp3_Z.png) ![estados exp3 Z](plots/states_exp3_Z.png)

### S (distinta, max_ip=7 con A) → MatchAlmacenado (A)

![exp3 S](plots/exp3_S.png)

![energía exp3 S](plots/energy_exp3_S.png) ![estados exp3 S](plots/states_exp3_S.png)

### I (distinta, max_ip=5 con A) → Espurio

![exp3 I](plots/exp3_I.png)

![energía exp3 I](plots/energy_exp3_I.png) ![estados exp3 I](plots/states_exp3_I.png)
