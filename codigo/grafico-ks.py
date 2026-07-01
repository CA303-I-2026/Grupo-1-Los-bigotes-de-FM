# grafico_ks_resumen.py
# Grafica el resumen de la prueba KS (D_stat vs D_alpha) y el MAD por posicion
# a partir de ../datos/procesados/ks_tokens_resumen.txt

import re
import matplotlib.pyplot as plt
import seaborn as sns

IN_TXT = "../datos/procesados/ks_tokens_resumen.txt"
OUT_PNG = "../datos/procesados/ks_resumen_grafico.png"
palette = sns.color_palette("Blues", 10)

# --- Parsear el archivo de resumen ---
pos, D, D_alpha, mad, rechaza = [], [], [], [], []

with open(IN_TXT, "r", encoding="utf-8") as f:
    for linea in f:
        m = re.match(r"^(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(RECHAZA|NO rechaza)\s+([\d.]+)", linea)
        if m:
            pos.append(int(m.group(1)))
            D.append(float(m.group(3)))
            D_alpha.append(float(m.group(4)))
            rechaza.append(m.group(5) == "RECHAZA")
            mad.append(float(m.group(6)))

# --- Graficar ---
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
fig.patch.set_facecolor("white")

# D_stat vs D_alpha
ax = axes[0]
colores = [palette[3] if r else palette[3] for r in rechaza]
ax.bar(pos, D, color=colores, alpha=0.9, label="D estadístico")
ax.plot(pos, D_alpha, "o--", color="red", markersize=4, label="D crítico (α=0.05)")
ax.set_yscale("log")
ax.set_title("Estadístico D vs valor crítico por posición")
ax.set_xlabel("Posición")
ax.set_ylabel("D (escala log)")
ax.legend(fontsize=9)
sns.despine(ax=ax)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# MAD por posicion
ax = axes[1]
ax.bar(pos, mad, color=palette[6], alpha=0.9)
ax.set_title("MAD (desviación media absoluta) por posición")
ax.set_xlabel("Posición")
ax.set_ylabel("MAD")
sns.despine(ax=ax)
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

print(f"-> {OUT_PNG} guardado")