import io

import streamlit as st
import pandas as pd

from utils.sesion_archivo import obtener_dataframe_sesion
from utils.limpieza_texto import limpiar_texto_columna, limpiar_nombres_columnas
from utils.paises import columna_a_codigo_pais


def mostrar_etl():

    st.header("ETL")

    df_original = obtener_dataframe_sesion(permitir_filas_a_saltar=False)

    if df_original is None:
        return

    # Se trabaja sobre una copia: el ETL no debe alterar el DataFrame que
    # está en sesión hasta que el usuario decida explícitamente actualizarlo
    df = df_original.copy()

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Filtro previo (opcional) ────────────────────────────────
    st.subheader("Filtrar antes de transformar")

    aplicar_filtro_previo = st.checkbox("Filtrar filas antes de aplicar el ETL")

    if aplicar_filtro_previo:

        col_filtro = st.selectbox(
            "Seleccione la columna para filtrar",
            options=df.columns.tolist(),
            key="col_filtro_previo"
        )

        valores_disponibles = df[col_filtro].dropna().unique().tolist()

        valores_seleccionados = st.multiselect(
            f"Seleccione el/los valor(es) de '{col_filtro}' a conservar",
            options=valores_disponibles,
            key="valores_filtro_previo"
        )

        if valores_seleccionados:
            df = df[df[col_filtro].isin(valores_seleccionados)]

            st.success(
                f"Filtro aplicado: {len(df)} fila(s) coinciden con "
                f"{', '.join(str(v) for v in valores_seleccionados)} en '{col_filtro}'."
            )
        else:
            st.info("Seleccione al menos un valor para aplicar el filtro.")

    st.subheader("Transformaciones")

    # ── Texto ─────────────────────────────────────────────────
    st.markdown("**Texto**")

    col1, col2, col3 = st.columns(3)

    convertir_mayusculas = col1.checkbox("Convertir a MAYÚSCULAS")
    convertir_minusculas = col2.checkbox("Convertir a minúsculas")
    limpiar_texto        = col3.checkbox("Limpiar texto (tildes, ñ, puntuación, espacios)")

    # ── Columnas ──────────────────────────────────────────────
    st.markdown("**Columnas**")

    limpiar_nombres = st.checkbox("Limpiar nombres de columnas")

    # ── Tipos de datos ────────────────────────────────────────
    st.markdown("**Tipos de datos**")

    rellenar_nulos = st.checkbox("Rellenar nulos con valor personalizado")

    valor_relleno = None
    if rellenar_nulos:
        valor_relleno = st.text_input(
            "Valor para rellenar nulos (ej: 0, N/A, Desconocido)",
            value="N/A"
        )

    # ── Extracción de país ─────────────────────────────────────
    st.markdown("**Extracción de país**")

    extraer_pais = st.checkbox("Extraer código de país desde una columna de texto")

    columna_direccion = None
    nombre_columna_resultado = "pais_codigo"

    if extraer_pais:

        columna_direccion = st.selectbox(
            "Seleccione la columna que contiene la dirección/país",
            options=df.columns.tolist(),
            key="col_direccion_pais"
        )

        nombre_columna_resultado = st.text_input(
            "Nombre de la nueva columna",
            value="pais_codigo"
        )

    # ═══════════════════════════════════════════════════════════
    # Aplicar transformaciones
    # ═══════════════════════════════════════════════════════════

    filas_antes = len(df)
    cols_antes  = len(df.columns)

    if limpiar_nombres:
        df.columns = limpiar_nombres_columnas(df.columns)

    columnas_texto = df.select_dtypes(include="object").columns

    if limpiar_texto:
        for col in columnas_texto:
            df[col] = limpiar_texto_columna(df[col])

    if convertir_mayusculas and not convertir_minusculas:
        for col in columnas_texto:
            df[col] = df[col].astype(str).str.upper()

    if convertir_minusculas and not convertir_mayusculas:
        for col in columnas_texto:
            df[col] = df[col].astype(str).str.lower()

    if convertir_mayusculas and convertir_minusculas:
        st.warning("Seleccionó MAYÚSCULAS y minúsculas a la vez — no se aplicó ninguna.")

    if rellenar_nulos and valor_relleno is not None:
        df = df.fillna(valor_relleno)

    if extraer_pais and columna_direccion:
        try:
            df[nombre_columna_resultado] = columna_a_codigo_pais(df, columna_direccion)

            no_encontrados = df[nombre_columna_resultado].isna().sum()

            if no_encontrados > 0:
                st.info(
                    f"Se generó la columna '{nombre_columna_resultado}'. "
                    f"{no_encontrados} fila(s) no coincidieron con ningún país conocido."
                )

        except Exception as e:
            st.error(f"No se pudo extraer el país: {e}")

    # ═══════════════════════════════════════════════════════════
    # Resumen del impacto
    # ═══════════════════════════════════════════════════════════

    st.subheader("Impacto de las transformaciones")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Filas originales", filas_antes)
    m2.metric("Filas resultado", len(df), delta=len(df) - filas_antes)
    m3.metric("Columnas originales", cols_antes)
    m4.metric("Columnas resultado", len(df.columns), delta=len(df.columns) - cols_antes)

    # ═══════════════════════════════════════════════════════════
    # Resultado y descarga
    # ═══════════════════════════════════════════════════════════

    st.subheader("Resultado")
    st.dataframe(df, use_container_width=True)

    col_csv, col_xlsx = st.columns(2)

    col_csv.download_button(
        label="Descargar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="resultado_etl.csv",
        mime="text/csv",
        use_container_width=True
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    col_xlsx.download_button(
        label="Descargar Excel",
        data=buffer.getvalue(),
        file_name="resultado_etl.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.divider()

    if st.button(
        "Usar este resultado en Calidad de Datos y Dashboard",
        help="Reemplaza el archivo cargado en sesión por esta versión transformada."
    ):
        st.session_state["df_actual"] = df
        st.success(
            "Listo. Calidad de Datos y Dashboard ahora usarán esta versión "
            "transformada del archivo."
        )