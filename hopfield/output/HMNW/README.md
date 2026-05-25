# Grupo HMNW

Letras almacenadas: **H, M, N, W**

Convención del overlay: verde claro = match `+1↔+1`, blanco = match `-1↔-1`, rojo = mismatch.

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — Patrones almacenados como input

Esperamos que cada patrón almacenado sea un punto fijo (convergencia en 1 iteración a sí mismo).

| letra   |   iters | motivo   | convergio_a   | outcome   | es_fijo   |   energia_inicial |   energia_final |
|:--------|--------:|:---------|:--------------|:----------|:----------|------------------:|----------------:|
| H       |       3 | stable   | N             | FP        | False     |            -27.84 |          -33.92 |
| M       |       3 | stable   | N             | FP        | False     |            -30.88 |          -33.92 |
| N       |       1 | stable   | N             | TP        | True      |            -33.92 |          -33.92 |
| W       |       3 | stable   | N             | FP        | False     |            -30.88 |          -33.92 |

### H (almacenada)

![exp1 H](plots/exp1_H.png)

### M (almacenada)

![exp1 M](plots/exp1_M.png)

### N (almacenada)

![exp1 N](plots/exp1_N.png)

### W (almacenada)

![exp1 W](plots/exp1_W.png)

## Experimento 2 — Patrones almacenados con ruido

Niveles: 10%, 20%, 65%. Una muestra determinística por nivel (seed=1).

| letra_objetivo   |   ruido |   seed |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:-----------------|--------:|-------:|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| H                |    0.1  |      1 |       3 | stable   | N             | FP        |                 1 |               4 |            -22.08 |          -33.92 |
| H                |    0.2  |      1 |       3 | stable   | N             | FP        |                 5 |               4 |            -13.92 |          -33.92 |
| H                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                14 |              21 |             -0.32 |          -33.92 |
| M                |    0.1  |      1 |       2 | stable   | N             | FP        |                 3 |               2 |            -19.36 |          -33.92 |
| M                |    0.2  |      1 |       3 | stable   | N             | FP        |                 3 |               2 |            -16.64 |          -33.92 |
| M                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                17 |              23 |             -3.36 |          -33.92 |
| N                |    0.1  |      1 |       1 | stable   | N             | TP        |                 0 |               0 |            -33.92 |          -33.92 |
| N                |    0.2  |      1 |       2 | stable   | N             | TP        |                 4 |               0 |            -12.16 |          -33.92 |
| N                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                17 |              25 |             -6.88 |          -33.92 |
| W                |    0.1  |      1 |       3 | stable   | N             | FP        |                 4 |               2 |            -10.4  |          -33.92 |
| W                |    0.2  |      1 |       2 | stable   | N             | FP        |                 8 |               2 |             -6.24 |          -33.92 |
| W                |    0.65 |      1 |       3 | stable   | nan           | Espurio   |                16 |              23 |             -1.76 |          -33.92 |

### H con ruido 10% → FP (N)

![exp2 H n10](plots/exp2_H_n10.png)

![energía exp2 H n10](plots/energy_exp2_n10_H.png) ![estados exp2 H n10](plots/states_exp2_n10_H.png)

### H con ruido 20% → FP (N)

![exp2 H n20](plots/exp2_H_n20.png)

![energía exp2 H n20](plots/energy_exp2_n20_H.png) ![estados exp2 H n20](plots/states_exp2_n20_H.png)

### H con ruido 65% → Espurio

![exp2 H n65](plots/exp2_H_n65.png)

![energía exp2 H n65](plots/energy_exp2_n65_H.png) ![estados exp2 H n65](plots/states_exp2_n65_H.png)

### M con ruido 10% → FP (N)

![exp2 M n10](plots/exp2_M_n10.png)

![energía exp2 M n10](plots/energy_exp2_n10_M.png) ![estados exp2 M n10](plots/states_exp2_n10_M.png)

### M con ruido 20% → FP (N)

![exp2 M n20](plots/exp2_M_n20.png)

![energía exp2 M n20](plots/energy_exp2_n20_M.png) ![estados exp2 M n20](plots/states_exp2_n20_M.png)

### M con ruido 65% → Espurio

![exp2 M n65](plots/exp2_M_n65.png)

![energía exp2 M n65](plots/energy_exp2_n65_M.png) ![estados exp2 M n65](plots/states_exp2_n65_M.png)

### N con ruido 10% → TP (N)

![exp2 N n10](plots/exp2_N_n10.png)

![energía exp2 N n10](plots/energy_exp2_n10_N.png) ![estados exp2 N n10](plots/states_exp2_n10_N.png)

### N con ruido 20% → TP (N)

![exp2 N n20](plots/exp2_N_n20.png)

![energía exp2 N n20](plots/energy_exp2_n20_N.png) ![estados exp2 N n20](plots/states_exp2_n20_N.png)

### N con ruido 65% → Espurio

![exp2 N n65](plots/exp2_N_n65.png)

![energía exp2 N n65](plots/energy_exp2_n65_N.png) ![estados exp2 N n65](plots/states_exp2_n65_N.png)

### W con ruido 10% → FP (N)

![exp2 W n10](plots/exp2_W_n10.png)

![energía exp2 W n10](plots/energy_exp2_n10_W.png) ![estados exp2 W n10](plots/states_exp2_n10_W.png)

### W con ruido 20% → FP (N)

![exp2 W n20](plots/exp2_W_n20.png)

![energía exp2 W n20](plots/energy_exp2_n20_W.png) ![estados exp2 W n20](plots/states_exp2_n20_W.png)

### W con ruido 65% → Espurio

![exp2 W n65](plots/exp2_W_n65.png)

![energía exp2 W n65](plots/energy_exp2_n65_W.png) ![estados exp2 W n65](plots/states_exp2_n65_W.png)

## Experimento 3 — Letras no almacenadas

Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados (similares), 3 con menor (distintas).

| letra_query   | tipo     |   max_inner_product | mas_parecida_a   |   iters | motivo   | convergio_a   | outcome         |   energia_inicial |   energia_final |
|:--------------|:---------|--------------------:|:-----------------|--------:|:---------|:--------------|:----------------|------------------:|----------------:|
| A             | similar  |                  15 | H                |       3 | stable   | N             | MatchAlmacenado |             -5.44 |          -33.92 |
| K             | similar  |                  13 | H                |       3 | stable   | N             | MatchAlmacenado |            -11.52 |          -33.92 |
| G             | distinta |                   3 | H                |       4 | stable   | nan           | Espurio         |              1.76 |          -33.92 |
| Q             | distinta |                   3 | N                |       3 | stable   | N             | MatchAlmacenado |              1.6  |          -33.92 |
| O             | distinta |                   1 | H                |       3 | stable   | nan           | Espurio         |              1.92 |          -33.92 |

### A (similar, max_ip=15 con H) → MatchAlmacenado (N)

![exp3 A](plots/exp3_A.png)

![energía exp3 A](plots/energy_exp3_A.png) ![estados exp3 A](plots/states_exp3_A.png)

### K (similar, max_ip=13 con H) → MatchAlmacenado (N)

![exp3 K](plots/exp3_K.png)

![energía exp3 K](plots/energy_exp3_K.png) ![estados exp3 K](plots/states_exp3_K.png)

### G (distinta, max_ip=3 con H) → Espurio

![exp3 G](plots/exp3_G.png)

![energía exp3 G](plots/energy_exp3_G.png) ![estados exp3 G](plots/states_exp3_G.png)

### Q (distinta, max_ip=3 con N) → MatchAlmacenado (N)

![exp3 Q](plots/exp3_Q.png)

![energía exp3 Q](plots/energy_exp3_Q.png) ![estados exp3 Q](plots/states_exp3_Q.png)

### O (distinta, max_ip=1 con H) → Espurio

![exp3 O](plots/exp3_O.png)

![energía exp3 O](plots/energy_exp3_O.png) ![estados exp3 O](plots/states_exp3_O.png)
