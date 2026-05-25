# Hopfield

Notebook y scripts para el ejercicio de Hopfield del TP4.

## Levantar el Jupyter

Desde la raíz del repo, con el `.venv` ya creado:

```bash
cd /Users/tomaspinausig/code/SIA-TP4
source .venv/bin/activate
pip install -r requirements.txt    # solo la primera vez
jupyter lab hopfield/ortogonalidad_letras.ipynb
```

Alternativas:

- Interfaz clásica: `jupyter notebook hopfield/ortogonalidad_letras.ipynb`
- Si `jupyter` no está en el PATH tras activar el venv: `python -m jupyter lab hopfield/ortogonalidad_letras.ipynb`

## Archivos

- `ortogonalidad_letras.ipynb` — análisis de ortogonalidad entre patrones de letras.
- `letters.txt` — patrones de letras usados como entrada.
- `step_perceptron.py` — utilidades de perceptrón por pasos.
- `Implementación.md` — notas de implementación.
