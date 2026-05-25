# Grupo GRTV

Letras almacenadas: **G, R, T, V**

Convención del overlay: verde claro = match `+1↔+1`, blanco = match `-1↔-1`, rojo = mismatch.

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — Patrones almacenados como input

Esperamos que cada patrón almacenado sea un punto fijo (convergencia en 1 iteración a sí mismo).

| letra | iters | motivo | convergio_a | outcome | es_fijo | energia_inicial | energia_final |
| :---- | ----: | :----- | :---------- | :------ | :------ | --------------: | ------------: |
| G     |     1 | stable | G           | TP      | True    |          -10.56 |        -10.56 |
| R     |     1 | stable | R           | TP      | True    |          -10.56 |        -10.56 |
| T     |     1 | stable | T           | TP      | True    |          -10.56 |        -10.56 |
| V     |     1 | stable | V           | TP      | True    |          -10.56 |        -10.56 |

### G (almacenada)

![exp1 G](plots/exp1_G.png)

### R (almacenada)

![exp1 R](plots/exp1_R.png)

### T (almacenada)

![exp1 T](plots/exp1_T.png)

### V (almacenada)

![exp1 V](plots/exp1_V.png)

## Experimento 2 — Patrones almacenados con ruido

Niveles: 10%, 20%, 65%. Una muestra determinística por nivel (seed=1).

| letra_objetivo   |   ruido |   seed |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:-----------------|--------:|-------:|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| G                |    0.1  |      1 |       2 | stable   | G             | TP        |                 1 |               0 |             -8.96 |          -10.56 |
| G                |    0.2  |      1 |       2 | stable   | G             | TP        |                 5 |               0 |             -3.04 |          -10.56 |
| G                |    0.65 |      1 |       4 | stable   | nan           | Espurio   |                14 |              25 |              1.6  |          -10.56 |
| R                |    0.1  |      1 |       2 | stable   | R             | TP        |                 3 |               0 |             -6.4  |          -10.56 |
| R                |    0.2  |      1 |       2 | stable   | R             | TP        |                 3 |               0 |             -5.76 |          -10.56 |
| R                |    0.65 |      1 |       5 | stable   | nan           | Espurio   |                17 |              12 |             -0.64 |          -10.56 |
| T                |    0.1  |      1 |       1 | stable   | T             | TP        |                 0 |               0 |            -10.56 |          -10.56 |
| T                |    0.2  |      1 |       2 | stable   | T             | TP        |                 4 |               0 |             -4.32 |          -10.56 |
| T                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                17 |              25 |             -0.48 |          -10.56 |
| V                |    0.1  |      1 |       3 | stable   | V             | TP        |                 4 |               0 |             -4.96 |          -10.56 |
| V                |    0.2  |      1 |       3 | stable   | V             | TP        |                 8 |               0 |             -0.8  |          -10.56 |
| V                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                16 |              12 |             -1.76 |          -10.56 |

### G con ruido 10% → TP (G)

![exp2 G n10](plots/exp2_G_n10.png)

![energía exp2 G n10](plots/energy_exp2_n10_G.png) ![estados exp2 G n10](plots/states_exp2_n10_G.png)

### G con ruido 20% → TP (G)

![exp2 G n20](plots/exp2_G_n20.png)

![energía exp2 G n20](plots/energy_exp2_n20_G.png) ![estados exp2 G n20](plots/states_exp2_n20_G.png)

### G con ruido 65% → Espurio

![exp2 G n65](plots/exp2_G_n65.png)

![energía exp2 G n65](plots/energy_exp2_n65_G.png) ![estados exp2 G n65](plots/states_exp2_n65_G.png)

### R con ruido 10% → TP (R)

![exp2 R n10](plots/exp2_R_n10.png)

![energía exp2 R n10](plots/energy_exp2_n10_R.png) ![estados exp2 R n10](plots/states_exp2_n10_R.png)

### R con ruido 20% → TP (R)

![exp2 R n20](plots/exp2_R_n20.png)

![energía exp2 R n20](plots/energy_exp2_n20_R.png) ![estados exp2 R n20](plots/states_exp2_n20_R.png)

### R con ruido 65% → Espurio

![exp2 R n65](plots/exp2_R_n65.png)

![energía exp2 R n65](plots/energy_exp2_n65_R.png) ![estados exp2 R n65](plots/states_exp2_n65_R.png)

### T con ruido 10% → TP (T)

![exp2 T n10](plots/exp2_T_n10.png)

![energía exp2 T n10](plots/energy_exp2_n10_T.png) ![estados exp2 T n10](plots/states_exp2_n10_T.png)

### T con ruido 20% → TP (T)

![exp2 T n20](plots/exp2_T_n20.png)

![energía exp2 T n20](plots/energy_exp2_n20_T.png) ![estados exp2 T n20](plots/states_exp2_n20_T.png)

### T con ruido 65% → Espurio

![exp2 T n65](plots/exp2_T_n65.png)

![energía exp2 T n65](plots/energy_exp2_n65_T.png) ![estados exp2 T n65](plots/states_exp2_n65_T.png)

### V con ruido 10% → TP (V)

![exp2 V n10](plots/exp2_V_n10.png)

![energía exp2 V n10](plots/energy_exp2_n10_V.png) ![estados exp2 V n10](plots/states_exp2_n10_V.png)

### V con ruido 20% → TP (V)

![exp2 V n20](plots/exp2_V_n20.png)

![energía exp2 V n20](plots/energy_exp2_n20_V.png) ![estados exp2 V n20](plots/states_exp2_n20_V.png)

### V con ruido 65% → Espurio

![exp2 V n65](plots/exp2_V_n65.png)

![energía exp2 V n65](plots/energy_exp2_n65_V.png) ![estados exp2 V n65](plots/states_exp2_n65_V.png)

## Experimento 3 — Letras no almacenadas

Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados (similares), 3 con menor (distintas).

| letra_query   | tipo     |   max_inner_product | mas_parecida_a   |   iters | motivo   | convergio_a   | outcome         |   energia_inicial |   energia_final |
|:--------------|:---------|--------------------:|:-----------------|--------:|:---------|:--------------|:----------------|------------------:|----------------:|
| P             | similar  |                  21 | R                |       2 | stable   | R             | MatchAlmacenado |      -7.04        |          -10.56 |
| C             | similar  |                  19 | G                |       2 | stable   | G             | MatchAlmacenado |      -5.92        |          -10.56 |
| Z             | distinta |                   9 | T                |       3 | stable   | T             | MatchAlmacenado |       9.71445e-17 |          -10.56 |
| L             | distinta |                   7 | G                |       5 | stable   | G             | MatchAlmacenado |       0.16        |          -10.56 |
| M             | distinta |                   7 | T                |       3 | stable   | nan           | Espurio         |       0.32        |          -10.56 |

### P (similar, max_ip=21 con R) → MatchAlmacenado (R)

![exp3 P](plots/exp3_P.png)

![energía exp3 P](plots/energy_exp3_P.png) ![estados exp3 P](plots/states_exp3_P.png)

### C (similar, max_ip=19 con G) → MatchAlmacenado (G)

![exp3 C](plots/exp3_C.png)

![energía exp3 C](plots/energy_exp3_C.png) ![estados exp3 C](plots/states_exp3_C.png)

### Z (distinta, max_ip=9 con T) → MatchAlmacenado (T)

![exp3 Z](plots/exp3_Z.png)

![energía exp3 Z](plots/energy_exp3_Z.png) ![estados exp3 Z](plots/states_exp3_Z.png)

### L (distinta, max_ip=7 con G) → MatchAlmacenado (G)

![exp3 L](plots/exp3_L.png)

![energía exp3 L](plots/energy_exp3_L.png) ![estados exp3 L](plots/states_exp3_L.png)

### M (distinta, max_ip=7 con T) → Espurio

![exp3 M](plots/exp3_M.png)

![energía exp3 M](plots/energy_exp3_M.png) ![estados exp3 M](plots/states_exp3_M.png)
