import string
import unicodedata

import pandas as pd


def _limpiar_valor(valor):

    if pd.isna(valor):
        return valor

    texto = str(valor).strip()

    # Proteger la ñ/Ñ antes de quitar tildes, para convertirla después a n/N
    texto = texto.replace("ñ", "{{enie}}").replace("Ñ", "{{ENIE}}")

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    texto = texto.replace("{{enie}}", "n").replace("{{ENIE}}", "N")

    # Quitar todos los signos de puntuación
    texto = texto.translate(str.maketrans("", "", string.punctuation))

    # Colapsar espacios múltiples y quitar extremos
    texto = " ".join(texto.split())

    return texto


def limpiar_texto_columna(serie):
    """Quita tildes, convierte ñ→n, elimina puntuación, y normaliza espacios."""

    return serie.apply(_limpiar_valor)


def limpiar_nombres_columnas(columnas):
    """Convierte nombres de columna a snake_case, manejando tildes/ñ
    correctamente (en vez de simplemente borrarlas)."""

    columnas_limpias = limpiar_texto_columna(pd.Series(columnas))

    return (
        columnas_limpias
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )