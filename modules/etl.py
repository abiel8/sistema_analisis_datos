import io

import streamlit as st
import pandas as pd

from utils.carga_archivos import seleccionar_hoja_ui, leer_vista_cruda, cargar_dataframe_ui
from utils.proteccion_tipos import convertir_tipos_preservando_ceros, mostrar_aviso_columnas_protegidas
from utils.limpieza_texto import limpiar_texto_columna, limpiar_nombres_columnas
from utils.paises import columna_a_codigo_pais


def mostrar_etl():

    st.header("ETL")

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

    fila_encabezado = st.number_input(
        "¿En qué fila están los encabezados? (0 = primera fila)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
        help="Si tu Excel tiene títulos o metadatos arriba, indica cuántas filas saltarse."
    )

    # Vista previa cruda para que el usuario identifique la fila correcta
    with st.expander("Ver archivo crudo (sin procesar)"):
        try:
            df_crudo = leer_vista_cruda(archivo_bytes, archivo.name, hoja_seleccionada)
            st.dataframe(df_crudo, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo generar la vista previa cruda: {e}")

    df = cargar_dataframe_ui(archivo, fila_encabezado, [], hoja_seleccionada)

    if df is None:
        return

    df, columnas_protegidas = convertir_tipos_preservando_ceros(df)
    mostrar_aviso_columnas_protegidas(columnas_protegidas)

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