import re

import pandas as pd


def _columna_tiene_cero_inicial(serie):

    valores = serie.dropna().astype(str)

    if valores.empty:
        return False

    patron_cero_inicial = re.compile(r"^0\d+$")

    return valores.apply(lambda v: bool(patron_cero_inicial.match(v.strip()))).any()


def _convertir_tipos_preservando_ceros(df):

    columnas_protegidas = []

    for columna in df.columns:

        serie = df[columna]

        if _columna_tiene_cero_inicial(serie):
            df[columna] = serie.astype(str).str.strip()
            columnas_protegidas.append(columna)
            continue

        try:
            df[columna] = pd.to_numeric(serie)
        except (ValueError, TypeError):
            pass  # Se deja como texto

    return df, columnas_protegidas


def cargar_archivo(archivo, hoja=0, fila_encabezado=1):

    if archivo.name.endswith(".csv"):
        df = pd.read_csv(
            archivo,
            dtype=str
        )

    elif archivo.name.endswith(".xls"):
        df = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=fila_encabezado - 1,
            dtype=str,
            engine="xlrd"
        )

    else:  # .xlsx
        df = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=fila_encabezado - 1,
            dtype=str,
            engine="openpyxl"
        )

    df, _ = _convertir_tipos_preservando_ceros(df)

    return df