import streamlit as st
import pandas as pd


def mostrar_etl():

    st.header("ETL")

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

    # Vista previa cruda para que el usuario pueda identificar la fila correcta
    with st.expander("Ver archivo crudo (sin procesar)"):
        if archivo.name.endswith(".csv"):
            df_crudo = pd.read_csv(archivo, header=None, nrows=15)
        else:
            df_crudo = pd.read_excel(archivo, header=None, nrows=15)
        
        st.dataframe(df_crudo, use_container_width=True)
        archivo.seek(0)  # Resetear el puntero tras la vista previa

    # ── Cargar con el encabezado correcto ─────────────────────
    if archivo.name.endswith(".csv"):
        df_original = pd.read_csv(archivo, header=fila_encabezado)
    else:
        df_original = pd.read_excel(archivo, header=fila_encabezado)

    df = df_original.copy()

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)


    st.subheader("Transformaciones")

    # ── Limpieza ──────────────────────────────────────────────
    st.markdown("**Limpieza**")

    col1, col2, col3 = st.columns(3)

    eliminar_vacios = col1.checkbox("Eliminar filas vacías")
    eliminar_duplicados = col2.checkbox("Eliminar duplicados")
    eliminar_columnas_vacias = col3.checkbox("Eliminar columnas 100% vacías")

    # ── Texto ─────────────────────────────────────────────────
    st.markdown("**Texto**")

    col4, col5, col6 = st.columns(3)

    convertir_mayusculas = col4.checkbox("Convertir a MAYÚSCULAS")
    convertir_minusculas = col5.checkbox("Convertir a minúsculas")
    quitar_espacios     = col6.checkbox("Quitar espacios extremos (strip)")

    # ── Columnas ──────────────────────────────────────────────
    st.markdown("**Columnas**")

    col7, col8 = st.columns(2)

    limpiar_nombres = col7.checkbox("Limpiar nombres de columnas")
    eliminar_cols   = col8.checkbox("Eliminar columnas específicas")

    columnas_a_eliminar = []
    if eliminar_cols:
        columnas_a_eliminar = st.multiselect(
            "Seleccione columnas a eliminar",
            options=df.columns.tolist()
        )

    # ── Tipos de datos ────────────────────────────────────────
    st.markdown("**Tipos de datos**")

    col9, col10 = st.columns(2)

    inferir_tipos  = col9.checkbox("Inferir tipos automáticamente")
    rellenar_nulos = col10.checkbox("Rellenar nulos con valor personalizado")

    valor_relleno = None
    if rellenar_nulos:
        valor_relleno = st.text_input(
            "Valor para rellenar nulos (ej: 0, N/A, Desconocido)",
            value="N/A"
        )

    # ═══════════════════════════════════════════════════════════
    # Aplicar transformaciones
    # ═══════════════════════════════════════════════════════════

    filas_antes = len(df)
    cols_antes  = len(df.columns)

    if eliminar_columnas_vacias:
        df = df.dropna(axis=1, how="all")

    if eliminar_vacios:
        df = df.dropna()

    if eliminar_duplicados:
        df = df.drop_duplicates()

    if columnas_a_eliminar:
        df = df.drop(columns=columnas_a_eliminar, errors="ignore")

    if limpiar_nombres:
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"[^a-z0-9_]", "", regex=True)
        )

    columnas_texto = df.select_dtypes(include="object").columns

    if quitar_espacios:
        for col in columnas_texto:
            df[col] = df[col].astype(str).str.strip()

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

    if inferir_tipos:
        df = df.infer_objects()
        for col in df.select_dtypes(include="object").columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass  # Si no se puede convertir, se deja como está

    # ═══════════════════════════════════════════════════════════
    # Resumen del impacto
    # ═══════════════════════════════════════════════════════════

    st.subheader("Impacto de las transformaciones")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Filas originales",
        filas_antes
    )
    m2.metric(
        "Filas resultado",
        len(df),
        delta=len(df) - filas_antes
    )
    m3.metric(
        "Columnas originales",
        cols_antes
    )
    m4.metric(
        "Columnas resultado",
        len(df.columns),
        delta=len(df.columns) - cols_antes
    )

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

    buffer = __import__("io").BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    col_xlsx.download_button(
        label="Descargar Excel",
        data=buffer.getvalue(),
        file_name="resultado_etl.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )