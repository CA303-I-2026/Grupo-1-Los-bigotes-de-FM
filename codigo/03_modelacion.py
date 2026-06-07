# 03_modelacion.py
# Pruebas estadisticas sobre los datos procesados
# Hecho por Anthonny Flores Rojas (C32975)
#
# Correr: python 03_pruebas.py

import os
import csv
import math
from collections import defaultdict
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


# Rutas de archivos procesados
ROCKYOUE         = "../datos/procesados/rockyoue.txt"
ROCKYOUEDIST     = "../datos/procesados/rockyouedist.txt"
ROCKYOUBENFORD   = "../datos/procesados/rockyoubenford.txt"
ROCKYOUMASKS     = "../datos/procesados/rockyoumasks.txt"
ROCKYOULENGTHFREQ = "../datos/procesados/rockyoulengthfreq.txt"
TOKENS           = "../datos/procesados/tokens.txt"
TOKENS_DIST = "../datos/procesados/tokens_dist_digitos.txt" 
OUT_DIR     = "../datos/procesados/graficos_ks"
OUT_TXT     = "../datos/procesados/ks_tokens_resumen.txt"
OUT              = "../datos/procesados/pruebas_resumen.txt"
palette = sns.color_palette("Blues", 5)


# Funcion para calcular Kolmogorov-Smirnov contra la Ley de Benford teorica
# Entrada: tokens_dist_digitos..txt
# Salida:  estadistico D y p-valor por posicion de chunk
def ks_benford(alpha=0.05):

    os.makedirs(OUT_DIR, exist_ok=True)

    # Formula generalizada de Benford para cada posicion
    def benford_expected(digit, pos):
        if pos == 1:
            if digit == 0:
                return 0.0
            return math.log10(1 + 1 / digit) * 100
        else:
            total = 0.0
            start = 10 ** (pos - 2)
            end   = 10 ** (pos - 1)
            for k in range(start, end):
                denom = 10 * k + digit
                total += math.log10(1 + 1 / denom)
            return total * 100

    # Leer tokens_dist_digitos.txt
    # Formato: digit, pos1, pos2, ..., posN
    posiciones = []
    digitos    = []

    with open(TOKENS_DIST, "r", encoding="utf-8") as f:
        reader   = csv.DictReader(f)
        cols     = reader.fieldnames
        pos_cols = [c for c in cols if c.startswith("pos")]

        for _ in pos_cols:
            posiciones.append([])

        for row in reader:
            digitos.append(int(row["digit"]))
            for i, col in enumerate(pos_cols):
                posiciones[i].append(int(row[col]))

    resultados = []

    for i, conteos in enumerate(posiciones):

        pos_num = i + 1  # posicion 1-indexada

        # Distribucion teorica de Benford para esta posicion especifica
        # Posicion 1: digitos 1-9 (el 0 tiene prob 0 en Benford)
        # Posicion 2+: digitos 0-9
        if pos_num == 1:
            digitos_validos = [d for d in digitos if d != 0]
        else:
            digitos_validos = digitos

        idx_validos  = [digitos.index(d) for d in digitos_validos]
        conteos_arr  = np.array(conteos, dtype=float)
        conteos_pos  = conteos_arr[idx_validos]
        total        = conteos_pos.sum()

        if total == 0:
            print(f"  Posicion {pos_num}: sin datos, saltando...")
            continue

        # Calcular prob teorica de Benford para cada digito en esta posicion
        prob_teorica_raw = np.array([benford_expected(d, pos_num) for d in digitos_validos])
        prob_teorica     = prob_teorica_raw / prob_teorica_raw.sum()  # normalizar a 1

        prob_empirica = conteos_pos / total

        # CDF empirica y teorica para KS
        cdf_empirica = np.cumsum(prob_empirica)
        cdf_teorica  = np.cumsum(prob_teorica)

        # Estadistico KS: max diferencia absoluta entre CDFs
        D = np.max(np.abs(cdf_empirica - cdf_teorica))

        # Valor critico analitico de Kolmogorov (reemplaza scipy)
        D_alpha = 1.36 / math.sqrt(total)
        rechaza = D > D_alpha
        estado  = "RECHAZA H0" if rechaza else "No rechaza H0"

        # MAD
        mad = float(np.mean(np.abs(prob_empirica - prob_teorica)))
        if mad < 0.006:
            mad_result = "Muy cercana"
        elif mad < 0.012:
            mad_result = "Aceptable"
        elif mad < 0.015:
            mad_result = "Marginal"
        else:
            mad_result = "No conformidad"

        resultados.append({
            "posicion": pos_num,
            "n":        int(total),
            "D":        D,
            "D_alpha":  D_alpha,
            "rechaza":  rechaza,
            "mad":      mad,
            "mad_result": mad_result
        })

        print(f"  Posicion {pos_num}: n = {int(total):<12} D = {D:.6f}   D_alpha = {D_alpha:.6f}   {estado:<12} MAD = {mad:.6f}   {mad_result}")

        # Grafico
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("white")

        x     = np.array(digitos_validos)
        ancho = 0.35

        # Subplot izquierdo: distribucion (PDF)
        ax1 = axes[0]
        ax1.set_facecolor("white")
        ax1.bar(x - ancho/2, prob_teorica,  width=ancho, color=palette[2],  alpha=0.7, label=f"Benford pos {pos_num}")
        ax1.bar(x + ancho/2, prob_empirica, width=ancho, color=palette[3], alpha=0.7, label="Empirica")
        ax1.set_title(f"Posicion {pos_num} — Distribucion", fontsize=13)
        ax1.set_xlabel("Digito")
        ax1.set_ylabel("Probabilidad")
        ax1.set_xticks(x)
        ax1.legend()
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Subplot derecho: CDF
        ax2 = axes[1]
        ax2.set_facecolor("white")
        ax2.step(x, cdf_teorica,  where="post", color=palette[2],  linewidth=2, label=f"CDF Benford pos {pos_num}")
        ax2.step(x, cdf_empirica, where="post", color=palette[3], linewidth=2, label="CDF Empirica")

        # Marcar punto de maxima diferencia
        idx_max = np.argmax(np.abs(cdf_empirica - cdf_teorica))
        ax2.annotate(
            f"D = {D:.4f}",
            xy=(x[idx_max], (cdf_empirica[idx_max] + cdf_teorica[idx_max]) / 2),
            fontsize=10, color="red"
        )

        ax2.set_title(f"Posicion {pos_num} — CDF  |  D = {D:.4f}  |  {estado}", fontsize=13)
        ax2.set_xlabel("Digito")
        ax2.set_ylabel("CDF")
        ax2.set_xticks(x)
        ax2.legend()
        ax2.grid(linestyle="--", alpha=0.4)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/ks_pos{pos_num}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

    # Guardar resumen txt
    with open(OUT_TXT, "w", encoding="utf-8") as f:

        f.write("=== KS contra distribucion de Benford por posicion (alpha = 5%) ===\n\n")
        f.write(f"{'Pos':<6} {'n':<14} {'D_stat':<12} {'D_alpha':<12} {'KS':<14} {'MAD':<12} {'MAD result'}\n")
        f.write("-" * 80 + "\n")

        for r in resultados:
            estado = "RECHAZA" if r["rechaza"] else "NO rechaza"
            f.write(f"{r['posicion']:<6} {r['n']:<14} {r['D']:<12.6f} {r['D_alpha']:<12.6f} {estado:<14} {r['mad']:<12.6f} {r['mad_result']}\n")

        rechazadas = sum(1 for r in resultados if r["rechaza"])
        f.write(f"\nPosiciones que rechazan H0: {rechazadas} / {len(resultados)}\n")
        f.write(f"Alpha usado: {alpha}\n")
        f.write("Nota: posicion 1 usa digitos 1-9, posiciones 2+ usan digitos 0-9\n")

    print(f"\n  -> {OUT_TXT} guardado")
    print(f"  -> Graficos en {OUT_DIR}/")


# Funcion para calcular Kruskal-Wallis sobre entropias por grupo
# Grupos: por longitud de mascara, por tipo dominante, por rango de entropia_media
# Entrada: rockyoumasks.txt
# Salida:  estadistico H y p-valor por agrupacion
def kruskal_wallis_entropias():

    OUT_KW_DIR = "../datos/procesados/graficos_kw"
    OUT_KW_TXT = "../datos/procesados/kw_entropias_resumen.txt"
    os.makedirs(OUT_KW_DIR, exist_ok=True)

    # --- Leer rockyoumasks.txt ---
    mascaras      = []
    entropias     = []
    frecuencias   = []

    with open(ROCKYOUMASKS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mascaras.append(row["mascara"])
            entropias.append(float(row["entropia_media"]))
            frecuencias.append(int(row["frecuencia"]))

    mascaras    = np.array(mascaras)
    entropias   = np.array(entropias)
    frecuencias = np.array(frecuencias)

    # Helper: expandir por frecuencia (para que el test sea representativo)
    def expandir(vals, freqs, cap=500_000):
        out = []
        for v, f in zip(vals, freqs):
            out.extend([v] * min(f, cap))
        return np.array(out, dtype=float)

    resultados_kw = []

    # ---------------------------------------------------------------
    # AGRUPACION 1: por longitud de mascara
    # ---------------------------------------------------------------
    longitudes = np.array([len(m) for m in mascaras])

    grupos_long = defaultdict(list)
    for lon, ent, frq in zip(longitudes, entropias, frecuencias):
        grupos_long[lon].append((ent, frq))

    # Conservar solo grupos con >= 2 mascaras distintas
    grupos_long_valid = {k: v for k, v in grupos_long.items() if len(v) >= 2}
    etiquetas_long    = sorted(grupos_long_valid.keys())
    muestras_long     = [expandir([e for e, _ in grupos_long_valid[k]],
                                  [f for _, f in grupos_long_valid[k]])
                         for k in etiquetas_long]

    H_long, p_long = stats.kruskal(*muestras_long)
    rechaza_long   = p_long < 0.05
    resultados_kw.append({
        "agrupacion": "Longitud de mascara",
        "n_grupos":   len(etiquetas_long),
        "H":          H_long,
        "p":          p_long,
        "rechaza":    rechaza_long
    })
    print(f"  KW Longitud:      H = {H_long:.4f}   p = {p_long:.6f}   {'RECHAZA H0' if rechaza_long else 'No rechaza H0'}")

    # Grafico boxplot longitud
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    medias = [np.mean(m) for m in muestras_long]
    ax.boxplot(muestras_long, labels=etiquetas_long, patch_artist=True,
               boxprops=dict(facecolor=palette[2], alpha=0.7),
               medianprops=dict(color="navy", linewidth=2))
    ax.plot(range(1, len(etiquetas_long) + 1), medias, "ro--", markersize=4, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por longitud de mascara\nH = {H_long:.4f}  |  p = {p_long:.6f}  |  {'RECHAZA H0' if rechaza_long else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Longitud de mascara")
    ax.set_ylabel("Entropia media")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_longitud.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    # ---------------------------------------------------------------
    # AGRUPACION 2: por tipo dominante de mascara
    #   "Solo L"  -> solo letras minusculas
    #   "Solo D"  -> solo digitos
    #   "Solo U"  -> solo letras mayusculas
    #   "Mixta"   -> combinacion de tipos
    # ---------------------------------------------------------------
    def clasificar_tipo(mascara):
        chars = set(mascara)
        if chars <= {"L"}:
            return "Solo L"
        if chars <= {"D"}:
            return "Solo D"
        if chars <= {"U"}:
            return "Solo U"
        return "Mixta"

    tipos = np.array([clasificar_tipo(m) for m in mascaras])

    grupos_tipo = defaultdict(list)
    for tip, ent, frq in zip(tipos, entropias, frecuencias):
        grupos_tipo[tip].append((ent, frq))

    etiquetas_tipo = sorted(grupos_tipo.keys())
    muestras_tipo  = [expandir([e for e, _ in grupos_tipo[k]],
                               [f for _, f in grupos_tipo[k]])
                      for k in etiquetas_tipo]

    H_tipo, p_tipo = stats.kruskal(*muestras_tipo)
    rechaza_tipo   = p_tipo < 0.05
    resultados_kw.append({
        "agrupacion": "Tipo dominante",
        "n_grupos":   len(etiquetas_tipo),
        "H":          H_tipo,
        "p":          p_tipo,
        "rechaza":    rechaza_tipo
    })
    print(f"  KW Tipo dominante: H = {H_tipo:.4f}   p = {p_tipo:.6f}   {'RECHAZA H0' if rechaza_tipo else 'No rechaza H0'}")

    # Grafico boxplot tipo
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    medias_tipo = [np.mean(m) for m in muestras_tipo]
    ax.boxplot(muestras_tipo, labels=etiquetas_tipo, patch_artist=True,
               boxprops=dict(facecolor="lightgreen", alpha=0.7),
               medianprops=dict(color="darkgreen", linewidth=2))
    ax.plot(range(1, len(etiquetas_tipo) + 1), medias_tipo, "ro--", markersize=5, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por tipo de mascara\nH = {H_tipo:.4f}  |  p = {p_tipo:.6f}  |  {'RECHAZA H0' if rechaza_tipo else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Tipo de mascara")
    ax.set_ylabel("Entropia media")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_tipo.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    # ---------------------------------------------------------------
    # AGRUPACION 3: por rango de entropia_media
    #   Baja:  < 1.5
    #   Media: 1.5 - 2.5
    #   Alta:  >= 2.5
    # ---------------------------------------------------------------
    def rango_entropia(e):
        if e < 1.5:
            return "Baja (<1.5)"
        if e < 2.5:
            return "Media (1.5-2.5)"
        return "Alta (>=2.5)"

    rangos = np.array([rango_entropia(e) for e in entropias])

    grupos_rango = defaultdict(list)
    for rng, ent, frq in zip(rangos, entropias, frecuencias):
        grupos_rango[rng].append((ent, frq))

    orden_rangos   = ["Baja (<1.5)", "Media (1.5-2.5)", "Alta (>=2.5)"]
    etiquetas_rng  = [r for r in orden_rangos if r in grupos_rango]
    muestras_rng   = [expandir([e for e, _ in grupos_rango[k]],
                               [f for _, f in grupos_rango[k]])
                      for k in etiquetas_rng]

    H_rng, p_rng = stats.kruskal(*muestras_rng)
    rechaza_rng  = p_rng < 0.05
    resultados_kw.append({
        "agrupacion": "Rango de entropia",
        "n_grupos":   len(etiquetas_rng),
        "H":          H_rng,
        "p":          p_rng,
        "rechaza":    rechaza_rng
    })
    print(f"  KW Rango entropia: H = {H_rng:.4f}   p = {p_rng:.6f}   {'RECHAZA H0' if rechaza_rng else 'No rechaza H0'}")

    # Grafico boxplot rango
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    medias_rng = [np.mean(m) for m in muestras_rng]
    ax.boxplot(muestras_rng, labels=etiquetas_rng, patch_artist=True,
               boxprops=dict(facecolor="lightsalmon", alpha=0.7),
               medianprops=dict(color="darkred", linewidth=2))
    ax.plot(range(1, len(etiquetas_rng) + 1), medias_rng, "bo--", markersize=5, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por rango\nH = {H_rng:.4f}  |  p = {p_rng:.6f}  |  {'RECHAZA H0' if rechaza_rng else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Rango de entropia")
    ax.set_ylabel("Entropia media")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_rango.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    # --- Guardar resumen txt ---
    with open(OUT_KW_TXT, "w", encoding="utf-8") as f:
        f.write("=== Kruskal-Wallis sobre entropias por agrupacion (alpha = 5%) ===\n\n")
        f.write(f"{'Agrupacion':<25} {'N grupos':<10} {'H_stat':<12} {'p-valor':<14} {'Resultado'}\n")
        f.write("-" * 75 + "\n")
        for r in resultados_kw:
            estado = "RECHAZA H0" if r["rechaza"] else "No rechaza H0"
            f.write(f"{r['agrupacion']:<25} {r['n_grupos']:<10} {r['H']:<12.4f} {r['p']:<14.6f} {estado}\n")
        f.write("\nNota: muestras expandidas por frecuencia (cap 500k por mascara)\n")

    print(f"\n  -> {OUT_KW_TXT} guardado")
    print(f"  -> Graficos en {OUT_KW_DIR}/")


# Funcion para calcular correlacion de Spearman entre longitud y entropia
# Entrada: rockyoumasks.txt
# Salida:  coeficiente rho y p-valor
def spearman_longitud_entropia():

    OUT_SP_TXT = "../datos/procesados/spearman_resumen.txt"

    # --- Leer rockyoumasks.txt ---
    longitudes  = []
    entropias   = []
    frecuencias = []

    with open(ROCKYOUMASKS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            longitudes.append(len(row["mascara"]))
            entropias.append(float(row["entropia_media"]))
            frecuencias.append(int(row["frecuencia"]))

    longitudes  = np.array(longitudes,  dtype=float)
    entropias   = np.array(entropias,   dtype=float)
    frecuencias = np.array(frecuencias, dtype=float)

    # --- Spearman sin ponderar (sobre las mascaras unicas) ---
    rho_raw, p_raw = stats.spearmanr(longitudes, entropias)

    # --- Spearman ponderado: repetir cada fila segun frecuencia (cap 200k) ---
    cap = 200_000
    lon_exp = []
    ent_exp = []
    for lon, ent, frq in zip(longitudes, entropias, frecuencias):
        rep = min(int(frq), cap)
        lon_exp.extend([lon] * rep)
        ent_exp.extend([ent] * rep)

    rho_pond, p_pond = stats.spearmanr(lon_exp, ent_exp)

    rechaza_raw  = p_raw  < 0.05
    rechaza_pond = p_pond < 0.05

    print(f"  Spearman (sin ponderar):  rho = {rho_raw:.6f}   p = {p_raw:.6f}   {'RECHAZA H0' if rechaza_raw else 'No rechaza H0'}")
    print(f"  Spearman (ponderado):     rho = {rho_pond:.6f}   p = {p_pond:.6f}   {'RECHAZA H0' if rechaza_pond else 'No rechaza H0'}")

    # --- Grafico de dispersion (puntos = mascaras unicas, size = frecuencia) ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("white")

    # Subplot izquierdo: scatter con size proporcional a frecuencia
    ax1 = axes[0]
    ax1.set_facecolor("white")
    sizes = np.sqrt(frecuencias / frecuencias.max()) * 80
    sc = ax1.scatter(longitudes, entropias, s=sizes, alpha=0.5, color="steelblue", edgecolors="none")
    # Linea de tendencia
    z = np.polyfit(longitudes, entropias, 1)
    p_fit = np.poly1d(z)
    xs = np.linspace(longitudes.min(), longitudes.max(), 200)
    ax1.plot(xs, p_fit(xs), "r--", linewidth=1.5, label="Tendencia lineal")
    ax1.set_title(f"Longitud vs Entropia (sin ponderar)\nrho = {rho_raw:.4f}  |  p = {p_raw:.6f}", fontsize=12)
    ax1.set_xlabel("Longitud de mascara")
    ax1.set_ylabel("Entropia media")
    ax1.legend()
    ax1.grid(linestyle="--", alpha=0.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Subplot derecho: entropia media por longitud (agregado)
    ax2 = axes[1]
    ax2.set_facecolor("white")
    lon_unicas = sorted(set(longitudes.astype(int)))
    medias_por_lon = []
    for l in lon_unicas:
        mask = longitudes == l
        media_pond = np.average(entropias[mask], weights=frecuencias[mask])
        medias_por_lon.append(media_pond)

    ax2.bar(lon_unicas, medias_por_lon, color="steelblue", alpha=0.7, edgecolor="white")
    ax2.set_title(f"Entropia media ponderada por longitud\nrho = {rho_pond:.4f}  |  p = {p_pond:.6f}", fontsize=12)
    ax2.set_xlabel("Longitud de mascara")
    ax2.set_ylabel("Entropia media ponderada")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig("../datos/procesados/graficos_kw/spearman_longitud_entropia.png",
                dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    # --- Guardar resumen txt ---
    with open(OUT_SP_TXT, "w", encoding="utf-8") as f:
        f.write("=== Spearman: correlacion longitud de mascara vs entropia media ===\n\n")
        f.write(f"{'Variante':<25} {'rho':<12} {'p-valor':<14} {'Resultado'}\n")
        f.write("-" * 65 + "\n")
        f.write(f"{'Sin ponderar':<25} {rho_raw:<12.6f} {p_raw:<14.6f} {'RECHAZA H0' if rechaza_raw else 'No rechaza H0'}\n")
        f.write(f"{'Ponderado':<25} {rho_pond:<12.6f} {p_pond:<14.6f} {'RECHAZA H0' if rechaza_pond else 'No rechaza H0'}\n")
        f.write("\nNota: version ponderada repite cada mascara segun su frecuencia (cap 200k)\n")
        f.write("Longitud calculada como len(mascara)\n")

    print(f"\n  -> {OUT_SP_TXT} guardado")
    print(f"  -> Grafico en ../datos/procesados/graficos_kw/spearman_longitud_entropia.png")



# Funcion para calcular intervalos de confianza por bootstrap para la entropia media
# Entrada: rockyoue.txt (columnas: password, entropyS, entropyD)
# Parametros: n_iter (iteraciones), alpha (nivel de confianza)
# Salida:  intervalo [lower, upper] para entropyS y entropyD
def bootstrap_entropia(n_iter=1000, alpha=0.05):

    OUT_BS_DIR = "../datos/procesados/graficos_bootstrap"
    OUT_BS_TXT = "../datos/procesados/bootstrap_resumen.txt"
    os.makedirs(OUT_BS_DIR, exist_ok=True)

    # --- Leer rockyoue.txt ---
    entropias_s = []
    entropias_d = []

    print("  Leyendo rockyoue.txt...")
    with open(ROCKYOUE, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entropias_s.append(float(row["entropyS"]))
                entropias_d.append(float(row["entropyD"]))
            except (ValueError, KeyError):
                continue

    entropias_s = np.array(entropias_s)
    entropias_d = np.array(entropias_d)
    n           = len(entropias_s)
    print(f"  Registros leidos: {n:,}")

    resultados_bs = []

    for nombre, datos in [("entropyS", entropias_s), ("entropyD", entropias_d)]:

        media_obs = np.mean(datos)

        # Bootstrap: remuestrear con reemplazo n_iter veces
        rng           = np.random.default_rng(seed=42)
        medias_boot   = np.array([
            np.mean(rng.choice(datos, size=n, replace=True))
            for _ in range(n_iter)
        ])

        lower = np.percentile(medias_boot, 100 * (alpha / 2))
        upper = np.percentile(medias_boot, 100 * (1 - alpha / 2))
        sesgo = np.mean(medias_boot) - media_obs

        resultados_bs.append({
            "metrica": nombre,
            "n":       n,
            "media":   media_obs,
            "lower":   lower,
            "upper":   upper,
            "sesgo":   sesgo
        })

        print(f"  {nombre}: media = {media_obs:.4f}   IC {int((1-alpha)*100)}% = [{lower:.4f}, {upper:.4f}]   sesgo = {sesgo:.6f}")

        # Grafico: histograma de distribucion bootstrap + IC
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.hist(medias_boot, bins=50, color="steelblue", alpha=0.7, edgecolor="white")
        ax.axvline(media_obs, color="navy",   linewidth=2,   linestyle="-",  label=f"Media observada = {media_obs:.4f}")
        ax.axvline(lower,     color="crimson", linewidth=1.5, linestyle="--", label=f"IC inferior = {lower:.4f}")
        ax.axvline(upper,     color="crimson", linewidth=1.5, linestyle="--", label=f"IC superior = {upper:.4f}")
        ax.fill_betweenx([0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1],
                         lower, upper, color="crimson", alpha=0.08)

        ax.set_title(f"Bootstrap — Distribucion de medias ({nombre})\n{n_iter} iteraciones  |  IC {int((1-alpha)*100)}%  |  n = {n:,}", fontsize=12)
        ax.set_xlabel(f"Media bootstrap de {nombre}")
        ax.set_ylabel("Frecuencia")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.savefig(f"{OUT_BS_DIR}/bootstrap_{nombre}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

    # Grafico comparativo: IC lado a lado
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for i, r in enumerate(resultados_bs):
        ax.errorbar(i, r["media"],
                    yerr=[[r["media"] - r["lower"]], [r["upper"] - r["media"]]],
                    fmt="o", color="steelblue", markersize=8, capsize=8, linewidth=2)
        ax.text(i, r["lower"] - 0.002, f"{r['lower']:.4f}", ha="center", fontsize=9, color="crimson")
        ax.text(i, r["upper"] + 0.001, f"{r['upper']:.4f}", ha="center", fontsize=9, color="crimson")

    ax.set_xticks([0, 1])
    ax.set_xticklabels([r["metrica"] for r in resultados_bs])
    ax.set_title(f"Intervalos de confianza bootstrap {int((1-alpha)*100)}%\npor tipo de entropia", fontsize=12)
    ax.set_ylabel("Entropia media")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUT_BS_DIR}/bootstrap_comparativo.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    # --- Guardar resumen txt ---
    with open(OUT_BS_TXT, "w", encoding="utf-8") as f:
        f.write(f"=== Bootstrap para entropia media (n_iter={n_iter}, alpha={alpha}) ===\n\n")
        f.write(f"{'Metrica':<12} {'n':<12} {'Media':<10} {'IC lower':<12} {'IC upper':<12} {'Sesgo'}\n")
        f.write("-" * 65 + "\n")
        for r in resultados_bs:
            f.write(f"{r['metrica']:<12} {r['n']:<12,} {r['media']:<10.4f} {r['lower']:<12.4f} {r['upper']:<12.4f} {r['sesgo']:.6f}\n")
        f.write(f"\nMetodo: percentil bootstrap\n")
        f.write(f"Semilla aleatoria: 42\n")

    print(f"\n  -> {OUT_BS_TXT} guardado")
    print(f"  -> Graficos en {OUT_BS_DIR}/")


# Funcion para calcular prueba de bondad de ajuste chi-cuadrado
# sobre la distribucion de caracteres por posicion
# Entrada: rockyouedist.txt  (char, pos1..pos16)
# Salida:  estadistico chi2 y p-valor por posicion
def chi2_bondad_dist_caracteres():

    OUT_CH_DIR = "../datos/procesados/graficos_chi2"
    OUT_CH_TXT = "../datos/procesados/chi2_dist_resumen.txt"
    os.makedirs(OUT_CH_DIR, exist_ok=True)

    # --- Leer rockyouedist.txt ---
    chars      = []
    posiciones = []   # lista de listas: posiciones[i] = conteos de cada char en pos i+1

    with open(ROCKYOUEDIST, "r", encoding="latin-1") as f:
        reader   = csv.DictReader(f)
        cols     = reader.fieldnames
        pos_cols = [c for c in cols if c.startswith("pos")]

        for _ in pos_cols:
            posiciones.append([])

        for row in reader:
            chars.append(row["char"] if row["char"] != "" else "<space>")
            for i, col in enumerate(pos_cols):
                posiciones[i].append(int(row[col]))

    resultados = []

    for i, conteos in enumerate(posiciones):

        pos_num     = i + 1
        conteos_arr = np.array(conteos, dtype=float)
        total       = conteos_arr.sum()

        if total == 0:
            print(f"  Posicion {pos_num}: sin datos, saltando...")
            continue

        # H0: distribucion uniforme entre los caracteres que aparecen en esta posicion
        # Solo incluir chars con conteo > 0 (evitar celdas vacias que inflan chi2)
        mask        = conteos_arr > 0
        conteos_obs = conteos_arr[mask]
        n_cats      = mask.sum()

        if n_cats < 2:
            print(f"  Posicion {pos_num}: menos de 2 categorias, saltando...")
            continue

        esperado    = np.full(n_cats, total / n_cats)   # uniforme
        chi2_stat, p_val = stats.chisquare(conteos_obs, f_exp=esperado)
        rechaza     = p_val < 0.05
        estado      = "RECHAZA H0" if rechaza else "No rechaza H0"
        gl          = int(n_cats - 1)

        resultados.append({
            "posicion": pos_num,
            "n":        int(total),
            "n_cats":   int(n_cats),
            "gl":       gl,
            "chi2":     chi2_stat,
            "p":        p_val,
            "rechaza":  rechaza
        })

        print(f"  Posicion {pos_num}: n = {int(total):<10,} cats = {int(n_cats):<5} chi2 = {chi2_stat:.2f}   p = {p_val:.6f}   {estado}")

        # Grafico: top 20 caracteres mas frecuentes en esta posicion
        chars_arr  = np.array(chars)
        top_idx    = np.argsort(conteos_arr)[::-1][:20]
        top_chars  = chars_arr[top_idx]
        top_counts = conteos_arr[top_idx]
        top_esp    = np.full(len(top_idx), total / n_cats)

        fig, ax = plt.subplots(figsize=(13, 5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        x     = np.arange(len(top_chars))
        ancho = 0.35
        ax.bar(x - ancho/2, top_counts / total, width=ancho, color="steelblue",  alpha=0.7, label="Empirica")
        ax.bar(x + ancho/2, top_esp    / total, width=ancho, color="lightsalmon", alpha=0.7, label="Uniforme esperada")
        ax.set_title(f"Posicion {pos_num} — Top 20 caracteres\nchi2 = {chi2_stat:.2f}  |  gl = {gl}  |  p = {p_val:.6f}  |  {estado}", fontsize=12)
        ax.set_xlabel("Caracter")
        ax.set_ylabel("Proporcion")
        ax.set_xticks(x)
        ax.set_xticklabels([repr(c)[1:-1] if len(repr(c)) > 3 else c for c in top_chars], fontsize=8)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.savefig(f"{OUT_CH_DIR}/chi2_dist_pos{pos_num}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

    # --- Guardar resumen txt ---
    with open(OUT_CH_TXT, "w", encoding="utf-8") as f:
        f.write("=== Chi-cuadrado bondad de ajuste: distribucion de caracteres por posicion ===\n")
        f.write("H0: distribucion uniforme entre caracteres presentes en esa posicion\n\n")
        f.write(f"{'Pos':<6} {'n':<14} {'Cats':<8} {'GL':<6} {'chi2':<14} {'p-valor':<14} {'Resultado'}\n")
        f.write("-" * 75 + "\n")
        for r in resultados:
            estado = "RECHAZA H0" if r["rechaza"] else "No rechaza H0"
            f.write(f"{r['posicion']:<6} {r['n']:<14,} {r['n_cats']:<8} {r['gl']:<6} {r['chi2']:<14.2f} {r['p']:<14.6f} {estado}\n")

        rechazadas = sum(1 for r in resultados if r["rechaza"])
        f.write(f"\nPosiciones que rechazan H0: {rechazadas} / {len(resultados)}\n")
        f.write("Nota: solo se incluyen caracteres con conteo > 0 en cada posicion\n")

    print(f"\n  -> {OUT_CH_TXT} guardado")
    print(f"  -> Graficos en {OUT_CH_DIR}/")


# Funcion para calcular prueba chi-cuadrado contra Benford teorico
# Entrada: tokens_dist_digitos.txt  (digit, pos1..posN)
# Salida:  estadistico chi2 y p-valor por posicion de chunk
def chi2_benford():

    OUT_CB_TXT = "../datos/procesados/chi2_benford_resumen.txt"
    OUT_CB_DIR = "../datos/procesados/graficos_chi2"
    os.makedirs(OUT_CB_DIR, exist_ok=True)

    # Formula generalizada de Benford (reutilizada de ks_benford)
    def benford_expected(digit, pos):
        if pos == 1:
            if digit == 0:
                return 0.0
            return math.log10(1 + 1 / digit) * 100
        else:
            total = 0.0
            start = 10 ** (pos - 2)
            end   = 10 ** (pos - 1)
            for k in range(start, end):
                denom = 10 * k + digit
                total += math.log10(1 + 1 / denom)
            return total * 100

    # --- Leer tokens_dist_digitos.txt ---
    posiciones = []
    digitos    = []

    with open(ROCKYOUE, "r", encoding="latin-1") as f:
        reader   = csv.DictReader(f)
        cols     = reader.fieldnames
        pos_cols = [c for c in cols if c.startswith("pos")]

        for _ in pos_cols:
            posiciones.append([])

        for row in reader:
            digitos.append(int(row["digit"]))
            for i, col in enumerate(pos_cols):
                posiciones[i].append(int(row[col]))

    resultados = []

    for i, conteos in enumerate(posiciones):

        pos_num = i + 1

        if pos_num == 1:
            digitos_validos = [d for d in digitos if d != 0]
        else:
            digitos_validos = digitos

        idx_validos  = [digitos.index(d) for d in digitos_validos]
        conteos_arr  = np.array(conteos, dtype=float)
        conteos_pos  = conteos_arr[idx_validos]
        total        = conteos_pos.sum()

        if total == 0:
            print(f"  Posicion {pos_num}: sin datos, saltando...")
            continue

        # Frecuencias esperadas segun Benford
        prob_teorica_raw = np.array([benford_expected(d, pos_num) for d in digitos_validos])
        prob_teorica     = prob_teorica_raw / prob_teorica_raw.sum()
        esperado         = prob_teorica * total

        # Fusionar celdas con esperado < 5 (requisito de chi2)
        # Agrupar desde los extremos hacia el centro si es necesario
        obs_merged = []
        exp_merged = []
        buffer_obs = 0.0
        buffer_exp = 0.0

        for obs_val, exp_val in zip(conteos_pos, esperado):
            buffer_obs += obs_val
            buffer_exp += exp_val
            if buffer_exp >= 5:
                obs_merged.append(buffer_obs)
                exp_merged.append(buffer_exp)
                buffer_obs = 0.0
                buffer_exp = 0.0

        # Absorber remanente en la ultima celda
        if buffer_exp > 0 and obs_merged:
            obs_merged[-1] += buffer_obs
            exp_merged[-1] += buffer_exp

        obs_merged = np.array(obs_merged)
        exp_merged = np.array(exp_merged)
        gl         = len(obs_merged) - 1

        if gl < 1:
            print(f"  Posicion {pos_num}: grados de libertad insuficientes, saltando...")
            continue

        chi2_stat = float(np.sum((obs_merged - exp_merged) ** 2 / exp_merged))
        p_val     = 1 - stats.chi2.cdf(chi2_stat, df=gl)
        rechaza   = p_val < 0.05
        estado    = "RECHAZA H0" if rechaza else "No rechaza H0"

        resultados.append({
            "posicion": pos_num,
            "n":        int(total),
            "gl":       gl,
            "chi2":     chi2_stat,
            "p":        p_val,
            "rechaza":  rechaza
        })

        print(f"  Posicion {pos_num}: n = {int(total):<12,} gl = {gl:<4} chi2 = {chi2_stat:.4f}   p = {p_val:.6f}   {estado}")

        # Grafico comparativo empirico vs Benford
        x            = np.array(digitos_validos)
        prob_emp     = conteos_pos / total
        ancho        = 0.35

        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.bar(x - ancho/2, prob_teorica, width=ancho, color="skyblue",   alpha=0.7, label=f"Benford pos {pos_num}")
        ax.bar(x + ancho/2, prob_emp,     width=ancho, color="lightgreen", alpha=0.7, label="Empirica")
        ax.set_title(f"Posicion {pos_num} — Chi2 vs Benford\nchi2 = {chi2_stat:.4f}  |  gl = {gl}  |  p = {p_val:.6f}  |  {estado}", fontsize=12)
        ax.set_xlabel("Digito")
        ax.set_ylabel("Probabilidad")
        ax.set_xticks(x)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.savefig(f"{OUT_CB_DIR}/chi2_benford_pos{pos_num}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

    # --- Guardar resumen txt ---
    with open(OUT_CB_TXT, "w", encoding="utf-8") as f:
        f.write("=== Chi-cuadrado contra distribucion de Benford por posicion (alpha = 5%) ===\n\n")
        f.write(f"{'Pos':<6} {'n':<14} {'GL':<6} {'chi2':<14} {'p-valor':<14} {'Resultado'}\n")
        f.write("-" * 65 + "\n")
        for r in resultados:
            estado = "RECHAZA H0" if r["rechaza"] else "No rechaza H0"
            f.write(f"{r['posicion']:<6} {r['n']:<14,} {r['gl']:<6} {r['chi2']:<14.4f} {r['p']:<14.6f} {estado}\n")

        rechazadas = sum(1 for r in resultados if r["rechaza"])
        f.write(f"\nPosiciones que rechazan H0: {rechazadas} / {len(resultados)}\n")
        f.write("Nota: celdas con frecuencia esperada < 5 fueron fusionadas antes del test\n")
        f.write("Nota: posicion 1 usa digitos 1-9, posiciones 2+ usan digitos 0-9\n")

    print(f"\n  -> {OUT_CB_TXT} guardado")
    print(f"  -> Graficos en {OUT_CB_DIR}/")



# main
if __name__ == "__main__":

    print("=== Pruebas estadisticas ===\n")

    # Metodos no parametricos
    print("Calculando KS contra Benford...")
    ks_benford(0.1)

    print("Calculando Kruskal-Wallis sobre entropias...")
    kruskal_wallis_entropias()

    print("Calculando Spearman longitud vs entropia...")
    spearman_longitud_entropia()

    print("Calculando Bootstrap para entropia media...")
    bootstrap_entropia(n_iter=1000, alpha=0.05)

    print("Calculando Chi-cuadrado bondad de ajuste por posicion...")
    chi2_bondad_dist_caracteres()

    print("Calculando Chi-cuadrado contra Benford...")
    chi2_benford()