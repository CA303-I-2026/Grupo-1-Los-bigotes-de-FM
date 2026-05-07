

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

tabla_a_png(benford_tidy.head(10), "../proyecto_final/figuras/benford_tidy_muestra.png", "rockyoubenford (tidy)")
tabla_a_png(edist_tidy.head(10),   "../proyecto_final/figuras/edist_tidy_muestra.png",  "rockyouedist (tidy)")


