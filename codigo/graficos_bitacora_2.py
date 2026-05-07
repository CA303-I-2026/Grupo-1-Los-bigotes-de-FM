

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
# =========================
# Estilo Bigotes
# =========================

# Estilo general
sns.set_theme(style="ticks")

# Paleta de colores
sns.set_palette("Blues")

# Configuración de tipografía
plt.rcParams.update({
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13
})

#Lectura de archivos
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
benford = pd.read_csv("../datos/procesados/rockyoubenford.txt")
edist   = pd.read_csv("../datos/procesados/rockyouedist.txt", quoting=3)

#Transformacion a formato Tidy

# Tidy: rockyoubenford 
benford_tidy = benford.melt(
    id_vars    = "digit",
    var_name   = "chunk",
    value_name = "frecuencia"
)

# Tidy: rockyouedist
edist_tidy = edist.melt(
    id_vars    = "char",
    var_name   = "posicion",
    value_name = "frecuencia"
)

edist_tidy["posicion_num"] = edist_tidy["posicion"].str.extract(r"(\d+)").astype(int)

# Verificación
def tabla_a_png(df, ruta, titulo=""):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axis("off")
    tabla = ax.table(
        cellText    = df.values,
        colLabels   = df.columns,
        cellLoc     = "center",
        loc         = "center"
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.auto_set_column_width(col=list(range(len(df.columns))))
    if titulo:
        plt.title(titulo, fontsize=12, pad=10)
    plt.savefig(ruta, bbox_inches="tight", dpi=150)
    plt.close()

tabla_a_png(benford_tidy.head(10), "../bitacoras/bitacora_2/figuras/benford_tidy_muestra.png", "rockyoubenford (tidy)")
tabla_a_png(edist_tidy.head(10),   "../bitacoras/bitacora_2/figuras/edist_tidy_muestra.png",  "rockyouedist (tidy)")

# CUADROS RESUMEN
def tabla_a_png(df, ruta, titulo="", figsize=(10, 3)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    # Convertir a enteros si es posible
    df = df.copy()
    for col in df.select_dtypes(include="float").columns:
        df[col] = df[col].astype(int)
    tabla = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.auto_set_column_width(col=list(range(len(df.columns))))
    if titulo: plt.title(titulo, fontsize=12, pad=10)
    plt.savefig(ruta, bbox_inches="tight", dpi=150)
    plt.close()

# Cuadro 1
cuadro1 = benford_tidy.groupby("digit")["frecuencia"].agg(Media="mean", Mediana="median", Minimo="min", Maximo="max", Total="sum").reset_index().round(0)
cuadro1.columns = ["Dígito", "Media", "Mediana", "Mínimo", "Máximo", "Total"]
tabla_a_png(cuadro1, "../bitacoras/bitacora_2/figuras/cuadro1_benford.png", "Cuadro 1: Estadísticas descriptivas de frecuencia por dígito")

# Cuadro 2
cuadro2 = edist_tidy.groupby("posicion_num")["frecuencia"].agg(Media="mean", Mediana="median", Minimo="min", Maximo="max", Total="sum").reset_index().round(0)
cuadro2.columns = ["Posición", "Media", "Mediana", "Mínimo", "Máximo", "Total"]
tabla_a_png(cuadro2, "../bitacoras/bitacora_2/figuras/cuadro2_posicion.png", "Cuadro 2: Estadísticas descriptivas de frecuencia por posición", figsize=(12, 4))

# Cuadro 3
cuadro3 = edist_tidy[edist_tidy["posicion_num"] == 1].nlargest(10, "frecuencia")[["char", "frecuencia"]].reset_index(drop=True)
cuadro3.columns = ["Carácter", "Frecuencia"]
tabla_a_png(cuadro3, "../bitacoras/bitacora_2/figuras/cuadro3_top10.png", "Cuadro 3: Top 10 caracteres más frecuentes en la primera posición", figsize=(6, 4))


#Graficos

# Listas de referencia
digitos = [str(d) for d in range(10)]
letras  = list("abcdefghijklmnopqrstuvwxyz")

# --- Gráfico 1: Frecuencia del primer dígito vs. Ley de Benford ---
chunk1 = benford_tidy[benford_tidy["chunk"] == "chunk1"].copy()
total_chunk1 = chunk1["frecuencia"].sum()
chunk1["pct_observado"] = chunk1["frecuencia"] / total_chunk1 * 100
chunk1["pct_benford"] = chunk1["digit"].apply(
    lambda d: np.log10(1 + 1 / d) * 100 if d != 0 else np.nan
)
g1_long = chunk1.melt(
    id_vars    = "digit",
    value_vars = ["pct_observado", "pct_benford"],
    var_name   = "tipo",
    value_name = "porcentaje"
)
g1_long["tipo"] = g1_long["tipo"].map({
    "pct_observado": "RockYou observado",
    "pct_benford":   "Ley de Benford teórica"
})
plt.figure(figsize=(10, 6))
sns.barplot(data=g1_long, x="digit", y="porcentaje", hue="tipo", palette="Blues")
plt.title("Gráfico 1: Frecuencia del primer dígito vs. Ley de Benford")
plt.xlabel("Dígito")
plt.ylabel("Frecuencia (%)")
plt.legend(title="")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico1_benford.png", dpi=150)
plt.close()

# --- Gráfico 2: Proporción de letras, dígitos y otros por posición ---
otros = [c for c in edist_tidy["char"].unique() if c not in letras and c not in digitos]

def clasificar(char):
    if char in letras:
        return "Letra"
    elif char in digitos:
        return "Dígito"
    else:
        return "Otro"

edist_tidy["tipo_char"] = edist_tidy["char"].apply(clasificar)

g2 = edist_tidy.groupby(["posicion_num", "tipo_char"])["frecuencia"].sum().reset_index()
total_por_pos = g2.groupby("posicion_num")["frecuencia"].transform("sum")
g2["pct"] = g2["frecuencia"] / total_por_pos * 100

plt.figure(figsize=(12, 6))
sns.barplot(data=g2, x="posicion_num", y="pct", hue="tipo_char",
            palette="Blues", edgecolor="white")
plt.title("Gráfico 2: Proporción de letras, dígitos y otros caracteres por posición")
plt.xlabel("Posición")
plt.ylabel("Proporción (%)")
plt.xticks(range(0, 16), range(1, 17))
plt.legend(title="Tipo de carácter")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico2_prop_tipo_posicion.png", dpi=150)
plt.close()

# --- Gráfico 3: Top 10 caracteres más frecuentes en la segunda posición ---
g3 = edist_tidy[edist_tidy["posicion_num"] == 2].nlargest(10, "frecuencia")
plt.figure(figsize=(10, 6))
sns.barplot(data=g3, y="char", x="frecuencia",
            hue="char", palette="Blues_d", legend=False)
plt.title("Gráfico 3: Top 10 caracteres más frecuentes en la segunda posición")
plt.xlabel("Frecuencia")
plt.ylabel("Carácter")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico3_top10_pos2.png", dpi=150)
plt.close()

# --- Gráfico 4: Top 10 caracteres más frecuentes en la primera posición ---
g4 = edist_tidy[edist_tidy["posicion_num"] == 1].nlargest(10, "frecuencia")
plt.figure(figsize=(10, 6))
sns.barplot(data=g4, y="char", x="frecuencia",
            hue="char", palette="Blues_d", legend=False)
plt.title("Gráfico 4: Top 10 caracteres más frecuentes en la primera posición")
plt.xlabel("Frecuencia")
plt.ylabel("Carácter")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico4_top10_pos1.png", dpi=150)
plt.close()

# --- Gráfico 5: Composición relativa de dígitos por chunk (normalizado) ---
benford_tidy["chunk_num"] = benford_tidy["chunk"].str.extract(r"(\d+)").astype(int)
total_por_chunk            = benford_tidy.groupby("chunk_num")["frecuencia"].transform("sum")
benford_tidy["pct"]        = benford_tidy["frecuencia"] / total_por_chunk * 100
benford_tidy["digit_str"]  = benford_tidy["digit"].astype(str)
plt.figure(figsize=(12, 6))
sns.lineplot(data=benford_tidy, x="chunk_num", y="pct",
             hue="digit_str", marker="o", palette="Blues")
plt.title("Gráfico 5: Composición relativa de dígitos por chunk (%)")
plt.xlabel("Chunk")
plt.ylabel("Proporción (%)")
plt.xticks(range(1, 9))
plt.legend(title="Dígito", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico5_chunks_norm.png", dpi=150)
plt.close()

# --- Gráfico 6a: Evolución por posición — top 3 letras ---
top3_letras = (
    edist_tidy[edist_tidy["char"].isin(letras)]
    .groupby("char")["frecuencia"].sum()
    .nlargest(3).index
)
g6a = edist_tidy[edist_tidy["char"].isin(top3_letras)]
plt.figure(figsize=(12, 6))
sns.lineplot(data=g6a, x="posicion_num", y="frecuencia",
             hue="char", marker="o", palette="Blues")
plt.title("Gráfico 6a: Evolución por posición — top 3 letras")
plt.xlabel("Posición")
plt.ylabel("Frecuencia")
plt.xticks(range(1, 17))
plt.legend(title="Letra", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico6a_top3_letras.png", dpi=150)
plt.close()

# --- Gráfico 6b: Evolución por posición — top 3 dígitos ---
top3_digitos = (
    edist_tidy[edist_tidy["char"].isin(digitos)]
    .groupby("char")["frecuencia"].sum()
    .nlargest(3).index
)
g6b = edist_tidy[edist_tidy["char"].isin(top3_digitos)]
plt.figure(figsize=(12, 6))
sns.lineplot(data=g6b, x="posicion_num", y="frecuencia",
             hue="char", marker="o", palette="Blues")
plt.title("Gráfico 6b: Evolución por posición — top 3 dígitos")
plt.xlabel("Posición")
plt.ylabel("Frecuencia")
plt.xticks(range(1, 17))
plt.legend(title="Dígito", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("../bitacoras/bitacora_2/figuras/grafico6b_top3_digitos.png", dpi=150)
plt.close()

print("Gráficos guardados ✓")