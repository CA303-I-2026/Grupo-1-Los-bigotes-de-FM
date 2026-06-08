# 03_modelacion.py
# Pruebas estadisticas sobre los datos procesados
# Hecho por Anthonny Flores Rojas (C32975)
#
# Correr: python 03_pruebas.py

# Librerias
import os
import csv
import math
from collections import defaultdict
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


ROCKYOUE          = "../datos/procesados/rockyoue.txt"
ROCKYOUEDIST      = "../datos/procesados/rockyouedist.txt"
ROCKYOUBENFORD    = "../datos/procesados/rockyoubenford.txt"
ROCKYOUMASKS      = "../datos/procesados/rockyoumasks.txt"
ROCKYOULENGTHFREQ = "../datos/procesados/rockyoulengthfreq.txt"
TOKENS            = "../datos/procesados/tokens.txt"
TOKENS_DIST       = "../datos/procesados/tokens_dist_digitos.txt"
OUT_DIR           = "../datos/procesados/graficos_ks"
OUT_TXT           = "../datos/procesados/ks_tokens_resumen.txt"
OUT               = "../datos/procesados/pruebas_resumen.txt"
palette           = sns.color_palette("Blues", 10)



def ks_benford(alpha=0.05):
    """
    Calcula el estadistico Kolmogorov-Smirnov comparando la distribucion empirica
    de digitos en tokens contra la distribucion teorica de Benford por posicion.

    Args:
        alpha (float): Nivel de significancia para el valor critico de Kolmogorov.
                       Por defecto 0.05.

    Returns:
        None: Guarda graficos PNG por posicion y un resumen en texto plano.

    Example:
        >>> ks_benford(alpha=0.05)
        Posicion 1: n = 3248901     D = 0.012400   D_alpha = 0.000754   RECHAZA H0   MAD = 0.008100   Aceptable

    Notes:
        Usa la formula generalizada de Benford para calcular la probabilidad esperada
        de cada digito en cada posicion. El valor critico D_alpha se calcula
        analiticamente como 1.36 / sqrt(n), reemplazando scipy para evitar
        dependencias adicionales. La MAD clasifica la conformidad en cuatro niveles:
        Muy cercana, Aceptable, Marginal y No conformidad.
    """

    os.makedirs(OUT_DIR, exist_ok=True)

    def benford_expected(digit, pos):
        """
        Calcula la probabilidad esperada segun Benford para un digito en una posicion dada.

        Args:
            digit (int): Digito del 0 al 9.
            pos   (int): Posicion (1-indexada).

        Returns:
            float: Probabilidad esperada en porcentaje (0-100).
        """
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

        prob_teorica_raw = np.array([benford_expected(d, pos_num) for d in digitos_validos])
        prob_teorica     = prob_teorica_raw / prob_teorica_raw.sum()
        prob_empirica    = conteos_pos / total

        cdf_empirica = np.cumsum(prob_empirica)
        cdf_teorica  = np.cumsum(prob_teorica)

        D       = np.max(np.abs(cdf_empirica - cdf_teorica))
        D_alpha = 1.36 / math.sqrt(total)
        rechaza = D > D_alpha
        estado  = "RECHAZA H0" if rechaza else "No rechaza H0"

        mad = float(np.mean(np.abs(prob_empirica - prob_teorica)))

        resultados.append({
            "posicion":   pos_num,
            "n":          int(total),
            "D":          D,
            "D_alpha":    D_alpha,
            "rechaza":    rechaza,
            "mad":        mad
        })

        print(f"  Posicion {pos_num}: n = {int(total):<12} D = {D:.6f}   D_alpha = {D_alpha:.6f}   {estado:<12} MAD = {mad:.6f}   {mad}")

        x     = np.array(digitos_validos)
        ancho = 0.35

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("white")

        ax1 = axes[0]
        ax1.set_facecolor("white")
        ax1.bar(x - ancho/2, prob_teorica,  width=ancho, color=palette[4], alpha=0.85, label=f"Benford pos {pos_num}")
        ax1.bar(x + ancho/2, prob_empirica, width=ancho, color=palette[9], alpha=0.85, label="Empirica")
        ax1.set_title(f"Posicion {pos_num} — Distribucion", fontsize=13)
        ax1.set_xlabel("Digito")
        ax1.set_ylabel("Probabilidad")
        ax1.set_xticks(x)
        ax1.legend()
        sns.despine(ax=ax1)
        ax1.grid(axis="y", linestyle="--", alpha=0.4)

        ax2 = axes[1]
        ax2.set_facecolor("white")
        ax2.step(x, cdf_teorica,  where="post", color=palette[4], linewidth=2, label=f"CDF Benford pos {pos_num}")
        ax2.step(x, cdf_empirica, where="post", color=palette[9], linewidth=2, label="CDF Empirica")

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
        sns.despine(ax=ax2)
        ax2.grid(linestyle="--", alpha=0.4)

        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/ks_pos{pos_num}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

    with open(OUT_TXT, "w", encoding="utf-8") as f:

        f.write("=== KS contra distribucion de Benford por posicion (alpha = 5%) ===\n\n")
        f.write(f"{'Pos':<6} {'n':<14} {'D_stat':<12} {'D_alpha':<12} {'KS':<14} {'MAD':<12} {'MAD result'}\n")
        f.write("-" * 80 + "\n")

        for r in resultados:
            estado = "RECHAZA" if r["rechaza"] else "NO rechaza"
            f.write(f"{r['posicion']:<6} {r['n']:<14} {r['D']:<12.6f} {r['D_alpha']:<12.6f} {estado:<14} {r['mad']:<12.6f}\n")

        rechazadas = sum(1 for r in resultados if r["rechaza"])
        f.write(f"\nPosiciones que rechazan H0: {rechazadas} / {len(resultados)}\n")
        f.write(f"Alpha usado: {alpha}\n")
        f.write("Nota: posicion 1 usa digitos 1-9, posiciones 2+ usan digitos 0-9\n")

    print(f"\n  -> {OUT_TXT} guardado")
    print(f"  -> Graficos en {OUT_DIR}/")



def kruskal_wallis_entropias(cap_expand = 500000):
    """
    Calcula la prueba de Kruskal-Wallis sobre las entropias medias de las mascaras
    agrupadas por tres criterios: longitud de mascara, tipo dominante de caracteres
    y rango de entropia media.

    Args:
        None

    Returns:
        None: Guarda graficos boxplot por agrupacion y un resumen en texto plano.

    Example:
        >>> kruskal_wallis_entropias()
        KW Longitud:       H = 48231.2100   p = 0.000000   RECHAZA H0
        KW Tipo dominante: H = 12045.8800   p = 0.000000   RECHAZA H0
        KW Rango entropia: H = 11746760.06  p = 0.000000   RECHAZA H0

    Notes:
        Las muestras se expanden por frecuencia (hasta un cap de 500k por mascara)
        para que el test pondere correctamente las mascaras mas comunes.
        Los tipos dominantes son: Solo L (solo minusculas), Solo D (solo digitos),
        Solo U (solo mayusculas) y Mixta (combinacion de tipos).
        El resultado de la agrupacion por rango de entropia es trivialmente
        significativo por construccion y debe interpretarse solo como descriptivo.
    """

    OUT_KW_DIR = "../datos/procesados/graficos_kw"
    OUT_KW_TXT = "../datos/procesados/kw_entropias_resumen.txt"
    os.makedirs(OUT_KW_DIR, exist_ok=True)

    mascaras    = []
    entropias   = []
    frecuencias = []

    with open(ROCKYOUMASKS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mascaras.append(row["mascara"])
            entropias.append(float(row["entropia_media"]))
            frecuencias.append(int(row["frecuencia"]))

    mascaras    = np.array(mascaras)
    entropias   = np.array(entropias)
    frecuencias = np.array(frecuencias)

    def expandir(vals, freqs, cap=500_000):
        """
        Expande una lista de valores repitiendolos segun su frecuencia asociada.

        Args:
            vals (list[float]): Valores a expandir.
            freqs (list[int]):  Frecuencias correspondientes.
            cap (int):          Limite maximo de repeticiones por valor. Por defecto 500000.

        Returns:
            numpy.ndarray: Array expandido de floats.
        """
        out = []
        for v, f in zip(vals, freqs):
            out.extend([v] * min(f, cap))
        return np.array(out, dtype=float)

    resultados_kw = []

    longitudes  = np.array([len(m) for m in mascaras])
    grupos_long = defaultdict(list)

    for lon, ent, frq in zip(longitudes, entropias, frecuencias):
        grupos_long[lon].append((ent, frq))

    grupos_long_valid = {k: v for k, v in grupos_long.items() if len(v) >= 2}
    etiquetas_long    = sorted(grupos_long_valid.keys())
    muestras_long = [expandir([e for e, _ in grupos_long_valid[k]],
                           [f for _, f in grupos_long_valid[k]], cap_expand)
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

    medias     = [np.mean(m) for m in muestras_long]
    df_long    = {"longitud": [], "entropia": []}
    for k, m in zip(etiquetas_long, muestras_long):
        df_long["longitud"].extend([k] * len(m))
        df_long["entropia"].extend(m.tolist())

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("white")
    sns.boxplot(x=df_long["longitud"], y=df_long["entropia"],
                palette="Blues", ax=ax, linewidth=0.8, fliersize=1)
    ax.plot(range(len(etiquetas_long)), medias, "o--",
            color=palette[4], markersize=4, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por longitud de mascara\nH = {H_long:.4f}  |  p = {p_long:.6f}  |  {'RECHAZA H0' if rechaza_long else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Longitud de mascara")
    ax.set_ylabel("Entropia media")
    ax.legend()
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_longitud.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    def clasificar_tipo(mascara):
        """
        Clasifica una mascara segun el tipo dominante de sus caracteres.

        Args:
            mascara (str): Cadena de caracteres tipo mascara (ej. 'LLLDDD').

        Returns:
            str: Una de las etiquetas: 'Solo L', 'Solo D', 'Solo U' o 'Mixta'.
        """
        chars = set(mascara)
        if chars <= {"L"}:
            return "Solo L"
        if chars <= {"D"}:
            return "Solo D"
        if chars <= {"U"}:
            return "Solo U"
        if chars <= {"S"}:
            return "Solo S"
        return "Mixta"

    tipos       = np.array([clasificar_tipo(m) for m in mascaras])
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

    medias_tipo = [np.mean(m) for m in muestras_tipo]
    df_tipo     = {"tipo": [], "entropia": []}
    for k, m in zip(etiquetas_tipo, muestras_tipo):
        df_tipo["tipo"].extend([k] * len(m))
        df_tipo["entropia"].extend(m.tolist())

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    sns.boxplot(x=df_tipo["tipo"], y=df_tipo["entropia"],
                palette="Blues", ax=ax, linewidth=0.8, fliersize=1)
    ax.plot(range(len(etiquetas_tipo)), medias_tipo, "o--",
            color=palette[4], markersize=5, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por tipo de mascara\nH = {H_tipo:.4f}  |  p = {p_tipo:.6f}  |  {'RECHAZA H0' if rechaza_tipo else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Tipo de mascara")
    ax.set_ylabel("Entropia media")
    ax.legend()
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_tipo.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    def rango_entropia(e):
        """
        Clasifica un valor de entropia en uno de tres rangos predefinidos.

        Args:
            e (float): Valor de entropia media.

        Returns:
            str: Etiqueta del rango: 'Baja (<2.4464)', 'Media (2.4464-2.9477)' o 'Alta (>=2.9477)'.
        """
        if e < 2.4464:
            return "Baja (<2.4464)"
        if e < 2.9477:
            return "Media (2.4464-2.9477)"
        return "Alta (>=2.9477)"

    rangos       = np.array([rango_entropia(e) for e in entropias])
    grupos_rango = defaultdict(list)

    for rng, ent, frq in zip(rangos, entropias, frecuencias):
        grupos_rango[rng].append((ent, frq))

    orden_rangos  = ["Baja (<2.4464)", "Media (2.4464-2.9477)", "Alta (>=2.9477)"]
    etiquetas_rng = [r for r in orden_rangos if r in grupos_rango]
    muestras_rng  = [expandir([e for e, _ in grupos_rango[k]],
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

    medias_rng = [np.mean(m) for m in muestras_rng]
    df_rng     = {"rango": [], "entropia": []}
    for k, m in zip(etiquetas_rng, muestras_rng):
        df_rng["rango"].extend([k] * len(m))
        df_rng["entropia"].extend(m.tolist())

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    sns.boxplot(x=df_rng["rango"], y=df_rng["entropia"],
                palette="Blues", order=etiquetas_rng, ax=ax, linewidth=0.8, fliersize=1)
    ax.plot(range(len(etiquetas_rng)), medias_rng, "o--",
            color=palette[4], markersize=5, label="Media")
    ax.set_title(f"Kruskal-Wallis — Entropia por rango\nH = {H_rng:.4f}  |  p = {p_rng:.6f}  |  {'RECHAZA H0' if rechaza_rng else 'No rechaza H0'}", fontsize=12)
    ax.set_xlabel("Rango de entropia")
    ax.set_ylabel("Entropia media")
    ax.legend()
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(f"{OUT_KW_DIR}/kw_rango.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

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


def spearman_longitud_entropia(cap_spear = 200_000):
    """
    Calcula la correlacion de Spearman entre la longitud de la mascara y su
    entropia media, en dos variantes: sin ponderar (una observacion por mascara)
    y ponderada (cada mascara repetida segun su frecuencia).

    Args:
        None

    Returns:
        None: Guarda un grafico de dispersion con tendencia y un resumen en texto plano.

    Example:
        >>> spearman_longitud_entropia()
        Spearman (sin ponderar):  rho = 0.701254   p = 0.000000   RECHAZA H0
        Spearman (ponderado):     rho = 0.884739   p = 0.000000   RECHAZA H0

    Notes:
        La longitud se calcula como len(mascara). La version ponderada repite cada
        mascara hasta un cap de 200k repeticiones para evitar desbordamiento de memoria.
        Un rho positivo indica que mascaras mas largas tienden a tener mayor entropia.
    """

    OUT_SP_TXT = "../datos/procesados/spearman_resumen.txt"

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

    rho_raw, p_raw = stats.spearmanr(longitudes, entropias)

    cap = cap_spear
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

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("white")

    ax1   = axes[0]
    sizes = np.sqrt(frecuencias / frecuencias.max()) * 80

    sns.scatterplot(x=longitudes, y=entropias, size=sizes, sizes=(5, 80),
                    color=palette[3], alpha=0.5, edgecolor="none", legend=False, ax=ax1)

    z     = np.polyfit(longitudes, entropias, 1)
    p_fit = np.poly1d(z)
    xs    = np.linspace(longitudes.min(), longitudes.max(), 200)

    ax1.plot(xs, p_fit(xs), "--", color=palette[4], linewidth=1.5, label="Tendencia lineal")
    ax1.set_title(f"Longitud vs Entropia (sin ponderar)\nrho = {rho_raw:.4f}  |  p = {p_raw:.6f}", fontsize=12)
    ax1.set_xlabel("Longitud de mascara")
    ax1.set_ylabel("Entropia media")
    ax1.legend()
    sns.despine(ax=ax1)
    ax1.grid(linestyle="--", alpha=0.4)

    ax2        = axes[1]
    lon_unicas = sorted(set(longitudes.astype(int)))
    medias_por_lon = []

    for l in lon_unicas:
        mask       = longitudes == l
        media_pond = np.average(entropias[mask], weights=frecuencias[mask])
        medias_por_lon.append(media_pond)

    sns.barplot(x=lon_unicas, y=medias_por_lon, palette="Blues", ax=ax2)
    ax2.set_title(f"Entropia media ponderada por longitud\nrho = {rho_pond:.4f}  |  p = {p_pond:.6f}", fontsize=12)
    ax2.set_xlabel("Longitud de mascara")
    ax2.set_ylabel("Entropia media ponderada")
    sns.despine(ax=ax2)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("../datos/procesados/graficos_kw/spearman_longitud_entropia.png",
                dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

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

def analizar_patrones_mascaras():
    """
    Analiza patrones estructurales en las mascaras de contrasennas ponderadas por frecuencia
    y genera una suite de graficos descriptivos integrados.
 
    Graficos generados:
        - Barras composicion de tipos (Solo L, Solo D, L+D, etc.)
        - Barras horizontales de inicio y final por tipo de caracter
        - Heatmap de correlacion entre presencia de tipos (L, U, D, S)
        - Barras de longitud ponderada
        - Barras de estructuras de bloque top 15
        - Scatter: longitud vs entropia media (burbuja por frecuencia)
        - Heatmap de bigramas de transicion entre tipos
        - Barras de posicion del primer D (sufijo numerico)
 
    Args:
        None
 
    Returns:
        None: Guarda graficos PNG en OUT_PAT_DIR y resumen de texto en OUT_PAT_TXT.
 
    Example:
        >>> analizar_patrones_mascaras()
        [patrones] composicion guardada
        [patrones] heatmap correlacion guardado
        ...
 
    Notes:
        Todos los calculos se ponderan por frecuencia de mascara salvo donde
        se indica. El heatmap de correlacion muestra el porcentaje de contrasennas
        que contienen ambos tipos simultaneamente, normalizado por el menor
        de los dos marginals (coeficiente de Jaccard ponderado).
    """
 
    OUT_PAT_DIR = "../datos/procesados/graficos_patrones"
    OUT_PAT_TXT = "../datos/procesados/patrones_mascaras_resumen.txt"
    os.makedirs(OUT_PAT_DIR, exist_ok=True)
 
    mascaras    = []
    frecuencias = []
    entropias   = []
 
    with open(ROCKYOUMASKS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mascaras.append(row["mascara"])
            frecuencias.append(int(row["frecuencia"]))
            entropias.append(float(row["entropia_media"]))
 
    mascaras    = np.array(mascaras)
    frecuencias = np.array(frecuencias, dtype=float)
    entropias   = np.array(entropias,   dtype=float)
    total_pw    = frecuencias.sum()
 
    def wpct(mask_bool):
        return frecuencias[mask_bool].sum() / total_pw * 100
 
    chars_set = [set(m) for m in mascaras]
 
    tiene = {
        t: np.array([t in s for s in chars_set])
        for t in ["L", "U", "D", "S"]
    }
 
    def bloques(m):
        if not m:
            return ""
        r = [m[0]]
        for c in m[1:]:
            if c != r[-1]:
                r.append(c)
        return "".join(r)
 
    longitudes = np.array([len(m) for m in mascaras])
 
    # ------------------------------------------------------------------ #
    # 1. Composicion de tipos                                      #
    # ------------------------------------------------------------------ #
    solo_L = np.array([s == {"L"}              for s in chars_set])
    solo_D = np.array([s == {"D"}              for s in chars_set])
    solo_U = np.array([s == {"U"}              for s in chars_set])
    solo_S = np.array([s == {"S"}              for s in chars_set])
    LD     = np.array([s == {"L","D"}          for s in chars_set])
    LU     = np.array([s == {"L","U"}          for s in chars_set])
    LS     = np.array([s == {"L","S"}          for s in chars_set])
    LUD    = np.array([s == {"L","U","D"}      for s in chars_set])
    LUDS   = np.array([s == {"L","U","D","S"}  for s in chars_set])
    otros  = ~(solo_L | solo_D | solo_U | solo_S | LD | LU | LS | LUD | LUDS)
 
    etiquetas_donut = ["Solo L", "Solo D", "Solo U", "L+D", "L+U", "L+S",
                       "L+U+D", "L+U+D+S", "Solo S", "Otros"]
    mascaras_donut  = [solo_L, solo_D, solo_U, LD, LU, LS, LUD, LUDS, solo_S, otros]
    valores_donut   = [wpct(m) for m in mascaras_donut]
    colores_donut   = [palette[9], palette[7], palette[5], palette[8],
                       palette[6], palette[4], palette[3], palette[2],
                       palette[1], palette[0]]
 
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("white")
    sns.barplot(x=etiquetas_donut, y=valores_donut, palette="Blues", ax=ax)
    ax.set_ylabel("% contraseñas (ponderado)")
    ax.set_xlabel("Tipo de composición")
    ax.set_title("Composición de tipos de caracter\n(ponderado por frecuencia)", fontsize=12)
    ax.tick_params(axis="x", rotation=45)
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/01_composicion_tipos.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] composicion guardada")
 
    # ------------------------------------------------------------------ #
    # 2. BARRAS DOBLES — inicio y final por tipo                          #
    # ------------------------------------------------------------------ #
    tipos        = ["L", "D", "U", "S"]
    pct_inicio   = [wpct(np.array([m[0]  == t for m in mascaras])) for t in tipos]
    pct_final    = [wpct(np.array([m[-1] == t for m in mascaras])) for t in tipos]
 
    x     = np.arange(len(tipos))
    ancho = 0.35
 
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("white")
    bars1 = ax.bar(x - ancho/2, pct_inicio, ancho, color=palette[7], alpha=0.9, label="Inicia con")
    bars2 = ax.bar(x + ancho/2, pct_final,  ancho, color=palette[4], alpha=0.9, label="Termina con")
    ax.bar_label(bars1, fmt="%.1f%%", fontsize=8, padding=3)
    ax.bar_label(bars2, fmt="%.1f%%", fontsize=8, padding=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["Letras minúsculas (L)", "Dígitos (D)", "Mayúsculas (U)", "Símbolos (S)"], rotation=20, ha="right")
    ax.set_ylabel("% contrasennas (ponderado)")
    ax.set_title("Tipo de caracter en primera y ultima posicion", fontsize=12)
    ax.legend()
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/02_inicio_final.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] inicio/final guardada")
 
    # ------------------------------------------------------------------ #
    # 3. HEATMAP — correlacion (Jaccard ponderado) entre tipos            #
    # ------------------------------------------------------------------ #
    tipos4 = ["L", "U", "D", "S"]
    n4     = len(tipos4)
    mat    = np.zeros((n4, n4))
 
    for i, ti in enumerate(tipos4):
        for j, tj in enumerate(tipos4):
            if i == j:
                mat[i, j] = wpct(tiene[ti])
            else:
                ambos    = tiene[ti] & tiene[tj]
                cualquiera = tiene[ti] | tiene[tj]
                denom    = frecuencias[cualquiera].sum()
                mat[i, j] = (frecuencias[ambos].sum() / denom * 100) if denom > 0 else 0
 
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor("white")
    sns.heatmap(
        mat,
        annot=True,
        fmt=".1f",
        xticklabels=tipos4,
        yticklabels=tipos4,
        cmap="Blues",
        linewidths=0.5,
        ax=ax,
        vmin=0, vmax=100,
        annot_kws={"size": 10}
    )
    ax.set_title("Co-ocurrencia ponderada entre tipos (%)\n(diagonal = presencia individual;\nfuera = Jaccard ponderado)", fontsize=10)
    ax.set_xlabel("Tipo B")
    ax.set_ylabel("Tipo A")
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/03_heatmap_correlacion_tipos.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] heatmap correlacion guardado")
 
    # ------------------------------------------------------------------ #
    # 4. BARRAS — distribucion de longitudes (hasta 20)                   #
    # ------------------------------------------------------------------ #
    lons_validas = range(1, 21)
    pct_lon      = []
    for l in lons_validas:
        pct_lon.append(wpct(longitudes == l))
 
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("white")
    barras = ax.bar(list(lons_validas), pct_lon, color=palette[6], alpha=0.88)
    ax.bar_label(barras, fmt="%.1f%%", fontsize=7, rotation=45, padding=2)
    ax.set_xlabel("Longitud de mascara")
    ax.set_ylabel("% contrasennas (ponderado)")
    ax.set_title("Distribucion de longitud de mascara", fontsize=12)
    ax.set_xticks(list(lons_validas))
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/04_longitud.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] longitud guardada")
 
    # ------------------------------------------------------------------ #
    # 5. BARRAS HORIZONTALES — top 15 estructuras de bloque               #
    # ------------------------------------------------------------------ #
    bloque_freq = {}
    for m, f in zip(mascaras, frecuencias):
        b = bloques(m)
        bloque_freq[b] = bloque_freq.get(b, 0) + f
 
    top15_bloques = sorted(bloque_freq.items(), key=lambda x: -x[1])[:15]
    bl_labels     = [b for b, _ in top15_bloques]
    bl_vals       = [v / total_pw * 100 for _, v in top15_bloques]
 
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor("white")
    bars = ax.barh(bl_labels[::-1], bl_vals[::-1], color=palette[6], alpha=0.88)
    ax.bar_label(bars, fmt="%.2f%%", fontsize=8, padding=3)
    ax.set_xlabel("% contrasennas (ponderado)")
    ax.set_title("Top 15 estructuras de bloque\n(tipos contiguos comprimidos)", fontsize=12)
    sns.despine(ax=ax)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/05_bloques.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] bloques guardada")
 
    # ------------------------------------------------------------------ #
    # 6. SCATTER burbuja — longitud vs entropia media                     #
    # ------------------------------------------------------------------ #
    lon_media_por_lon = {}
    for l in range(1, 31):
        mask = longitudes == l
        if mask.sum() == 0:
            continue
        lon_media_por_lon[l] = {
            "ent_pond": np.average(entropias[mask], weights=frecuencias[mask]),
            "frec":     frecuencias[mask].sum()
        }
 
    xs    = list(lon_media_por_lon.keys())
    ys    = [lon_media_por_lon[l]["ent_pond"] for l in xs]
    sz_f  = np.array([lon_media_por_lon[l]["frec"] for l in xs])
    sz    = np.sqrt(sz_f / sz_f.max()) * 600
 
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("white")
    sc = ax.scatter(xs, ys, s=sz, c=palette[7], alpha=0.7, edgecolors=palette[9], linewidths=0.5)
    z     = np.polyfit(xs, ys, 1)
    p_fit = np.poly1d(z)
    xline = np.linspace(min(xs), max(xs), 200)
    ax.plot(xline, p_fit(xline), "--", color=palette[4], linewidth=1.5, label="Tendencia")
    ax.set_xlabel("Longitud de mascara")
    ax.set_ylabel("Entropia media ponderada")
    ax.set_title("Longitud de mascara vs entropia media\n(tamano de burbuja = frecuencia relativa)", fontsize=12)
    ax.legend()
    sns.despine(ax=ax)
    ax.grid(linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/06_longitud_vs_entropia.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] scatter longitud-entropia guardada")
 
    # ------------------------------------------------------------------ #
    # 7. HEATMAP — bigramas de transicion entre tipos                     #
    # ------------------------------------------------------------------ #
    tipos_ord  = ["L", "U", "D", "S"]
    trans_mat  = np.zeros((4, 4))
    t_idx      = {t: i for i, t in enumerate(tipos_ord)}
 
    trans_total = 0.0
    for m, f in zip(mascaras, frecuencias):
        for k in range(len(m) - 1):
            a, b2 = m[k], m[k+1]
            if a in t_idx and b2 in t_idx:
                trans_mat[t_idx[a], t_idx[b2]] += f
                trans_total += f
 
    trans_pct = trans_mat / trans_total * 100 if trans_total > 0 else trans_mat
 
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor("white")
    sns.heatmap(
        trans_pct,
        annot=True,
        fmt=".2f",
        xticklabels=tipos_ord,
        yticklabels=tipos_ord,
        cmap="Blues",
        linewidths=0.5,
        ax=ax,
        annot_kws={"size": 10}
    )
    ax.set_title("Bigramas de transicion entre tipos (%)\n(fila = tipo origen, col = tipo destino)", fontsize=10)
    ax.set_xlabel("Tipo destino")
    ax.set_ylabel("Tipo origen")
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/07_heatmap_transiciones.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] heatmap transiciones guardado")
 
    # ------------------------------------------------------------------ #
    # 8. BARRAS — posicion del primer D (mascaras con D)                  #
    # ------------------------------------------------------------------ #
    tipos_pos = ["D", "L", "U", "S"]
    for t in tipos_pos:
        with_t    = [(m, f) for m, f in zip(mascaras, frecuencias) if t in m]
        total_t_f = sum(f for _, f in with_t)
        pos_t_freq = {}
        for m, f in with_t:
            pos = next(i+1 for i, c in enumerate(m) if c == t)
            pos_t_freq[pos] = pos_t_freq.get(pos, 0) + f

        top_pos = sorted(pos_t_freq.items(), key=lambda x: x[0])
        labels  = [f"Pos {p}" for p, _ in top_pos]
        vals    = [v / total_t_f * 100 for _, v in top_pos]

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("white")
        bars = ax.bar(labels, vals, color=palette[6], alpha=0.88)
        ax.bar_label(bars, fmt="%.1f%%", fontsize=8, padding=2)
        ax.set_xlabel(f"Posición del primer {t} en la máscara")
        ax.set_ylabel(f"% (de máscaras con {t})")
        ax.set_title(f"Posición del primer {t}\n(entre máscaras que contienen al menos un {t})", fontsize=12)
        sns.despine(ax=ax)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        plt.tight_layout()
        plt.savefig(f"{OUT_PAT_DIR}/08_posicion_primer_{t}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  [patrones] posición primer {t} guardada")

 
    # ------------------------------------------------------------------ #
    # 9. BARRAS — longitud del sufijo numerico (mascaras que terminan D)  #
    # ------------------------------------------------------------------ #
    term_D     = [(m, f) for m, f in zip(mascaras, frecuencias) if m[-1] == "D"]
    total_tD   = sum(f for _, f in term_D)
    sufijo_len = {}
    for m, f in term_D:
        suf = 0
        for c in reversed(m):
            if c == "D": suf += 1
            else: break
        sufijo_len[suf] = sufijo_len.get(suf, 0) + f
 
    suf_items  = sorted(sufijo_len.items(), key=lambda x: x[0])
    suf_labels = [f"{s} D" for s, _ in suf_items]
    suf_vals   = [v / total_tD * 100 for _, v in suf_items]
 
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("white")
    bars = ax.bar(suf_labels, suf_vals, color=palette[5], alpha=0.88)
    ax.bar_label(bars, fmt="%.1f%%", fontsize=8, padding=2)
    ax.set_xlabel("Longitud del sufijo numerico")
    ax.set_ylabel("% (de mascaras que terminan en D)")
    ax.set_title("Longitud del sufijo numerico al final de la mascara", fontsize=12)
    sns.despine(ax=ax)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{OUT_PAT_DIR}/09_sufijo_numerico.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  [patrones] sufijo numerico guardada")
 
    # ------------------------------------------------------------------ #
    # 10. RESUMEN TXT                                                      #
    # ------------------------------------------------------------------ #
    lineas = []
    def pr(t=""):
        lineas.append(t)
 
    pr("=" * 65)
    pr("  PATRONES EN MASCARAS (ponderado por frecuencia)")
    pr("=" * 65)
    pr(f"  Mascaras unicas : {len(mascaras):>10,}")
    pr(f"  Contrasennas    : {int(total_pw):>10,}")
    pr()
    pr("--- Composicion ---")
    pr(f"  Solo L           : {wpct(solo_L):.2f}%")
    pr(f"  Solo D           : {wpct(solo_D):.2f}%")
    pr(f"  Solo U           : {wpct(solo_U):.2f}%")
    pr(f"  Solo S           : {wpct(solo_S):.2f}%")
    pr(f"  L+D              : {wpct(LD):.2f}%")
    pr(f"  L+U              : {wpct(LU):.2f}%")
    pr(f"  L+S              : {wpct(LS):.2f}%")
    pr(f"  L+U+D            : {wpct(LUD):.2f}%")
    pr(f"  L+U+D+S          : {wpct(LUDS):.2f}%")
    pr()
    pr("--- Inicio y final ---")
    for t in tipos:
        pr(f"  Inicia {t}         : {wpct(np.array([m[0]==t  for m in mascaras])):.2f}%")
        pr(f"  Termina {t}        : {wpct(np.array([m[-1]==t for m in mascaras])):.2f}%")
    pr()
    pr("--- Longitud media ponderada ---")
    pr(f"  {np.average(longitudes, weights=frecuencias):.2f} caracteres")
    pr()
    pr(f"Graficos en: {OUT_PAT_DIR}/")
 
    with open(OUT_PAT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
 
    print(f"\n  -> {OUT_PAT_TXT} guardado")
    print(f"  -> Graficos en {OUT_PAT_DIR}/")


# main
if __name__ == "__main__":

    alpha_ks   = 0.05
    cap_expand = 500_000
    cap_spear  = 200_000

    print("=" * 50)
    print("  Bienvenido al menu de pruebas estadisticas")
    print("=" * 50)

    opcion = input(f"\nAlpha actual: {alpha_ks} | ¿Desea cambiarlo? (s/n): ").strip().lower()
    if opcion == 's':
        try:
            alpha_ks = float(input("Ingrese el nuevo alpha (ej. 0.01, 0.05, 0.10): "))
        except ValueError:
            print("  Valor inválido, se usará alpha = 0.05")
            alpha_ks = 0.05

    opcion = input(f"\nCap de expansión KW actual: {cap_expand} | ¿Desea cambiarlo? (s/n): ").strip().lower()
    if opcion == 's':
        try:
            cap_expand = int(input("Ingrese el nuevo cap de expansión (ej. 100000): "))
        except ValueError:
            print("  Valor inválido, se usará cap = 500000")
            cap_expand = 500_000

    opcion = input(f"\nCap de expansión Spearman actual: {cap_spear} | ¿Desea cambiarlo? (s/n): ").strip().lower()
    if opcion == 's':
        try:
            cap_spear = int(input("Ingrese el nuevo cap Spearman (ej. 50000): "))
        except ValueError:
            print("  Valor inválido, se usará cap = 200000")
            cap_spear = 200_000

    print(f"\nUsando alpha={alpha_ks}, cap_expand={cap_expand}, cap_spear={cap_spear}\n")
    print("=" * 50)
    print("=== Pruebas estadisticas ===\n")

    # PUNTO 3
    #
    # Pregunta de investigación (implicita en el proyecto):
    # En progreso
    #
    # El modelo seleccionado combina tres (por el momento) pruebas no parametricas:
    #   1. KS vs Benford  → ajuste de distribucion por posicion de dígito
    #   2. Kruskal-Wallis → diferencias de entropía entre grupos (longitud / tipo / rango)
    #   3. Spearman       → relacion monotonica entre longitud y entropía
    #
    # Juntas, responden si los patrones de contraseñas son predecibles
    # (Benford) y si la estructura interna (longitud, tipo) discrimina
    # la aleatoriedad medida por entropía. Esto permite concluir parcialmente
    # sobre la vulnerabilidad estructural de las contraseñas analizadas

    print("Calculando KS contra Benford...")
    # Compara la CDF empirica de digitos por posicion contra
    # la CDF teorica de Benford. Si D > D_alpha se rechaza H0, indicando
    # que los digitos NO siguen Benford -> patron diferente de benford
    ks_benford(alpha_ks)

    print("Calculando Kruskal-Wallis sobre entropias...")
    # Prueba si la distribucion de entropia difiere entre grupos.
    # Al rechazar H0 en longitud y tipo dominante se confirma que la estructura
    # de la mascara si predice la entropia, respondiendo parcialmente la pregunta
    # sobre predictibilidad de contrasenas segun su patron de caracteres.
    kruskal_wallis_entropias()

    print("Calculando Spearman longitud vs entropia...")
    # Cuantifica la fuerza y direccion de la relacion monotonica.
    # Un rho alto y positivo confirma que contrasenas mas largas son mas
    # entropicas, lo que respalda la recomendacion de longitud minima.
    spearman_longitud_entropia()

    
    # PUNTO 4
    #
    # Criterios para calificar si el modelo está bien ajustado:
    #
    # [A] Tamano de muestra (n):
    #     - n >> 10 000 en todas las pruebas -> alta potencia estadistica.
    #     - Ojo: con n muy grande hasta diferencias chiquitas salen
    #       significativas. Por eso se mira tambien D, MAD, H y rho
    #       para evaluar relevancia practica, no solo estadistica.
    #
    # [B] KS — ajuste a Benford:
    #     - Se reporta MAD (Mean Absolute Deviation) ademas del estadistico D.
    #     - Si todas las posiciones rechazan H0 pero el MAD es bajo,
    #       el rechazo se debe al n enorme, no a desviaciones reales.
    #
    # [C] Kruskal-Wallis — supuestos:
    #     - No pide normalidad (ya se cumple por construccion).
    #     - Necesita al menos 2 observaciones por grupo (eso se filtra en el codigo).
    #     - El cap de frecuencia es el riesgo: si es muy alto puede inflar H.
    #       Conviene probar con distintos caps para ver si los resultados se mantienen.
    #     - El agrupamiento por rango de entropia es obvio que da significativo
    #       (los grupos se definen con la misma variable). Se usa solo como descriptivo,
    #       no como prueba inferencial.
    #
    # [D] Spearman — robustez de la correlacion:
    #     - No asume linealidad ni normalidad -> sirve para datos ordinales
    #       y distribuciones sesgadas de contrasenas.
    #     - Se comparan version sin ponderar y ponderada; si rho se mantiene,
    #       la correlacion es robusta a la distribucion de frecuencias.
    #     - Un p ~ 0 con n gigante no dice mucho: lo que importa es el rho
    #       (si |rho| > 0.7 -> correlacion fuerte).
    #
    # [E] Consistencia global:
    #     - Si KS rechaza Benford, KW separa grupos y Spearman da rho alto,
    #       las pruebas son consistentes: los digitos no son aleatorios
    #       y la longitud/tipo los modula. Eso habla bien del modelo.
    #     - Si alguna prueba no rechaza H0, se anota como hallazgo,
    #       no como fallo del modelo.



    print("Analizando los patrones de las mascaras...")
    analizar_patrones_mascaras()
