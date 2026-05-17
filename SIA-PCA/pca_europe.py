"""
PCA sobre europe.csv - siguiendo el procedimiento de la slide 32.
Paso 1: construir matriz X (variables en columnas).
Paso 2: estandarizar (resta media, divide por desvío).
Boxplots antes y después de estandarizar (slides 43-44).
"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("europe.csv")
countries = df["Country"].values
X = df.drop(columns=["Country"])

print("Matriz X (variables en columnas):")
print(X)
print("\nShape:", X.shape)

fig, ax = plt.subplots(figsize=(10, 6))
X.boxplot(ax=ax)
ax.set_title("Boxplot - Variables originales")
ax.set_ylabel("Valor")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("boxplot_original.png", dpi=120)
plt.close()
print("\nGuardado: boxplot_original.png")

X_std = (X - X.mean()) / X.std()

print("\nMatriz X estandarizada (primeras filas):")
print(X_std.head())
print("\nMedia tras estandarizar (~0):")
print(X_std.mean().round(6).to_dict())
print("Desvío tras estandarizar (~1):")
print(X_std.std().round(6).to_dict())

fig, ax = plt.subplots(figsize=(10, 6))
X_std.boxplot(ax=ax)
ax.set_title("Boxplot - Variables estandarizadas")
ax.set_ylabel("Valor estandarizado")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("boxplot_estandarizado.png", dpi=120)
plt.close()
print("Guardado: boxplot_estandarizado.png")

# ---------------------------------------------------------------
# Paso 3 slide 32: matriz de correlaciones Sx
# Sobre variables estandarizadas, la covarianza = correlación.
# Definición slide 11:  r_ik = s_ik / (sqrt(s_ii) * sqrt(s_kk))
# ---------------------------------------------------------------

# Calculo de referencia: s_11 (varianza muestral de Area)
# Slide 7:  s^2 = 1/(n-1) * sum (x_i - X_bar)^2
col = "Area"
x = X[col].values
n = len(x)
x_mean = x.mean()
desvios = x - x_mean
desvios_cuad = desvios ** 2
suma_cuad = desvios_cuad.sum()
s11 = suma_cuad / (n - 1)

# Correlacion muestral entre Area y GDP como segundo ejemplo (slide 8 + 11)
col2 = "GDP"
y = X[col2].values
y_mean = y.mean()
s12 = ((x - x_mean) * (y - y_mean)).sum() / (n - 1)
s22 = ((y - y_mean) ** 2).sum() / (n - 1)
r12 = s12 / ((s11 ** 0.5) * (s22 ** 0.5))

# Matriz de correlaciones completa
S = X.corr()
print("\nMatriz de correlaciones Sx:")
print(S.round(4))

# Volcar a /Notas
with open("Notas/matriz_correlaciones.md", "w") as f:
    f.write("# Matriz de correlaciones - europe.csv\n\n")
    f.write("Procedimiento (slide 32, paso 3): calcular la matriz de correlaciones Sx.\n")
    f.write("Sobre variables estandarizadas, la covarianza coincide con la correlacion.\n\n")

    f.write("## Calculo de referencia: s_11 (varianza muestral de Area)\n\n")
    f.write("Formula (slide 7):  s^2 = 1/(n-1) * sum_{i=1..n} (x_i - X_bar)^2\n\n")
    f.write(f"- n = {n}\n")
    f.write(f"- X_bar (media de Area) = {x_mean:.4f}\n\n")
    f.write("Desvios (x_i - X_bar) y sus cuadrados:\n\n")
    f.write("| i | pais | x_i | x_i - X_bar | (x_i - X_bar)^2 |\n")
    f.write("|---|------|-----|-------------|------------------|\n")
    for i, (pais, xi, d, dc) in enumerate(zip(countries, x, desvios, desvios_cuad), 1):
        f.write(f"| {i} | {pais} | {xi} | {d:.2f} | {dc:.2f} |\n")
    f.write(f"\n- sum (x_i - X_bar)^2 = {suma_cuad:.2f}\n")
    f.write(f"- s_11 = {suma_cuad:.2f} / ({n} - 1) = **{s11:.4f}**\n\n")

    f.write("## Calculo de referencia: r_12 (correlacion Area - GDP)\n\n")
    f.write("Formulas:\n")
    f.write("- s_ik = 1/(n-1) * sum (x_ji - X_bar_i)(x_jk - X_bar_k)  (slide 8, con n-1)\n")
    f.write("- r_ik = s_ik / (sqrt(s_ii) * sqrt(s_kk))                 (slide 11)\n\n")
    f.write(f"- s_12 (cov Area-GDP) = {s12:.4f}\n")
    f.write(f"- s_22 (var GDP)      = {s22:.4f}\n")
    f.write(f"- r_12 = {s12:.4f} / (sqrt({s11:.4f}) * sqrt({s22:.4f})) = **{r12:.4f}**\n\n")
    f.write("Para el resto de los s_ik y r_ik se aplica exactamente el mismo procedimiento\n")
    f.write("variando los pares de variables.\n\n")

    f.write("## Matriz de correlaciones Sx completa (7x7)\n\n")
    cols = list(S.columns)
    f.write("| | " + " | ".join(cols) + " |\n")
    f.write("|" + "---|" * (len(cols) + 1) + "\n")
    for i, row in enumerate(cols):
        vals = " | ".join(f"{S.iloc[i, j]:.4f}" for j in range(len(cols)))
        f.write(f"| **{row}** | {vals} |\n")
    f.write("\nInterpretacion (slide 10):\n")
    f.write("- valores > 0: asociacion lineal positiva\n")
    f.write("- valores < 0: asociacion lineal negativa\n")
    f.write("- valores ~ 0: variables independientes\n")

print("\nGuardado: Notas/matriz_correlaciones.md")

# ---------------------------------------------------------------
# Paso 4 slide 32: calcular AyA (autovalores y autovectores de Sx)
# Paso 5: ordenarlos de mayor a menor
# Paso 6: armar V con los autovectores
# ---------------------------------------------------------------
import numpy as np

S_mat = S.values
vals, vecs = np.linalg.eigh(S_mat)  # Sx es simetrica
orden = np.argsort(vals)[::-1]
lambdas = vals[orden]
V = vecs[:, orden]

cols = list(S.columns)
print("\nAutovalores ordenados (lambda_i = Var(Y_i)):")
for i, lv in enumerate(lambdas, 1):
    print(f"  lambda_{i} = {lv:.4f}   ({lv/lambdas.sum()*100:.2f}% de la varianza)")

print("\nMatriz V (autovectores en columnas, slide 22):")
print(pd.DataFrame(V, index=cols,
      columns=[f"v{i}" for i in range(1, len(cols)+1)]).round(4))

# Paso 7: componentes principales Y como combinacion lineal de las X estandarizadas
Y = X_std.values @ V
Y_df = pd.DataFrame(Y, index=countries,
                    columns=[f"Y{i}" for i in range(1, len(cols)+1)])
print("\nComponentes principales Y (primeras filas):")
print(Y_df.round(4).head())

# Volcar a /Notas
with open("Notas/autovalores_autovectores.md", "w") as f:
    f.write("# Autovalores y autovectores de Sx - europe.csv\n\n")
    f.write("Pasos 4-7 del procedimiento (slide 32).\n\n")

    f.write("## Autovalores ordenados (slide 23)\n\n")
    f.write("`lambda_i` = varianza de la componente Y_i.\n")
    f.write("Proporcion = lambda_i / sum(lambdas)  (slide 31).\n\n")
    f.write("| i | lambda_i | Proporcion | Proporcion acumulada |\n")
    f.write("|---|----------|------------|----------------------|\n")
    acum = 0.0
    total = lambdas.sum()
    for i, lv in enumerate(lambdas, 1):
        prop = lv / total
        acum += prop
        f.write(f"| {i} | {lv:.4f} | {prop*100:.2f}% | {acum*100:.2f}% |\n")
    f.write(f"\nSuma de autovalores = {total:.4f} (= traza de Sx = nro de variables)\n\n")

    f.write("## Matriz V de autovectores (slide 22, paso 6)\n\n")
    f.write("Cada columna es el vector de cargas (loadings) de la componente Y_i.\n\n")
    f.write("| variable | " + " | ".join(f"v{i}" for i in range(1, len(cols)+1)) + " |\n")
    f.write("|" + "---|" * (len(cols)+1) + "\n")
    for i, var in enumerate(cols):
        vals_row = " | ".join(f"{V[i, j]:+.4f}" for j in range(len(cols)))
        f.write(f"| **{var}** | {vals_row} |\n")

    f.write("\n## Componentes principales Y (paso 7)\n\n")
    f.write("Y_i = v_1i * x_1 + v_2i * x_2 + ... + v_ni * x_n  (slide 22)\n\n")
    f.write("Con las X estandarizadas no hace falta restar la media (nota slide 20).\n\n")
    f.write("| pais | " + " | ".join(Y_df.columns) + " |\n")
    f.write("|" + "---|" * (len(Y_df.columns)+1) + "\n")
    for pais, row in Y_df.iterrows():
        vals_row = " | ".join(f"{v:+.4f}" for v in row.values)
        f.write(f"| {pais} | {vals_row} |\n")

print("\nGuardado: Notas/autovalores_autovectores.md")

# ---------------------------------------------------------------
# Grafico de barras de PC1 por pais (replica slide 46)
# ---------------------------------------------------------------
Y1 = Y_df["Y1"].sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(range(len(Y1)), Y1.values)
ax.set_xticks(range(len(Y1)))
ax.set_xticklabels(Y1.index, rotation=75, ha="right")
ax.axhline(0, color="black", linewidth=0.6)
ax.set_ylabel("PC1 (Y1)")
ax.set_title("PCA1 per country - europe.csv")
plt.tight_layout()
plt.savefig("pc1_por_pais.png", dpi=120)
plt.close()
print("Guardado: pc1_por_pais.png")

# ---------------------------------------------------------------
# Biplot PC1 vs PC2 (replica slide 45)
# Puntos: paises proyectados sobre PC1 y PC2
# Flechas: cargas de cada variable (v1, v2)
# ---------------------------------------------------------------
pc1 = Y_df["Y1"].values
pc2 = Y_df["Y2"].values
v1 = V[:, 0]
v2 = V[:, 1]

# Escala para las flechas (que se vean en el rango de los puntos)
escala = max(np.abs(pc1).max(), np.abs(pc2).max()) / np.abs(np.c_[v1, v2]).max() * 0.9

fig, ax = plt.subplots(figsize=(11, 8))
ax.scatter(pc1, pc2, color="purple", s=40, zorder=3)
for pais, x_, y_ in zip(countries, pc1, pc2):
    ax.annotate(pais, (x_, y_), fontsize=8, xytext=(4, 4),
                textcoords="offset points", color="purple")

for i, var in enumerate(cols):
    ax.arrow(0, 0, v1[i]*escala, v2[i]*escala,
             color="teal", width=0.005, head_width=0.08, length_includes_head=True)
    ax.text(v1[i]*escala*1.1, v2[i]*escala*1.1, var,
            color="teal", fontsize=9, ha="center")

ax.axhline(0, color="grey", linewidth=0.5)
ax.axvline(0, color="grey", linewidth=0.5)
ax.set_xlabel(f"PC1 ({lambdas[0]/lambdas.sum()*100:.1f}%)")
ax.set_ylabel(f"PC2 ({lambdas[1]/lambdas.sum()*100:.1f}%)")
ax.set_title("Biplot - Valores de las Componentes Principales 1 y 2")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("biplot.png", dpi=120)
plt.close()
print("Guardado: biplot.png")
