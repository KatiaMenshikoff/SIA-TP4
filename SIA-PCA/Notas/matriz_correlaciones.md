# Matriz de correlaciones - europe.csv

Procedimiento (slide 32, paso 3): calcular la matriz de correlaciones Sx.
Sobre variables estandarizadas, la covarianza coincide con la correlacion.

## Calculo de referencia: s_11 (varianza muestral de Area)

Formula (slide 7):  s^2 = 1/(n-1) * sum_{i=1..n} (x_i - X_bar)^2

- n = 28
- X_bar (media de Area) = 166422.5357

Desvios (x_i - X_bar) y sus cuadrados:

| i | pais | x_i | x_i - X_bar | (x_i - X_bar)^2 |
|---|------|-----|-------------|------------------|
| 1 | Austria | 83871 | -82551.54 | 6814756048.79 |
| 2 | Belgium | 30528 | -135894.54 | 18467324837.00 |
| 3 | Bulgaria | 110879 | -55543.54 | 3085084359.64 |
| 4 | Croatia | 56594 | -109828.54 | 12062307257.14 |
| 5 | Czech Republic | 78867 | -87555.54 | 7665971834.22 |
| 6 | Denmark | 43094 | -123328.54 | 15209927721.43 |
| 7 | Estonia | 45228 | -121194.54 | 14688115487.00 |
| 8 | Finland | 338145 | 171722.46 | 29488604740.36 |
| 9 | Germany | 357022 | 190599.46 | 36328155786.00 |
| 10 | Greece | 131957 | -34465.54 | 1187873152.07 |
| 11 | Hungary | 93028 | -73394.54 | 5386757872.72 |
| 12 | Iceland | 103000 | -63422.54 | 4022418036.43 |
| 13 | Ireland | 70273 | -96149.54 | 9244733218.07 |
| 14 | Italy | 301340 | 134917.46 | 18202722169.29 |
| 15 | Latvia | 64589 | -101833.54 | 10370068996.07 |
| 16 | Lithuania | 65300 | -101122.54 | 10225767229.29 |
| 17 | Luxembourg | 2586 | -163836.54 | 26842410434.86 |
| 18 | Netherlands | 41543 | -124879.54 | 15594898440.22 |
| 19 | Norway | 323802 | 157379.46 | 24768295778.86 |
| 20 | Poland | 312685 | 146262.46 | 21392708458.93 |
| 21 | Portugal | 92090 | -74332.54 | 5525325865.72 |
| 22 | Slovakia | 49035 | -117387.54 | 13779833541.07 |
| 23 | Slovenia | 20273 | -146149.54 | 21359686789.50 |
| 24 | Spain | 505370 | 338947.46 | 114885383545.72 |
| 25 | Sweden | 450295 | 283872.46 | 80583575979.64 |
| 26 | Switzerland | 41277 | -125145.54 | 15661405109.22 |
| 27 | Ukraine | 603550 | 437127.46 | 191080420032.86 |
| 28 | United Kingdom | 243610 | 77187.46 | 5957904642.86 |

- sum (x_i - X_bar)^2 = 739882437364.96
- s_11 = 739882437364.96 / (28 - 1) = **27403053235.7394**

## Calculo de referencia: r_12 (correlacion Area - GDP)

Formulas:
- s_ik = 1/(n-1) * sum (x_ji - X_bar_i)(x_jk - X_bar_k)  (slide 8, con n-1)
- r_ik = s_ik / (sqrt(s_ii) * sqrt(s_kk))                 (slide 11)

- s_12 (cov Area-GDP) = -332532111.5079
- s_22 (var GDP)      = 210311362.4339
- r_12 = -332532111.5079 / (sqrt(27403053235.7394) * sqrt(210311362.4339)) = **-0.1385**

Para el resto de los s_ik y r_ik se aplica exactamente el mismo procedimiento
variando los pares de variables.

## Matriz de correlaciones Sx completa (7x7)

| | Area | GDP | Inflation | Life.expect | Military | Pop.growth | Unemployment |
|---|---|---|---|---|---|---|---|
| **Area** | 1.0000 | -0.1385 | 0.3201 | -0.0217 | 0.1017 | -0.0886 | 0.0254 |
| **GDP** | -0.1385 | 1.0000 | -0.4928 | 0.7010 | -0.2845 | 0.7604 | -0.5278 |
| **Inflation** | 0.3201 | -0.4928 | 1.0000 | -0.6792 | 0.0483 | -0.4787 | 0.1988 |
| **Life.expect** | -0.0217 | 0.7010 | -0.6792 | 1.0000 | -0.0632 | 0.7716 | -0.2460 |
| **Military** | 0.1017 | -0.2845 | 0.0483 | -0.0632 | 1.0000 | -0.2823 | 0.2923 |
| **Pop.growth** | -0.0886 | 0.7604 | -0.4787 | 0.7716 | -0.2823 | 1.0000 | -0.1748 |
| **Unemployment** | 0.0254 | -0.5278 | 0.1988 | -0.2460 | 0.2923 | -0.1748 | 1.0000 |

Interpretacion (slide 10):
- valores > 0: asociacion lineal positiva
- valores < 0: asociacion lineal negativa
- valores ~ 0: variables independientes
