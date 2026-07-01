import re

import pandas as pd


# ═══════════════════════════════════════════════════════════════
# Dividir nombres: primera palabra = nombre, resto = apellido
# ═══════════════════════════════════════════════════════════════

def dividir_nombre_apellido(serie):
    """Recibe una Serie con nombres completos y devuelve un DataFrame
    con dos columnas: 'nombre' (primera palabra) y 'apellido' (el resto).
    Maneja valores vacíos/nulos sin romper."""

    def _dividir(valor):
        if pd.isna(valor) or str(valor).strip() == "":
            return pd.Series({"Nombre 1": None, "Nombre 2 ": None})

        partes = str(valor).strip().split(None, 1)  # split en el primer espacio

        nombre = partes[0] if len(partes) >= 1 else None
        apellido = partes[1] if len(partes) >= 2 else None

        return pd.Series({"Nombre 1": nombre, "Nombre 2 ": apellido})

    return serie.apply(_dividir)


# ═══════════════════════════════════════════════════════════════
# Estandarizar fechas a un formato destino
# ═══════════════════════════════════════════════════════════════

FORMATOS_FECHA = {
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD-MM-YYYY": "%d-%m-%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
}


def estandarizar_fechas(serie, formato_destino="DD/MM/YYYY"):
    """Intenta convertir cada valor de la serie a una fecha reconocible
    (usando pd.to_datetime con inferencia automática de formato) y luego
    la formatea al formato destino elegido. Los valores que no se pueden
    interpretar como fecha se dejan como están, sin romper la columna."""

    formato_strftime = FORMATOS_FECHA.get(formato_destino, "%d/%m/%Y")

    def _convertir(valor):

        if pd.isna(valor) or str(valor).strip() == "":
            return valor

        texto = str(valor).strip()

        # Intentar parsear con varios enfoques para cubrir más formatos
        for kwargs in [
            {"dayfirst": True},
            {"dayfirst": False},
            {"yearfirst": True},
        ]:
            try:
                fecha = pd.to_datetime(texto, **kwargs)
                return fecha.strftime(formato_strftime)
            except Exception:
                continue

        return valor  # No se pudo interpretar, se deja como está

    return serie.apply(_convertir)


# ═══════════════════════════════════════════════════════════════
# Reemplazar valores: un par buscar/reemplazar por vez
# ═══════════════════════════════════════════════════════════════

def reemplazar_valor(serie, buscar, reemplazar, exacto=True):
    """Reemplaza ocurrencias de 'buscar' por 'reemplazar' en la serie.

    Si exacto=True: solo reemplaza si el valor completo de la celda
    coincide exactamente con 'buscar' (útil para corregir abreviaciones).

    Si exacto=False: reemplaza cualquier aparición de 'buscar' dentro
    del texto, aunque sea una subcadena (útil para limpiar fragmentos).
    """

    if exacto:
        return serie.replace(buscar, reemplazar)

    return serie.astype(str).str.replace(
        re.escape(buscar), reemplazar, regex=True
    )


def reemplazar_en_dataframe(df, columna, buscar, reemplazar, exacto=True):
    """Aplica reemplazar_valor sobre una columna específica del DataFrame,
    o sobre todas las columnas de texto si columna == '__TODAS__'."""

    df = df.copy()

    if columna == "__TODAS__":
        for col in df.select_dtypes(include="object").columns:
            df[col] = reemplazar_valor(df[col], buscar, reemplazar, exacto)
    else:
        df[columna] = reemplazar_valor(df[columna], buscar, reemplazar, exacto)

    return df