import streamlit as st

from utils.carga_archivos import seleccionar_hoja_ui, cargar_dataframe_ui, listar_hojas, leer_dataframe
from utils.proteccion_tipos import convertir_tipos_preservando_ceros, mostrar_aviso_columnas_protegidas


def _guardar_en_sesion(df, archivo, hoja_seleccionada, columnas_protegidas):

    st.session_state["df_actual"] = df
    st.session_state["archivo_info"] = {
        "nombre": archivo.name if hasattr(archivo, "name") else st.session_state["archivo_info"]["nombre"],
        "tamano": archivo.size if hasattr(archivo, "size") else st.session_state["archivo_info"]["tamano"],
        "hoja": hoja_seleccionada,
    }
    st.session_state["columnas_protegidas_actual"] = columnas_protegidas


def _guardar_en_sesion_desde_bytes(df, hoja_seleccionada, columnas_protegidas):
    """Actualiza la sesión cuando se cambia de hoja sin subir el archivo de nuevo."""

    st.session_state["df_actual"] = df
    st.session_state["archivo_info"]["hoja"] = hoja_seleccionada
    st.session_state["columnas_protegidas_actual"] = columnas_protegidas


def limpiar_sesion_archivo():
    """Borra el archivo/DataFrame guardado, forzando a pedir uno nuevo."""

    for clave in ("df_actual", "archivo_info", "columnas_protegidas_actual", "archivo_bytes_sesion"):
        st.session_state.pop(clave, None)


def obtener_dataframe_sesion(permitir_filas_a_saltar=True, descripcion_modulo=None):
    """Flujo completo y reutilizable para los 3 módulos:

    1. Si ya hay un archivo cargado en esta sesión, lo reutiliza y muestra
       un resumen compacto con la opción de cambiar de hoja o subir otro archivo.
    2. Si no hay archivo en sesión, muestra el flujo normal de carga.

    Devuelve el DataFrame listo para usar, o None si todavía no hay nada
    cargado (en cuyo caso el módulo que llama debe hacer return).
    """

    archivo_en_sesion = "df_actual" in st.session_state

    if archivo_en_sesion:

        info = st.session_state["archivo_info"]
        nombre_archivo = info["nombre"]
        archivo_bytes  = st.session_state.get("archivo_bytes_sesion")

        # ── Encabezado: nombre del archivo + botón para cambiar ────
        col_info, col_boton = st.columns([4, 1])

        with col_info:
            st.success(
                f"Usando el archivo ya cargado: **{nombre_archivo}** "
                f"(hoja: {info['hoja']})"
            )

        with col_boton:
            if st.button("Subir otro archivo", use_container_width=True):
                limpiar_sesion_archivo()
                st.rerun()

        mostrar_aviso_columnas_protegidas(st.session_state.get("columnas_protegidas_actual", []))

        # ── Selector de hoja (solo si el archivo es Excel y tenemos los bytes) ──
        if (
            archivo_bytes is not None
            and not nombre_archivo.endswith(".csv")
        ):
            try:
                hojas_disponibles = listar_hojas(archivo_bytes)

                if len(hojas_disponibles) > 1:

                    hoja_actual = info["hoja"]
                    indice_actual = hojas_disponibles.index(hoja_actual) if hoja_actual in hojas_disponibles else 0

                    hoja_nueva = st.selectbox(
                        "Cambiar de hoja",
                        options=hojas_disponibles,
                        index=indice_actual,
                        key="selector_hoja_sesion"
                    )

                    if hoja_nueva != hoja_actual:
                        with st.spinner(f"Cargando hoja '{hoja_nueva}'..."):
                            df_nueva_hoja = leer_dataframe(
                                archivo_bytes,
                                nombre_archivo,
                                0,
                                tuple(),
                                hoja_nueva
                            )
                            df_nueva_hoja, columnas_protegidas = convertir_tipos_preservando_ceros(df_nueva_hoja)
                            _guardar_en_sesion_desde_bytes(df_nueva_hoja, hoja_nueva, columnas_protegidas)
                            st.rerun()

            except Exception:
                pass  # Si no se pueden listar las hojas, se omite silenciosamente

        return st.session_state["df_actual"]

    # ── No hay archivo en sesión: mensaje de bienvenida + carga ────

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

    # Guardar los bytes del archivo en sesión para poder cambiar de hoja después
    st.session_state["archivo_bytes_sesion"] = archivo_bytes

    _guardar_en_sesion(df, archivo, hoja_seleccionada, columnas_protegidas)

    return df