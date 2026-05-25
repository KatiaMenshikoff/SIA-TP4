# Por qué los complementos son estados estables

Observación: en los experimentos con `p_flip > 0.5` la red converge sistemáticamente al **complemento** del patrón almacenado (todos los píxeles invertidos). Por ejemplo, en GRTV con G@65% el output tiene `hamming=25` contra G original y `hamming=0` contra `-G`. Esto no es un bug — es una propiedad estructural de Hopfield.

## La cuenta directa

La función de energía es:

```
H(S) = -½ · Σ_{i,j} W_ij · S_i · S_j
```

Reemplazo `S` por `-S` (invertir todos los píxeles):

```
H(-S) = -½ · Σ W_ij · (-S_i) · (-S_j)
      = -½ · Σ W_ij · S_i · S_j           ← porque (-1)·(-1) = +1
      = H(S)
```

`H` es **invariante ante `S → -S`**. Cada configuración tiene la misma energía que su complemento. El paisaje de energía es simétrico: por cada pozo hay un pozo gemelo "espejo".

## Misma propiedad vista desde la regla de actualización

`S_{t+1} = sign(W · S_t)`

Si `ξ` es punto fijo, `sign(W·ξ) = ξ`. Entonces:

```
sign(W · (-ξ)) = sign(-W·ξ) = -sign(W·ξ) = -ξ
```

`-ξ` también es punto fijo. Conclusión: **por cada patrón almacenado `ξ^μ` la red tiene automáticamente otro punto fijo `-ξ^μ`**, sin que nadie lo pida. Con 4 patrones almacenados son 8 puntos fijos garantizados, más los espurios "mezcla" que aparezcan por interacciones.

## De dónde viene la simetría

La simetría de `H` viene de que `W` es simétrica (`W_ij = W_ji`) y de que `S_i · S_j` también es simétrica en el cambio de signo de ambos factores. El `np.fill_diagonal(W, 0)` no afecta esto (saca términos `W_ii · S_i² = W_ii`, que son constantes y no rompen la simetría ante `S → -S`).

## Cómo se manifiesta en los experimentos

Con `p_flip < 0.5` el input ruidoso está más cerca del original que del complemento (cuestión de hamming: en promedio se flippean `p_flip · N` píxeles, y si `p_flip · N < N/2` el input queda en la cuenca del original). La red converge al original.

Con `p_flip > 0.5` pasa lo opuesto. Verificación directa para G@65% en GRTV:

| | vs G original | vs G complemento |
|---|---|---|
| Query | 14 | 11 |
| Output | 25 | 0 |

El query ya estaba más cerca del complemento (11 < 14). La red hace lo que tiene que hacer: cae al patrón más cercano en su paisaje de energía. Como el complemento es un atractor igual de "fuerte" que el original, lo encuentra.

## Por qué la cátedra no lo trató

Euge habló de "estado espurio" como *"un estado atractor, un estado estable, pero no es uno de los patrones almacenados"*. El complemento entra en esa definición. Pero el caso particular `-ξ^μ` (que existe por la simetría de `H`) no se mencionó. En la literatura clásica de Hopfield se trata como un caso aparte porque tiene esta garantía estructural, mientras que los espurios "mezcla" aparecen por interacciones más sutiles entre patrones.

## Implicancia para el TP

- En los CSVs el complemento queda etiquetado como `outcome=Espurio` porque por definición no es uno de los almacenados. Esto es correcto técnicamente.
- Para la slide de "identificación de estado espurio" (consigna 2.1.b) **conviene elegir un espurio que NO sea complemento** — los hay con `hamming_final` intermedio (ej. 12) que son verdaderas mezclas. Esos son más ilustrativos y se quedan dentro del material visto en clase.
- Si igualmente aparece en alguna slide un caso de complemento, alcanza con decir *"converge a un estado estable que no es ninguno de los almacenados; resulta ser exactamente el patrón objetivo invertido. Esto es consistente con la simetría de la función de energía"* sin entrar en la demostración formal.
