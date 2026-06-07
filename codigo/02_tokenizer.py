# 02_tokenizer.py
# Tokenizacion de palabras con tiktoken (GPT-4) y distribucion de digitos de la suma
# Hecho por Anthonny Flores Rojas (C32975)
# Generado con Claude (Anthropic), inspirado y basado en la logica estructural
# de los programas originales 01_limpieza.cpp y 02_descriptivo.cpp
# escritos por Anthonny Flores Rojas
# Correguido y revisado por Anthonny Flores Rojas
#
# Instalar dependencia: pip install tiktoken
# Correr: python 02_tokenizer.py

import os
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

# Intentar cargar tiktoken; si no esta disponible, usar ASCII como fallback
try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
    def encode(word: str) -> list[int]:
        return _enc.encode(word)
    ENCODING_NAME = "cl100k_base (tiktoken)"
    print("Usando tiktoken cl100k_base (GPT-4)")
except Exception:
    def encode(word: str) -> list[int]:
        return [ord(c) for c in word]
    ENCODING_NAME = "ASCII (fallback)"
    print("tiktoken no disponible, usando ASCII como fallback")


# Estructura para manejo de datos por tokens
@dataclass
class DataToken:
    word:      str
    tokens:    list = field(default_factory=list)
    token_sum: int  = 0

# Estructura para distribucion del n-esimo digito
@dataclass
class DigitDist:
    counts: dict = field(default_factory=lambda: defaultdict(int))


# Clase tokenizer
class Tokenizer:

    def __init__(self):
        self.data:        list[DataToken] = []
        self.digit_dists: list[DigitDist] = []
        self.max_digits:  int             = 0
        self.max_len:     int             = 16
        self.max_chunks:  int             = 8

    # Funcion para tokenizar una palabra
    def tokenize_word(self, word: str) -> DataToken:

        tokens    = encode(word)
        token_sum = sum(tokens)
        return DataToken(word=word, tokens=tokens, token_sum=token_sum)

    # Funcion para leer el txt y tokenizar todas las palabras
    def read_and_tokenize(self, input_path: str) -> None:

        words = []

        with open(input_path, "r", encoding="utf-8", errors="replace") as f:

            for line in f:

                line = line.strip()
                if not line:
                    continue

                parts = line.split(None, 1)

                # Si el primer campo es numero => formato "freq palabra"
                if len(parts) == 2 and parts[0].isdigit():
                    word = parts[1]
                else:
                    word = parts[0]

                if word and len(word) <= self.max_len:
                    words.append(word)

        print(f"  {len(words)} palabras leidas, tokenizando...")

        workers = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=workers) as pool:
            self.data = list(pool.map(self.tokenize_word, words))

        print(f"  Tokenizado completo.")

    # Funcion para calcular la distribucion del n-esimo digito de la suma de tokens
    def make_digit_dists(self) -> None:

        self.max_digits  = max(len(str(dt.token_sum)) for dt in self.data)
        self.digit_dists = [DigitDist() for _ in range(self.max_digits)]

        n          = len(self.data)
        workers    = os.cpu_count() or 4
        chunk_size = max(1, n // workers)
        chunks     = [self.data[i:i+chunk_size] for i in range(0, n, chunk_size)]

        def process_chunk(items):

            local = [defaultdict(int) for _ in range(self.max_digits)]

            for dt in items:
                s = str(dt.token_sum)
                for pos, ch in enumerate(s):
                    local[pos][int(ch)] += 1

            return local

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(process_chunk, chunks))

        # Combinar resultados parciales de cada hilo
        for local in results:
            for pos in range(self.max_digits):
                for digit, count in local[pos].items():
                    self.digit_dists[pos].counts[digit] += count

    # Funcion para guardar los tokens en un archivo CSV
    def save_tokens(self, output_path: str) -> None:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["word", "tokens", "tokenSum"])

            for dt in self.data:
                writer.writerow([
                    dt.word,
                    "|".join(str(t) for t in dt.tokens),
                    dt.token_sum
                ])

        print(f"  -> {output_path} guardado ({len(self.data)} palabras)")

    # Funcion para guardar la distribucion de digitos de la suma de tokens
    def save_digit_dists(self, output_path: str) -> None:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["digit"] + [f"pos{p+1}" for p in range(self.max_digits)])

            for d in range(10):
                row = [d] + [self.digit_dists[p].counts.get(d, 0)
                             for p in range(self.max_digits)]
                writer.writerow(row)

        print(f"  -> {output_path} guardado ({self.max_digits} posiciones de digito)")

    # Funcion para guardar un resumen estadistico de las sumas de tokens
    def save_summary(self, output_path: str) -> None:

        sums = [dt.token_sum for dt in self.data]
        n    = len(sums)
        mean = sum(sums) / n
        var  = sum((s - mean) ** 2 for s in sums) / n
        sd   = var ** 0.5

        sums_sorted = sorted(sums)
        def pct(p):
            return sums_sorted[min(int(p * n), n - 1)]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== Resumen de sumas de tokens ===\n\n")
            f.write(f"Encoding usado:   {ENCODING_NAME}\n")
            f.write(f"Total palabras:   {n}\n")
            f.write(f"Max letras usado: {self.max_len}\n")
            f.write(f"Suma minima:      {min(sums)}\n")
            f.write(f"Suma maxima:      {max(sums)}\n")
            f.write(f"Media:            {mean:.4f}\n")
            f.write(f"Desv std:         {sd:.4f}\n")
            f.write(f"Max digitos suma: {self.max_digits}\n")
            f.write("\n=== Percentiles ===\n")
            for p in [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]:
                f.write(f"P{int(p*100):02d}: {pct(p)}\n")

        print(f"  -> {output_path} guardado")


# main
if __name__ == "__main__":

    INPUT = "../datos/originales/rockyou-with-count.txt"
    OUT1  = "../datos/procesados/tokens.txt"
    OUT2  = "../datos/procesados/tokens_dist_digitos.txt"
    OUT3  = "../datos/procesados/tokens_resumen.txt"

    tok = Tokenizer()

    # Menu de configuracion
    print("=== Configuracion de parametros ===")

    opcion = input(f"Maximo de letras actual: {tok.max_len} | Desea cambiarlo? (s/n): ").strip().lower()
    if opcion == 's':
        tok.max_len = int(input("Ingrese el nuevo maximo de letras: ").strip())

    opcion = input(f"Maximo de chunks actual: {tok.max_chunks} | Desea cambiarlo? (s/n): ").strip().lower()
    if opcion == 's':
        tok.max_chunks = int(input("Ingrese el nuevo maximo de chunks: ").strip())

    print(f"\nUsando maxLetras = {tok.max_len}, maxChunks = {tok.max_chunks}\n")

    print("Leyendo y tokenizando...")
    tok.read_and_tokenize(INPUT)

    print("\nGuardando tokens...")
    tok.save_tokens(OUT1)

    print("\nCalculando distribucion de digitos...")
    tok.make_digit_dists()
    tok.save_digit_dists(OUT2)

    print("\nGuardando resumen...")
    tok.save_summary(OUT3)

    print("\nListo.")

    # Correr con: python 02_tokenizer.py