import pandas as pd
import streamlit as st

from utils.validaciones import *


def mostrar_calidad_datos():

    st.header("Calidad de Datos")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv"]
    )

    if not archivo:
        return

    # ── Configuración de lectura ───────────────────────────────
    st.subheader("Configuración de lectura")

    col_a, col_b = st.columns(2)

    fila_encabezado = col_a.number_input(
        "¿En qué fila está el encabezado? (0 = primera fila)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
        help="Indica en qué fila (contando desde 0) están los nombres de columna."
    )

    fila_inicio_datos = col_b.number_input(
        "¿En qué fila empiezan los datos?",
        min_value=int(fila_encabezado) + 1,
        max_value=100,
        value=int(fila_encabezado) + 1,
        step=1,
        help="Por defecto es la fila siguiente al encabezado. Si hay filas vacías de separación, ajusta aquí."
    )

    # ── Vista previa cruda (con su propio manejo de errores) ───
    with st.expander("Ver archivo crudo (sin procesar)"):
        try:
            if archivo.name.endswith(".csv"):
                df_crudo = pd.read_csv(archivo, header=None, nrows=15)
            else:
                df_crudo = pd.read_excel(archivo, header=None, nrows=15, engine="openpyxl")

            st.dataframe(df_crudo, use_container_width=True)

        except Exception as e:
            st.warning(f"No se pudo generar la vista previa cruda: {e}")

        finally:
            archivo.seek(0)

    # ── Cargar: encabezado de una fila + datos desde otra ──────
    filas_a_saltar = list(range(int(fila_encabezado) + 1, int(fila_inicio_datos)))

    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar
            )
        elif archivo.name.endswith(".xls"):
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                engine="xlrd"
            )
        else:
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                engine="openpyxl"
            )

    except ValueError as e:
        st.error(
            "No se pudo leer el archivo con la configuración indicada. "
            f"Verifique la fila de encabezado y la fila de inicio de datos. Detalle: {e}"
        )
        return

    except ImportError:
        st.error(
            "Falta una librería para leer este tipo de archivo Excel. "
            "Si es un archivo .xls antiguo, instale xlrd con: pip install xlrd"
        )
        return

    except Exception as e:
        st.error(f"Ocurrió un error inesperado al leer el archivo: {e}")
        return

    if df.empty:
        st.warning("El archivo se leyó correctamente, pero no contiene datos con esta configuración.")
        return

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Selección de columna(s) para las métricas ──────────────
    columna = st.selectbox(
        "Seleccione una columna para ver el resumen de calidad",
        df.columns
    )

    # ── Resumen de calidad ─────────────────────────────────────
    st.subheader("Resumen de calidad")

    try:
        c1, c2, c3 = st.columns(3)
        c1.metric("Vacíos",                contar_vacios(df, columna))
        c2.metric("Duplicados",            contar_duplicados(df, columna))
        c3.metric("Únicos",                contar_unicos(df, columna))

        c4, c5, c6 = st.columns(3)
        c4.metric("Longitud > 10",         longitud_mayor(df, columna, 10))
        c5.metric("Contiene números",      contiene_numeros(df, columna))
        c6.metric("Contiene letras",       contiene_letras(df, columna))

        c7, c8, c9 = st.columns(3)
        c7.metric("Solo números",          solo_numeros(df, columna))
        c8.metric("Solo letras",           solo_letras(df, columna))
        c9.metric("Caracteres especiales", caracteres_especiales(df, columna))

    except Exception as e:
        st.error(f"No se pudieron calcular las métricas para la columna '{columna}': {e}")
        return

    # ── Filtrado por condiciones, en una o varias columnas ─────
    st.subheader("Filtrar filas por condición")

    columnas_a_filtrar = st.multiselect(
        "Seleccione una o más columnas donde buscar",
        options=df.columns.tolist(),
        default=[columna]
    )

    OPCIONES = {
        "Vacíos":                lambda d, c: d[c].isna() | (d[c].astype(str).str.strip() == ""),
        "Duplicados":            lambda d, c: d[c].duplicated(keep=False),
        "Longitud > 10":         lambda d, c: d[c].astype(str).str.len() > 10,
        "Contiene números":      lambda d, c: d[c].astype(str).str.contains(r'\d', na=False),
        "Contiene letras":       lambda d, c: d[c].astype(str).str.contains(r'[a-zA-Z]', na=False),
        "Solo números":          lambda d, c: d[c].astype(str).str.fullmatch(r'\d+', na=False),
        "Solo letras":           lambda d, c: d[c].astype(str).str.fullmatch(r'[a-zA-Z]+', na=False),
        "Caracteres especiales": lambda d, c: d[c].astype(str).str.contains(r'[^a-zA-Z0-9\s]', na=False),
    }

    seleccion = st.multiselect(
        "Seleccione una o más condiciones para filtrar",
        options=list(OPCIONES.keys())
    )

    if not columnas_a_filtrar or not seleccion:
        return

    modo_condiciones = st.radio(
        "¿Cómo combinar las condiciones entre sí?",
        options=["Cualquiera (OR)", "Todas (AND)"],
        horizontal=True,
        key="modo_condiciones"
    )

    modo_columnas = st.radio(
        "¿Cómo combinar entre las columnas seleccionadas?",
        options=["Cualquiera columna (OR)", "Todas las columnas (AND)"],
        horizontal=True,
        key="modo_columnas"
    )

    try:
        mascaras_por_columna = []

        for col in columnas_a_filtrar:

            mascaras_condicion = [
                OPCIONES[opcion](df, col)
                for opcion in seleccion
            ]

            if modo_condiciones == "Cualquiera (OR)":
                mascara_col = mascaras_condicion[0]
                for m in mascaras_condicion[1:]:
                    mascara_col = mascara_col | m
            else:
                mascara_col = mascaras_condicion[0]
                for m in mascaras_condicion[1:]:
                    mascara_col = mascara_col & m

            mascaras_por_columna.append(mascara_col)

        if modo_columnas == "Cualquiera columna (OR)":
            mascara_final = mascaras_por_columna[0]
            for m in mascaras_por_columna[1:]:
                mascara_final = mascara_final | m
        else:
            mascara_final = mascaras_por_columna[0]
            for m in mascaras_por_columna[1:]:
                mascara_final = mascara_final & m

        df_filtrado = df[mascara_final]

    except Exception as e:
        st.error(f"Ocurrió un error al aplicar el filtro: {e}")
        return

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
    
    