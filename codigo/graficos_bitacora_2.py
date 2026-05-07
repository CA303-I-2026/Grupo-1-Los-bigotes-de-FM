

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
