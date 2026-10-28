import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ENTRADA = sys.argv[1] if len(sys.argv) > 1 else os.path.join("results", "resultados.csv")
SALIDA = "results"
os.makedirs(SALIDA, exist_ok=True)

ORDEN_PATRONES = ["aleatorio", "ascendente", "descendente", "casi_ordenado", "duplicados"]
ETIQUETAS = {
    "aleatorio": "Aleatorio",
    "ascendente": "Ascendente",
    "descendente": "Descendente",
    "casi_ordenado": "Casi ordenado",
    "duplicados": "Con duplicados",
}

df = pd.read_csv(ENTRADA)
df["patron"] = pd.Categorical(df["patron"], categories=ORDEN_PATRONES, ordered=True)

# ---------------------------------------------------------------- TABLAS
for alg in ["Bubble", "Merge"]:
    d = df[df["algoritmo"] == alg]

    # Tabla 1: estadistica descriptiva del tiempo (ms)
    t = (d.groupby(["patron", "n"], observed=True)["tiempo_ms"]
           .agg(media="mean", mediana="median", desv_std="std", minimo="min", maximo="max")
           .round(4)
           .reset_index())
    t.to_csv(os.path.join(SALIDA, f"tabla_tiempos_{alg.lower()}.csv"), index=False)

    # Tabla 2: contadores (promedio sobre las repeticiones)
    c = (d.groupby(["patron", "n"], observed=True)
           .agg(comparaciones=("comparaciones", "mean"),
                intercambios=("intercambios", "mean"),
                profundidad=("profundidad_recursion", "max"))
           .round(0).astype("int64")
           .reset_index())
    c.to_csv(os.path.join(SALIDA, f"tabla_contadores_{alg.lower()}.csv"), index=False)

# ---------------------------------------------------------------- FIGURA 1: n vs tiempo
plt.rcParams.update({"font.size": 10, "font.family": "serif"})
colores = {"aleatorio": "#1f77b4", "ascendente": "#2ca02c", "descendente": "#d62728",
           "casi_ordenado": "#9467bd", "duplicados": "#ff7f0e"}

fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, alg in zip(axs, ["Bubble", "Merge"]):
    d = df[df["algoritmo"] == alg]
    med = d.groupby(["patron", "n"], observed=True)["tiempo_ms"].median().reset_index()
    for p in ORDEN_PATRONES:
        m = med[med["patron"] == p]
        ax.plot(m["n"], m["tiempo_ms"], marker="o", color=colores[p], label=ETIQUETAS[p])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Bubble Sort" if alg == "Bubble" else "Merge Sort")
    ax.set_xlabel("Tama\u00f1o de entrada n")
    ax.grid(True, which="both", alpha=0.3)
axs[0].set_ylabel("Tiempo mediano (ms)")
axs[1].legend(title="Patr\u00f3n", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(SALIDA, "fig1_n_vs_tiempo.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- FIGURA 2: boxplot
N_BOX = 10000   # unico tamano medido en ambos algoritmos con tiempos grandes
d = df[df["n"] == N_BOX]
fig, ax = plt.subplots(figsize=(9, 4.5))
datos, posiciones, cols, marcas = [], [], [], []
for i, p in enumerate(ORDEN_PATRONES):
    for j, (alg, col) in enumerate([("Bubble", "#d62728"), ("Merge", "#1f77b4")]):
        datos.append(d[(d["algoritmo"] == alg) & (d["patron"] == p)]["tiempo_ms"].values)
        posiciones.append(i * 3 + j)
        cols.append(col)
bp = ax.boxplot(datos, positions=posiciones, widths=0.8, patch_artist=True,
                flierprops={"markersize": 3})
for caja, col in zip(bp["boxes"], cols):
    caja.set_facecolor(col)
    caja.set_alpha(0.6)
ax.set_yscale("log")
ax.set_xticks([i * 3 + 0.5 for i in range(len(ORDEN_PATRONES))])
ax.set_xticklabels([ETIQUETAS[p] for p in ORDEN_PATRONES])
ax.set_ylabel("Tiempo (ms, escala log)")
ax.set_title(f"Distribuci\u00f3n de tiempos con n = {N_BOX:,}".replace(",", " "))
ax.grid(True, axis="y", which="both", alpha=0.3)
ax.legend([bp["boxes"][0], bp["boxes"][1]], ["Bubble Sort", "Merge Sort"], loc="center right")
fig.tight_layout()
fig.savefig(os.path.join(SALIDA, "fig2_boxplot.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- FIGURA 3: contadores
# Explica los tiempos de la Fig. 2: en Bubble las comparaciones son fijas y lo que cambia
# con el patron son los intercambios; en Merge cambian las comparaciones segun el patron.
d = df[df["n"] == N_BOX]
cont = (d.groupby(["algoritmo", "patron"], observed=True)[["comparaciones", "intercambios"]]
          .mean().reset_index())
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
etiquetas = [ETIQUETAS[p] for p in ORDEN_PATRONES]

b = cont[cont["algoritmo"] == "Bubble"].set_index("patron").loc[ORDEN_PATRONES]
axs[0].bar(etiquetas, b["intercambios"] / 1e6, color="#d62728", alpha=0.7)
axs[0].axhline(b["comparaciones"].iloc[0] / 1e6, color="black", linestyle="--", linewidth=1,
               label="Comparaciones (iguales en todos los patrones)")
NTXT = f"{N_BOX:,}".replace(",", " ")
axs[0].set_title("Bubble Sort, n = " + NTXT)
axs[0].set_ylabel("Intercambios (millones)")
axs[0].set_ylim(0, b["comparaciones"].iloc[0] / 1e6 * 1.25)
axs[0].legend(fontsize=8, loc="upper left")

m = cont[cont["algoritmo"] == "Merge"].set_index("patron").loc[ORDEN_PATRONES]
axs[1].bar(etiquetas, m["comparaciones"] / 1e3, color="#1f77b4", alpha=0.7)
axs[1].set_title("Merge Sort, n = " + NTXT)
axs[1].set_ylabel("Comparaciones (miles)")

for ax in axs:
    ax.tick_params(axis="x", labelrotation=30, labelsize=8)
    ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(SALIDA, "fig3_contadores.png"), dpi=200)
plt.close(fig)

print("Listo. Archivos generados en", SALIDA)
