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
palette           = sns.color_palette("Blues", 5)



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
        ax1.bar(x - ancho/2, prob_teorica,  width=ancho, color=palette[2], alpha=0.7, label=f"Benford pos {pos_num}")
        ax1.bar(x + ancho/2, prob_empirica, width=ancho, color=palette[3], alpha=0.7, label="Empirica")
        ax1.set_title(f"Posicion {pos_num} — Distribucion", fontsize=13)
        ax1.set_xlabel("Digito")
        ax1.set_ylabel("Probabilidad")
        ax1.set_xticks(x)
        ax1.legend()
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        ax2 = axes[1]
        ax2.set_facecolor("white")
        ax2.step(x, cdf_teorica,  where="post", color=palette[2], linewidth=2, label=f"CDF Benford pos {pos_num}")
        ax2.step(x, cdf_empirica, where="post", color=palette[3], linewidth=2, label="CDF Empirica")

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


# main
if __name__ == "__main__":

    print("=== Pruebas estadisticas ===\n")

    # Metodos no parametricos
    print("Calculando KS contra Benford...")
    ks_benford(0.1)