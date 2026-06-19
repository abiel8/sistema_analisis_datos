import pandas as pd
import streamlit as st

from utils.validaciones import *


def mostrar_calidad_datos():

    st.header("Calidad de Datos")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv", "xls"]
    )

    if not archivo:
        return

    # ── Configuración de lectura ───────────────────────────────
    st.subheader("Configuración de lectura")

    fila_encabezado = st.number_input(
        "¿En qué fila están los encabezados? (0 = primera fila)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
        help="Si tu Excel tiene títulos o metadatos arriba, indica cuántas filas saltarse."
    )

    with st.expander("Ver archivo crudo (sin procesar)"):
        if archivo.name.endswith(".csv"):
            df_crudo = pd.read_csv(archivo, header=None, nrows=15)
        else:
            df_crudo = pd.read_excel(archivo, header=None, nrows=15)

        st.dataframe(df_crudo, use_container_width=True)
        archivo.seek(0)

    # ── Cargar con el encabezado correcto ─────────────────────
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo, header=int(fila_encabezado))
    else:
        df = pd.read_excel(archivo, header=int(fila_encabezado))

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Selección de columna ───────────────────────────────────
    columna = st.selectbox(
        "Seleccione una columna",
        df.columns
    )

    # ── Resumen de calidad ─────────────────────────────────────
    st.subheader("Resumen de calidad")

    c1, c2, c3 = st.columns(3)
    c1.metric("Vacíos",                contar_vacios(df, columna))
    c2.metric("Duplicados",            contar_duplicados(df, columna))
    c3.metric("Únicos",                contar_unicos(df, columna))

    c4, c5, c6 = st.columns(3)
    c4.metric("Longitud > 5",          longitud_mayor(df, columna, 5))
    c5.metric("Contiene números",      contiene_numeros(df, columna))
    c6.metric("Contiene letras",       contiene_letras(df, columna))

    c7, c8, c9 = st.columns(3)
    c7.metric("Solo números",          solo_numeros(df, columna))
    c8.metric("Solo letras",           solo_letras(df, columna))
    c9.metric("Caracteres especiales", caracteres_especiales(df, columna))

    # ── Filtrado por condiciones ───────────────────────────────
    st.subheader("Filtrar filas por condición")

    OPCIONES = {
        "Vacíos":                lambda d, c: d[d[c].isna() | (d[c].astype(str).str.strip() == "")],
        "Duplicados":            lambda d, c: d[d[c].duplicated(keep=False)],
        "Longitud > 5":          lambda d, c: d[d[c].astype(str).str.len() > 5],
        "Contiene números":      lambda d, c: d[d[c].astype(str).str.contains(r'\d', na=False)],
        "Contiene letras":       lambda d, c: d[d[c].astype(str).str.contains(r'[a-zA-Z]', na=False)],
        "Solo números":          lambda d, c: d[d[c].astype(str).str.fullmatch(r'\d+', na=False)],
        "Solo letras":           lambda d, c: d[d[c].astype(str).str.fullmatch(r'[a-zA-Z]+', na=False)],
        "Caracteres especiales": lambda d, c: d[d[c].astype(str).str.contains(r'[^a-zA-Z0-9\s]', na=False)],
    }

    seleccion = st.multiselect(
        "Seleccione una o más condiciones para filtrar",
        options=list(OPCIONES.keys())
    )

    if not seleccion:
        return

    modo = st.radio(
        "¿Cómo combinar las condiciones?",
        options=["Cualquiera (OR)", "Todas (AND)"],
        horizontal=True
    )

    mascaras = [
        OPCIONES[opcion](df, columna).index
        for opcion in seleccion
    ]

    if modo == "Cualquiera (OR)":
        indice_final = mascaras[0]
        for m in mascaras[1:]:
            indice_final = indice_final.union(m)
    else:
        indice_final = mascaras[0]
        for m in mascaras[1:]:
            indice_final = indice_final.intersection(m)

    df_filtrado = df.loc[indice_final].sort_index()

    st.markdown(
        f"**{len(df_filtrado)}** filas encontradas "
        f"de **{len(df)}** totales."
    )

    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar filas filtradas (.csv)",
        data=csv,
        file_name="filas_filtradas.csv",
        mime="text/csv"
    )