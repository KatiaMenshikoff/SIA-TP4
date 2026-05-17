# Autovalores y autovectores de Sx - europe.csv

Pasos 4-7 del procedimiento (slide 32).

## Autovalores ordenados (slide 23)

`lambda_i` = varianza de la componente Y_i.
Proporcion = lambda_i / sum(lambdas)  (slide 31).

| i   | lambda_i | Proporcion | Proporcion acumulada |
| --- | -------- | ---------- | -------------------- |
| 1   | 3.2272   | 46.10%     | 46.10%               |
| 2   | 1.1871   | 16.96%     | 63.06%               |
| 3   | 1.0632   | 15.19%     | 78.25%               |
| 4   | 0.7704   | 11.01%     | 89.25%               |
| 5   | 0.4578   | 6.54%      | 95.80%               |
| 6   | 0.1687   | 2.41%      | 98.21%               |
| 7   | 0.1256   | 1.79%      | 100.00%              |

Suma de autovalores = 7.0000 (= traza de Sx = nro de variables)

## Matriz V de autovectores (slide 22, paso 6)

Cada columna es el vector de cargas (loadings) de la componente Y_i.

| variable         | v1      |
| ---------------- | ------- |
| **Area**         | -0.1249 |
| **GDP**          | +0.5005 |
| **Inflation**    | -0.4065 |
| **Life.expect**  | +0.4829 |
| **Military**     | -0.1881 |
| **Pop.growth**   | +0.4757 |
| **Unemployment** | -0.2717 |

## Componentes principales Y (paso 7)

Y_i = v_1i * x_1 + v_2i * x_2 + ... + v_ni * x_n  (slide 22)

Con las X estandarizadas no hace falta restar la media (nota slide 20).

| pais           | Y1      |
| -------------- | ------- |
| Austria        | +1.0623 |
| Belgium        | +0.6688 |
| Bulgaria       | -2.5629 |
| Croatia        | -1.2473 |
| Czech Republic | +0.1642 |
| Denmark        | +0.9380 |
| Estonia        | -2.4429 |
| Finland        | +0.2068 |
| Germany        | +0.5817 |
| Greece         | -0.9824 |
| Hungary        | -1.3717 |
| Iceland        | +1.5552 |
| Ireland        | +1.7763 |
| Italy          | +0.8378 |
| Latvia         | -2.2645 |
| Lithuania      | -1.5025 |
| Luxembourg     | +3.4158 |
| Netherlands    | +1.8069 |
| Norway         | +2.0686 |
| Poland         | -1.4453 |
| Portugal       | -0.5170 |
| Slovakia       | -0.7689 |
| Slovenia       | -0.0663 |
| Spain          | +0.1608 |
| Sweden         | +0.8692 |
| Switzerland    | +3.2225 |
| Ukraine        | -4.4977 |
| United Kingdom | +0.3347 |
