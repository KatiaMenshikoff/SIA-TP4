# Grupo BDOX
| 15.67 | ('B', 'D', 'O', 'X') |
| ----- | -------------------- |

Letras almacenadas: **B, D, O, X**

Convención del overlay: verde claro = match `+1↔+1`, blanco = match `-1↔-1`, rojo = mismatch.

![Outcomes](plots/outcomes_summary.png)

## Experimento 1 — Patrones almacenados como input

Esperamos que cada patrón almacenado sea un punto fijo (convergencia en 1 iteración a sí mismo).

| letra | iters | motivo | convergio_a | outcome | es_fijo | energia_inicial | energia_final |
| :---- | ----: | :----- | :---------- | :------ | :------ | --------------: | ------------: |
| B     |     3 | stable | D           | FP      | False   |          -23.04 |        -28.48 |
| D     |     1 | stable | D           | TP      | True    |          -28.48 |        -28.48 |
| O     |     1 | stable | O           | TP      | True    |          -28.48 |        -28.48 |
| X     |     3 | stable | nan         | Espurio | False   |          -23.04 |        -28.48 |

### B (almacenada)

![exp1 B](plots/exp1_B.png)

### D (almacenada)

![exp1 D](plots/exp1_D.png)

### O (almacenada)

![exp1 O](plots/exp1_O.png)

### X (almacenada)

![exp1 X](plots/exp1_X.png)

## Experimento 2 — Patrones almacenados con ruido

Niveles: 10%, 20%, 65%. Una muestra determinística por nivel (seed=1).

| letra_objetivo   |   ruido |   seed |   iters | motivo   | convergio_a   | outcome   |   hamming_inicial |   hamming_final |   energia_inicial |   energia_final |
|:-----------------|--------:|-------:|--------:|:---------|:--------------|:----------|------------------:|----------------:|------------------:|----------------:|
| B                |    0.1  |      1 |       3 | stable   | D             | FP        |                 1 |               4 |            -17.92 |          -28.48 |
| B                |    0.2  |      1 |       2 | stable   | D             | FP        |                 5 |               4 |            -10.4  |          -28.48 |
| B                |    0.65 |      1 |       4 | cycle    | nan           | Ciclo     |                14 |              20 |              1.28 |          -28.16 |
| D                |    0.1  |      1 |       3 | cycle    | nan           | Ciclo     |                 3 |               1 |            -17.28 |          -28.16 |
| D                |    0.2  |      1 |       2 | stable   | D             | TP        |                 3 |               0 |            -18.72 |          -28.48 |
| D                |    0.65 |      1 |       4 | cycle    | nan           | Ciclo     |                17 |              24 |             -4.48 |          -28.16 |
| O                |    0.1  |      1 |       1 | stable   | O             | TP        |                 0 |               0 |            -28.48 |          -28.48 |
| O                |    0.2  |      1 |       2 | stable   | O             | TP        |                 4 |               0 |             -9.28 |          -28.48 |
| O                |    0.65 |      1 |       2 | stable   | nan           | Espurio   |                17 |              25 |             -2.24 |          -28.48 |
| X                |    0.1  |      1 |       3 | stable   | nan           | Espurio   |                 4 |               4 |            -12.16 |          -28.48 |
| X                |    0.2  |      1 |       2 | stable   | nan           | Espurio   |                 8 |               4 |             -3.36 |          -28.48 |
| X                |    0.65 |      1 |       4 | cycle    | nan           | Ciclo     |                16 |              20 |             -1.92 |          -28.16 |

### B con ruido 10% → FP (D)

![exp2 B n10](plots/exp2_B_n10.png)

![energía exp2 B n10](plots/energy_exp2_n10_B.png) ![estados exp2 B n10](plots/states_exp2_n10_B.png)

### B con ruido 20% → FP (D)

![exp2 B n20](plots/exp2_B_n20.png)

![energía exp2 B n20](plots/energy_exp2_n20_B.png) ![estados exp2 B n20](plots/states_exp2_n20_B.png)

### B con ruido 65% → Ciclo

![exp2 B n65](plots/exp2_B_n65.png)

![energía exp2 B n65](plots/energy_exp2_n65_B.png) ![estados exp2 B n65](plots/states_exp2_n65_B.png)

### D con ruido 10% → Ciclo

![exp2 D n10](plots/exp2_D_n10.png)

![energía exp2 D n10](plots/energy_exp2_n10_D.png) ![estados exp2 D n10](plots/states_exp2_n10_D.png)

### D con ruido 20% → TP (D)

![exp2 D n20](plots/exp2_D_n20.png)

![energía exp2 D n20](plots/energy_exp2_n20_D.png) ![estados exp2 D n20](plots/states_exp2_n20_D.png)

### D con ruido 65% → Ciclo

![exp2 D n65](plots/exp2_D_n65.png)

![energía exp2 D n65](plots/energy_exp2_n65_D.png) ![estados exp2 D n65](plots/states_exp2_n65_D.png)

### O con ruido 10% → TP (O)

![exp2 O n10](plots/exp2_O_n10.png)

![energía exp2 O n10](plots/energy_exp2_n10_O.png) ![estados exp2 O n10](plots/states_exp2_n10_O.png)

### O con ruido 20% → TP (O)

![exp2 O n20](plots/exp2_O_n20.png)

![energía exp2 O n20](plots/energy_exp2_n20_O.png) ![estados exp2 O n20](plots/states_exp2_n20_O.png)

### O con ruido 65% → Espurio

![exp2 O n65](plots/exp2_O_n65.png)

![energía exp2 O n65](plots/energy_exp2_n65_O.png) ![estados exp2 O n65](plots/states_exp2_n65_O.png)

### X con ruido 10% → Espurio

![exp2 X n10](plots/exp2_X_n10.png)

![energía exp2 X n10](plots/energy_exp2_n10_X.png) ![estados exp2 X n10](plots/states_exp2_n10_X.png)

### X con ruido 20% → Espurio

![exp2 X n20](plots/exp2_X_n20.png)

![energía exp2 X n20](plots/energy_exp2_n20_X.png) ![estados exp2 X n20](plots/states_exp2_n20_X.png)

### X con ruido 65% → Ciclo

![exp2 X n65](plots/exp2_X_n65.png)

![energía exp2 X n65](plots/energy_exp2_n65_X.png) ![estados exp2 X n65](plots/states_exp2_n65_X.png)

## Experimento 3 — Letras no almacenadas

Elegidas por grupo: 2 con mayor `max |<,>|` contra los almacenados (similares), 3 con menor (distintas).

| letra_query   | tipo     |   max_inner_product | mas_parecida_a   |   iters | motivo   | convergio_a   | outcome         |   energia_inicial |   energia_final |
|:--------------|:---------|--------------------:|:-----------------|--------:|:---------|:--------------|:----------------|------------------:|----------------:|
| E             | similar  |                  17 | B                |       3 | stable   | D             | MatchAlmacenado |             -6.4  |          -28.48 |
| G             | similar  |                  17 | O                |       2 | stable   | O             | MatchAlmacenado |            -12.16 |          -28.48 |
| I             | distinta |                   3 | B                |       3 | stable   | D             | MatchAlmacenado |              1.6  |          -28.48 |
| J             | distinta |                   3 | B                |       3 | stable   | D             | MatchAlmacenado |              1.44 |          -28.48 |
| T             | distinta |                   1 | B                |       5 | cycle    | nan           | Ciclo           |              1.92 |          -28.16 |

### E (similar, max_ip=17 con B) → MatchAlmacenado (D)

![exp3 E](plots/exp3_E.png)

![energía exp3 E](plots/energy_exp3_E.png) ![estados exp3 E](plots/states_exp3_E.png)

### G (similar, max_ip=17 con O) → MatchAlmacenado (O)

![exp3 G](plots/exp3_G.png)

![energía exp3 G](plots/energy_exp3_G.png) ![estados exp3 G](plots/states_exp3_G.png)

### I (distinta, max_ip=3 con B) → MatchAlmacenado (D)

![exp3 I](plots/exp3_I.png)

![energía exp3 I](plots/energy_exp3_I.png) ![estados exp3 I](plots/states_exp3_I.png)

### J (distinta, max_ip=3 con B) → MatchAlmacenado (D)

![exp3 J](plots/exp3_J.png)

![energía exp3 J](plots/energy_exp3_J.png) ![estados exp3 J](plots/states_exp3_J.png)

### T (distinta, max_ip=1 con B) → Ciclo

![exp3 T](plots/exp3_T.png)

![energía exp3 T](plots/energy_exp3_T.png) ![estados exp3 T](plots/states_exp3_T.png)
