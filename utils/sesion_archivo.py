import streamlit as st

from utils.carga_archivos import seleccionar_hoja_ui, cargar_dataframe_ui
from utils.proteccion_tipos import convertir_tipos_preservando_ceros, mostrar_aviso_columnas_protegidas


def _mismo_archivo(archivo_nuevo):
    """Compara el archivo recién subido contra el que ya está en sesión,
    usando nombre + tamaño como huella simple (suficiente para detectar
    si el usuario subió un archivo distinto)."""

    anterior = st.session_state.get("archivo_info")

    if anterior is None:
        return False

    return (
        anterior["nombre"] == archivo_nuevo.name
        and anterior["tamano"] == archivo_nuevo.size
    )


def _guardar_en_sesion(df, archivo, hoja_seleccionada, columnas_protegidas):

    st.session_state["df_actual"] = df
    st.session_state["archivo_info"] = {
        "nombre": archivo.name,
        "tamano": archivo.size,
        "hoja": hoja_seleccionada,
    }
    st.session_state["columnas_protegidas_actual"] = columnas_protegidas


def limpiar_sesion_archivo():
    """Borra el archivo/DataFrame guardado, forzando a pedir uno nuevo."""

    for clave in ("df_actual", "archivo_info", "columnas_protegidas_actual"):
        st.session_state.pop(clave, None)


def obtener_dataframe_sesion(permitir_filas_a_saltar=True, descripcion_modulo=None):
    """Flujo completo y reutilizable para los 3 módulos:

    1. Si ya hay un archivo cargado en esta sesión, lo reutiliza y muestra
       un resumen compacto con la opción de cambiarlo.
    2. Si no hay archivo en sesión (o el usuario pidió cambiarlo), muestra
       un mensaje de bienvenida (si se indicó descripcion_modulo) seguido
       del flujo normal de carga.

    Devuelve el DataFrame listo para usar, o None si todavía no hay nada
    cargado (en cuyo caso el módulo que llama debe hacer return).
    """

    archivo_en_sesion = "df_actual" in st.session_state

    if archivo_en_sesion:

        info = st.session_state["archivo_info"]

        col_info, col_boton = st.columns([4, 1])

        with col_info:
            st.success(
                f"Usando el archivo ya cargado: **{info['nombre']}** "
                f"(hoja: {info['hoja']})"
            )

        with col_boton:
            if st.button("Subir otro archivo", use_container_width=True):
                limpiar_sesion_archivo()
                st.rerun()

        mostrar_aviso_columnas_protegidas(st.session_state.get("columnas_protegidas_actual", []))

        return st.session_state["df_actual"]

    # ── No hay archivo en sesión: mensaje de bienvenida + carga ─────

    if descripcion_modulo:
        st.info(descripcion_modulo)

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv", "xls"]
    )

    if not archivo:
        return None

    archivo_bytes = archivo.getvalue()

    hoja_seleccionada = seleccionar_hoja_ui(archivo, archivo_bytes)

    if hoja_seleccionada is None:
        return None

    st.subheader("Configuración de lectura")

    col_a, col_b = st.columns(2)

    fila_encabezado = col_a.number_input(
        "¿En qué fila está el encabezado? (0 = primera fila)",
        min_value=0,
        max_value=50,
        value=0,
        step=1
    )
    col_a.caption("La mayoría de archivos usan 0 (el encabezado es la primera fila).")

    filas_a_saltar = []

    if permitir_filas_a_saltar:

        fila_inicio_datos = col_b.number_input(
            "¿En qué fila empiezan los datos?",
            min_value=int(fila_encabezado) + 1,
            max_value=100,
            value=int(fila_encabezado) + 1,
            step=1
        )
        col_b.caption("Cambie esto solo si hay filas vacías entre el encabezado y los datos.")

        filas_a_saltar = list(range(int(fila_encabezado) + 1, int(fila_inicio_datos)))

    df = cargar_dataframe_ui(archivo, fila_encabezado, filas_a_saltar, hoja_seleccionada)

    if df is None:
        return None

    df, columnas_protegidas = convertir_tipos_preservando_ceros(df)
    mostrar_aviso_columnas_protegidas(columnas_protegidas)

    _guardar_en_sesion(df, archivo, hoja_seleccionada, columnas_protegidas)

    return df