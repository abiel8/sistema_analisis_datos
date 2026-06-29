import re

import pandas as pd
import streamlit as st


def _columna_tiene_cero_inicial(serie):

    valores = serie.dropna().astype(str)

    if valores.empty:
        return False

    patron_cero_inicial = re.compile(r"^0\d+$")

    return valores.apply(lambda v: bool(patron_cero_inicial.match(v.strip()))).any()


@st.cache_data(show_spinner=False)
def convertir_tipos_preservando_ceros(df):
    """Para cada columna: si tiene valores con cero a la izquierda (ej. '0006'),
    se protege como texto. Si no, se intenta convertir a numérico.
    Devuelve (df_convertido, lista_de_columnas_protegidas)."""

    df = df.copy()
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


def mostrar_aviso_columnas_protegidas(columnas_protegidas):

    if columnas_protegidas:
        st.info(
            "Se detectaron y protegieron como texto estas columnas con ceros a la izquierda: "
            f"{', '.join(columnas_protegidas)}"
        )