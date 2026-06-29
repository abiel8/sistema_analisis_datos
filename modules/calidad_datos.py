import streamlit as st

from utils.carga_archivos import seleccionar_hoja_ui, cargar_dataframe_ui
from utils.proteccion_tipos import convertir_tipos_preservando_ceros, mostrar_aviso_columnas_protegidas
from utils.metricas_calidad import (
    contar_vacios, contar_duplicados, contar_unicos, longitud_mayor,
    contiene_numeros, contiene_letras, solo_numeros, solo_letras,
    caracteres_especiales
)
from utils.validaciones_email import resumen_validacion_email
from utils.validaciones_telefono import resumen_validacion_telefono_internacional


def mostrar_calidad_datos():

    st.header("Calidad de Datos")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv", "xls"]
    )

    if not archivo:
        return

    archivo_bytes = archivo.getvalue()

    # ── Selección de hoja (solo para Excel) ────────────────────
    hoja_seleccionada = seleccionar_hoja_ui(archivo, archivo_bytes)

    if hoja_seleccionada is None:
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

    filas_a_saltar = list(range(int(fila_encabezado) + 1, int(fila_inicio_datos)))

    df = cargar_dataframe_ui(archivo, fila_encabezado, filas_a_saltar, hoja_seleccionada)

    if df is None:
        return

    df, columnas_protegidas = convertir_tipos_preservando_ceros(df)
    mostrar_aviso_columnas_protegidas(columnas_protegidas)

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Selección de columna ────────────────────────────────────
    columna = st.selectbox(
        "Seleccione una columna para analizar",
        df.columns
    )

    # ═══════════════════════════════════════════════════════════
    # Resumen general de calidad (siempre visible)
    # ═══════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════
    # Validación de correos electrónicos (opcional)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validar correos electrónicos")

    validar_correos = st.checkbox(
        f"Validar formato de correos en la columna '{columna}'",
        key="check_validar_email"
    )

    if validar_correos:

        try:
            resultado_email = resumen_validacion_email(df, columna)

            ce1, ce2, ce3 = st.columns(3)
            ce1.metric("Total de registros", resultado_email["total"])
            ce2.metric("Válidos", resultado_email["validos"])
            ce3.metric("Inválidos", resultado_email["invalidos"])

            st.progress(resultado_email["porcentaje_validos"] / 100)
            st.caption(f"{resultado_email['porcentaje_validos']}% de correos válidos")

            df_detalle_email = df.copy()
            df_detalle_email.insert(0, "fila_excel", df_detalle_email.index + 2)
            df_detalle_email["diagnostico"] = resultado_email["detalle"]

            mostrar_solo_invalidos_email = st.checkbox(
                "Mostrar solo los inválidos",
                value=True,
                key="solo_invalidos_email"
            )

            if mostrar_solo_invalidos_email:
                df_detalle_email = df_detalle_email[df_detalle_email["diagnostico"] != "Válido"]

            st.dataframe(df_detalle_email, use_container_width=True)

            if not df_detalle_email.empty:
                csv_email = df_detalle_email.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Descargar diagnóstico de correos (.csv)",
                    data=csv_email,
                    file_name="diagnostico_correos.csv",
                    mime="text/csv",
                    key="descargar_diagnostico_email"
                )

        except Exception as e:
            st.error(f"No se pudo validar la columna de correos: {e}")

    # ═══════════════════════════════════════════════════════════
    # Validación de teléfonos (opcional, nacional + internacional)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validar números telefónicos")

    validar_telefonos = st.checkbox(
        f"Validar formato de teléfono en la columna '{columna}'",
        key="check_validar_telefono"
    )

    if validar_telefonos:

        try:
            resultado_tel = resumen_validacion_telefono_internacional(df, columna, "HN")

            ct1, ct2, ct3 = st.columns(3)
            ct1.metric("Total de registros", resultado_tel["total"])
            ct2.metric("Válidos", resultado_tel["validos"])
            ct3.metric("Inválidos", resultado_tel["invalidos"])

            st.progress(resultado_tel["porcentaje_validos"] / 100)
            st.caption(f"{resultado_tel['porcentaje_validos']}% de teléfonos válidos")

            df_detalle_tel = df.copy()
            df_detalle_tel.insert(0, "fila_excel", df_detalle_tel.index + 2)
            df_detalle_tel["diagnostico"] = resultado_tel["detalle"]

            mostrar_solo_invalidos_tel = st.checkbox(
                "Mostrar solo los inválidos",
                value=True,
                key="solo_invalidos_telefono"
            )

            if mostrar_solo_invalidos_tel:
                df_detalle_tel = df_detalle_tel[df_detalle_tel["diagnostico"] != "Válido"]

            st.dataframe(df_detalle_tel, use_container_width=True)

            if not df_detalle_tel.empty:
                csv_tel = df_detalle_tel.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Descargar diagnóstico de teléfonos (.csv)",
                    data=csv_tel,
                    file_name="diagnostico_telefonos.csv",
                    mime="text/csv",
                    key="descargar_diagnostico_telefono"
                )

        except Exception as e:
            st.error(f"No se pudo validar la columna de teléfonos: {e}")