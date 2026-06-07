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
        if mad < 0.006:
            mad_result = "Muy cercana"
        elif mad < 0.012:
            mad_result = "Aceptable"
        elif mad < 0.015:
            mad_result = "Marginal"
        else:
            mad_result = "No conformidad"

        resultados.append({
            "posicion":   pos_num,
            "n":          int(total),
            "D":          D,
            "D_alpha":    D_alpha,
            "rechaza":    rechaza,
            "mad":        mad,
            "mad_result": mad_result
        })

        print(f"  Posicion {pos_num}: n = {int(total):<12} D = {D:.6f}   D_alpha = {D_alpha:.6f}   {estado:<12} MAD = {mad:.6f}   {mad_result}")

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
            f.write(f"{r['posicion']:<6} {r['n']:<14} {r['D']:<12.6f} {r['D_alpha']:<12.6f} {estado:<14} {r['mad']:<12.6f} {r['mad_result']}\n")

        rechazadas = sum(1 for r in resultados if r["rechaza"])
        f.write(f"\nPosiciones que rechazan H0: {rechazadas} / {len(resultados)}\n")
        f.write(f"Alpha usado: {alpha}\n")
        f.write("Nota: posicion 1 usa digitos 1-9, posiciones 2+ usan digitos 0-9\n")

    print(f"\n  -> {OUT_TXT} guardado")
    print(f"  -> Graficos en {OUT_DIR}/")



def kruskal_wallis_entropias():
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
            str: Etiqueta del rango: 'Baja (<1.5)', 'Media (1.5-2.5)' o 'Alta (>=2.5)'.
        """
        if e < 1.5:
            return "Baja (<1.5)"
        if e < 2.5:
            return "Media (1.5-2.5)"
        return "Alta (>=2.5)"

    rangos       = np.array([rango_entropia(e) for e in entropias])
    grupos_rango = defaultdict(list)

    for rng, ent, frq in zip(rangos, entropias, frecuencias):
        grupos_rango[rng].append((ent, frq))

    orden_rangos  = ["Baja (<1.5)", "Media (1.5-2.5)", "Alta (>=2.5)"]
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


def spearman_longitud_entropia():
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

    cap     = 200_000
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
