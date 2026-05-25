# Slide: identificación de un estado espurio

Nota para armar la slide que cubre la consigna 2.1.b: *"Ingresar un patrón muy ruidoso e identificar un estado espureo"*.

## Qué es un estado espurio (lo que sí se vio en clase)

Cita de Euge (`docs/clases/hopfield/hopfield.VTT`): *"converge hacia ese Estado. Es un estado atractor, un estado estable, pero no es uno de los patrones almacenados"*.

Mecánicamente: la función de energía `H(S) = -1/2 · Σ W_ij · S_i · S_j` tiene los patrones almacenados como mínimos, pero **también puede tener otros mínimos** (otros puntos fijos). Cuando la red converge a uno de esos otros mínimos, ese estado final no es ninguno de los `ξ^μ` que pusimos. Eso es un espurio.

## Qué no se vio en clase (y por qué importa al elegir el ejemplo)

- La cátedra no clasificó tipos de espurios (negaciones, mezclas, etc.).
- En la literatura clásica, la negación `-ξ^μ` de un patrón almacenado siempre es punto fijo (la energía es simétrica ante `S → -S`). En nuestros CSVs aparecen varios espurios que resultan ser exactamente la negación de un almacenado (hamming 25 contra ese almacenado).
- **Para no meter conceptos por fuera del material**, evitamos destacar como ejemplo principal un espurio que sea negación. Preferimos uno "tipo mezcla" (hamming intermedio contra todos los almacenados).

## Cómo elegir el espurio a mostrar

Mirar `output/<grupo>/exp2_ruido.csv` y filtrar `outcome == "Espurio"`. Para cada uno, calcular el hamming contra **cada** uno de los 4 almacenados.

Criterios para que el espurio sea ilustrativo:
1. **Hamming intermedio** contra todos los almacenados (ej. entre 5 y 15 de los 25 píxeles). Esto descarta el caso "es exactamente la negación de uno" (hamming 25 contra ese, 0 contra el resto invertido).
2. **Energía final negativa** comparable a la de los almacenados (≈ −10 para grupos chicos, ≈ −30 para HMNW). Confirma que es un mínimo local "fuerte", no algo casual.
3. **Trayectoria corta** (2–4 iters) pero con cambio de estado visible. Permite mostrar `S_0 → S_1 → S_final` en la tira y que se vea cómo la red lo va construyendo.

Para identificar candidatos rápido se puede correr (en notebook o script suelto):

```python
import pandas as pd
import numpy as np
from hopfield import load_letters

groups = ["GRTV", "JLRX", "AJKU", "BDOX", "HMNW"]
for g in groups:
    df = pd.read_csv(f"hopfield/output/{g}/exp2_ruido.csv")
    espurios = df[df["outcome"] == "Espurio"]
    # hamming_final ya está respecto del objetivo. Necesitamos contra todos.
    # Cruzar con io_patterns.csv para reconstruir el estado final
    print(g, espurios[["letra_objetivo", "ruido", "hamming_final", "energia_final"]])
```

## Estructura propuesta de la slide

Una sola slide, layout horizontal:

```
┌─────────────────────────────────────────────────────────────────┐
│ Identificación de un estado espurio                             │
│ Grupo <X>, query <L> con ruido 65%                              │
├─────────────────────────────────────────────────────────────────┤
│  [input ruidoso]   [tira S_0 → S_1 → S_final]    [output final] │
│      5×5                  5×5 × n_iter                  5×5     │
├─────────────────────────────────────────────────────────────────┤
│  Energía vs iteración                                           │
│  ─── curva decreciente que estabiliza                           │
├─────────────────────────────────────────────────────────────────┤
│  Hamming del estado final contra cada almacenado:               │
│   - vs <L1>: <h1>                                               │
│   - vs <L2>: <h2>                                               │
│   - vs <L3>: <h3>                                               │
│   - vs <L4>: <h4>                                               │
│                                                                 │
│  → No coincide con ningún almacenado, es un mínimo de energía   │
│    distinto. Estado espurio.                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Qué decir en voz alta

1. *"Para la parte b de la consigna metimos ruido del 65% (16 píxeles de 25 invertidos en promedio)."*
2. *"La red convergió a un estado estable — la energía bajó y se mantuvo."*
3. *"Pero el estado final no es ninguno de los 4 patrones almacenados. Tiene hamming X, Y, Z, W contra cada uno."*
4. *"Eso es un estado espurio: un mínimo de la función de energía distinto de los que pusimos a propósito."*
5. *"La red de Hopfield tiene esta limitación intrínseca — la función de energía puede tener más mínimos que los patrones que querés guardar, y ahí caés cuando el estímulo está lejos de todos."*

## Plots ya generados que sirven

Para cada candidato (`grupo`, `letra`, ruido 65%):
- `output/<grupo>/plots/exp2_<L>_n65.png` — input | output | overlay
- `output/<grupo>/plots/energy_exp2_n65_<L>.png` — energía vs iter
- `output/<grupo>/plots/states_exp2_n65_<L>.png` — tira S_0..S_final

Todos los necesitás están en los outputs actuales. No hace falta recomputar nada, solo elegir el caso.

## Backup: mostrar variedad de espurios

Si querés una segunda slide opcional, podés mostrar **una grilla 2×5 con 10 estados finales** de los 20 espurios totales que tenemos (uno por celda). Sin texto por estado, solo el dibujo, para hacer ver que la red cae en cosas raras y diversas (algunas parecen letras deformadas, otras no parecen nada). Refuerza la idea de "no son patrones almacenados".
