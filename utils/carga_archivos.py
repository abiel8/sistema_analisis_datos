import io

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def listar_hojas(archivo_bytes):
    """Devuelve la lista de nombres de hoja de un archivo Excel."""

    xls = pd.ExcelFile(io.BytesIO(archivo_bytes))
    return xls.sheet_names


@st.cache_data(show_spinner=False)
def leer_vista_cruda(archivo_bytes, nombre_archivo, hoja_seleccionada, nrows=15):
    """Lee las primeras filas sin encabezado, para que el usuario identifique
    en qué fila está su encabezado real."""

    if nombre_archivo.endswith(".csv"):
        return pd.read_csv(io.BytesIO(archivo_bytes), header=None, nrows=nrows)

    elif nombre_archivo.endswith(".xls"):
        return pd.read_excel(
            io.BytesIO(archivo_bytes), header=None, nrows=nrows,
            sheet_name=hoja_seleccionada, engine="xlrd"
        )

    else:
        return pd.read_excel(
            io.BytesIO(archivo_bytes), header=None, nrows=nrows,
            sheet_name=hoja_seleccionada, engine="openpyxl"
        )


@st.cache_data(show_spinner="Leyendo archivo...")
def leer_dataframe(archivo_bytes, nombre_archivo, fila_encabezado, filas_a_saltar, hoja_seleccionada):
    """Lee el archivo completo como texto (dtype=str), respetando la fila de
    encabezado y las filas a saltar. filas_a_saltar debe ser una tupla
    (no lista) para que la función sea cacheable."""

    if nombre_archivo.endswith(".csv"):
        df = pd.read_csv(
            io.BytesIO(archivo_bytes),
            header=fila_encabezado,
            skiprows=list(filas_a_saltar),
            dtype=str
        )

    elif nombre_archivo.endswith(".xls"):
        df = pd.read_excel(
            io.BytesIO(archivo_bytes),
            header=fila_encabezado,
            skiprows=list(filas_a_saltar),
            sheet_name=hoja_seleccionada,
            dtype=str,
            engine="xlrd"
        )

    else:
        df = pd.read_excel(
            io.BytesIO(archivo_bytes),
            header=fila_encabezado,
            skiprows=list(filas_a_saltar),
            sheet_name=hoja_seleccionada,
            dtype=str,
            engine="openpyxl"
        )

    return df


def seleccionar_hoja_ui(archivo, archivo_bytes):
    """Muestra el selector de hoja en la interfaz si el archivo es Excel
    con más de una hoja. Devuelve el nombre/índice de hoja elegido, o 0
    si es CSV o tiene una sola hoja. Lanza st.error y devuelve None si falla."""

    if archivo.name.endswith(".csv"):
        return 0

    try:
        hojas_disponibles = listar_hojas(archivo_bytes)

        if len(hojas_disponibles) > 1:
            return st.selectbox(
                "El archivo tiene varias hojas. Seleccione cuál usar:",
                options=hojas_disponibles
            )

        return hojas_disponibles[0]

    except Exception as e:
        st.error(f"No se pudo leer la lista de hojas del archivo: {e}")
        return None


def cargar_dataframe_ui(archivo, fila_encabezado, filas_a_saltar, hoja_seleccionada):
    """Envuelve leer_dataframe con manejo de errores estándar para mostrar
    en la interfaz. Devuelve el DataFrame o None si falló (y ya mostró
    el st.error correspondiente)."""

    archivo_bytes = archivo.getvalue()

    try:
        df = leer_dataframe(
            archivo_bytes,
            archivo.name,
            int(fila_encabezado),
            tuple(filas_a_saltar),
            hoja_seleccionada
        )

    except ValueError as e:
        st.error(
            "No se pudo leer el archivo con la configuración indicada. "
            f"Verifique la fila de encabezado y la fila de inicio de datos. Detalle: {e}"
        )
        return None

    except ImportError:
        st.error(
            "Falta una librería para leer este tipo de archivo. "
            "Si es un archivo .xls antiguo, instale xlrd con: pip install xlrd"
        )
        return None

    except Exception as e:
        st.error(f"Ocurrió un error inesperado al leer el archivo: {e}")
        return None

    if df.empty:
        st.warning("El archivo se leyó correctamente, pero no contiene datos con esta configuración.")
        return None

    return df