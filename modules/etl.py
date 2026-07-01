import io

import streamlit as st
import pandas as pd

from utils.sesion_archivo import obtener_dataframe_sesion
from utils.limpieza_texto import limpiar_texto_columna, limpiar_nombres_columnas
from utils.paises import columna_a_codigo_pais
from utils.transformaciones import (
    dividir_nombre_apellido,
    estandarizar_fechas,
    reemplazar_en_dataframe,
    FORMATOS_FECHA
)


def mostrar_etl():

    st.header("ETL")

    df_original = obtener_dataframe_sesion(
        permitir_filas_a_saltar=False,
        descripcion_modulo=(
            "Suba un archivo para limpiarlo: quitar tildes, convertir a "
            "mayúsculas/minúsculas, rellenar vacíos, o extraer el país desde "
            "una columna de texto. Descargue el resultado en CSV o Excel."
        )
    )

    if df_original is None:
        return

    df = df_original.copy()

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Filtro previo ───────────────────────────────────────────
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

    # ═══════════════════════════════════════════════════════════
    # Transformaciones agrupadas en groupboxes
    # ═══════════════════════════════════════════════════════════

    st.subheader("Transformaciones")

    # ── Fila 1: Texto | Columnas ────────────────────────────────
    col_gb1, col_gb2 = st.columns(2)

    with col_gb1:
        with st.container(border=True):
            st.markdown("**Texto**")
            convertir_mayusculas = st.checkbox("Convertir a MAYÚSCULAS")
            convertir_minusculas = st.checkbox("Convertir a minúsculas")
            limpiar_texto        = st.checkbox("Limpiar texto (tildes, ñ, puntuación, espacios)")

    with col_gb2:
        with st.container(border=True):
            st.markdown("**Columnas**")
            limpiar_nombres = st.checkbox("Limpiar nombres de columnas")
            eliminar_cols   = st.checkbox("Eliminar columnas específicas")

            columnas_a_eliminar = []
            if eliminar_cols:
                columnas_a_eliminar = st.multiselect(
                    "Seleccione columnas a eliminar",
                    options=df.columns.tolist()
                )

    # ── Fila 2: Nulos | País ────────────────────────────────────
    col_gb3, col_gb4 = st.columns(2)

    with col_gb3:
        with st.container(border=True):
            st.markdown("**Nulos**")
            rellenar_nulos = st.checkbox("Rellenar nulos con valor personalizado")

            valor_relleno = None
            if rellenar_nulos:
                valor_relleno = st.text_input(
                    "Valor para rellenar nulos",
                    value="N/A"
                )

    with col_gb4:
        with st.container(border=True):
            st.markdown("**Extracción de país**")
            extraer_pais = st.checkbox("Extraer código de país desde texto")

            columna_direccion = None
            nombre_columna_resultado = "pais_codigo"

            if extraer_pais:
                columna_direccion = st.selectbox(
                    "Columna con dirección/país",
                    options=df.columns.tolist(),
                    key="col_direccion_pais"
                )
                nombre_columna_resultado = st.text_input(
                    "Nombre de la nueva columna",
                    value="pais_codigo"
                )

    # ── Groupbox: Dividir nombres ───────────────────────────────
    with st.container(border=True):
        st.markdown("**Dividir nombres**")
        dividir_nombres = st.checkbox("Separar nombre completo en nombre y apellido")

        columna_nombres    = None
        col_nombre_nuevo   = "nombre"
        col_apellido_nuevo = "apellido"

        if dividir_nombres:
            col_d1, col_d2, col_d3 = st.columns(3)
            columna_nombres    = col_d1.selectbox("Columna a dividir", options=df.columns.tolist(), key="col_dividir_nombre")
            col_nombre_nuevo   = col_d2.text_input("Nombre para la columna 'nombre'", value="nombre")
            col_apellido_nuevo = col_d3.text_input("Nombre para la columna 'apellido'", value="apellido")

    # ── Groupbox: Fechas ────────────────────────────────────────
    with st.container(border=True):
        st.markdown("**Estandarizar fechas**")
        estandarizar = st.checkbox("Convertir fechas a un formato estándar")

        columna_fecha   = None
        formato_destino = "DD/MM/YYYY"
        alcance_fecha   = "Por columna específica"

        if estandarizar:
            col_f1, col_f2, col_f3 = st.columns(3)

            alcance_fecha = col_f1.radio(
                "Aplicar a",
                options=["Por columna específica", "Todas las columnas"],
                key="alcance_fecha",
                horizontal=True
            )

            if alcance_fecha == "Por columna específica":
                columna_fecha = col_f2.selectbox(
                    "Columna de fechas",
                    options=df.columns.tolist(),
                    key="col_fecha"
                )

            formato_destino = col_f3.selectbox(
                "Formato destino",
                options=list(FORMATOS_FECHA.keys()),
                key="formato_fecha"
            )

    # ── Groupbox: Reemplazar valores ────────────────────────────
    with st.container(border=True):
        st.markdown("**Reemplazar valores**")
        hacer_reemplazo = st.checkbox("Buscar y reemplazar un valor")

        columna_reemplazo = None
        valor_buscar      = ""
        valor_nuevo       = ""
        alcance_reemplazo = "Por columna específica"
        exacto            = True

        if hacer_reemplazo:
            col_r1, col_r2, col_r3 = st.columns(3)

            alcance_reemplazo = col_r1.radio(
                "Aplicar a",
                options=["Por columna específica", "Todas las columnas"],
                key="alcance_reemplazo",
                horizontal=True
            )

            if alcance_reemplazo == "Por columna específica":
                columna_reemplazo = col_r1.selectbox(
                    "Columna",
                    options=df.columns.tolist(),
                    key="col_reemplazo"
                )

            valor_buscar = col_r2.text_input("Buscar", key="val_buscar")
            valor_nuevo  = col_r3.text_input("Reemplazar por", key="val_nuevo")
            exacto = st.checkbox(
                "Coincidencia exacta (la celda completa debe ser igual al valor buscado)",
                value=True,
                key="exacto_reemplazo"
            )

    # ═══════════════════════════════════════════════════════════
    # Aplicar todas las transformaciones
    # ═══════════════════════════════════════════════════════════

    filas_antes = len(df)
    cols_antes  = len(df.columns)

    if columnas_a_eliminar:
        df = df.drop(columns=columnas_a_eliminar, errors="ignore")

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
                    f"Se generó '{nombre_columna_resultado}'. "
                    f"{no_encontrados} fila(s) sin país reconocido."
                )
        except Exception as e:
            st.error(f"No se pudo extraer el país: {e}")

    if dividir_nombres and columna_nombres:
        try:
            partes = dividir_nombre_apellido(df[columna_nombres])
            df[col_nombre_nuevo]   = partes["nombre"]
            df[col_apellido_nuevo] = partes["apellido"]
            st.info(f"Se dividió '{columna_nombres}' en '{col_nombre_nuevo}' y '{col_apellido_nuevo}'.")
        except Exception as e:
            st.error(f"No se pudo dividir la columna de nombres: {e}")

    if estandarizar:
        try:
            if alcance_fecha == "Por columna específica" and columna_fecha:
                df[columna_fecha] = estandarizar_fechas(df[columna_fecha], formato_destino)
                st.info(f"Fechas de '{columna_fecha}' estandarizadas a {formato_destino}.")
            elif alcance_fecha == "Todas las columnas":
                for col in df.select_dtypes(include="object").columns:
                    df[col] = estandarizar_fechas(df[col], formato_destino)
                st.info(f"Fechas estandarizadas a {formato_destino} en todas las columnas de texto.")
        except Exception as e:
            st.error(f"No se pudieron estandarizar las fechas: {e}")

    if hacer_reemplazo and valor_buscar:
        try:
            col_destino = columna_reemplazo if alcance_reemplazo == "Por columna específica" else "__TODAS__"
            df = reemplazar_en_dataframe(df, col_destino, valor_buscar, valor_nuevo, exacto)
            st.info(
                f"Reemplazado '{valor_buscar}' por '{valor_nuevo}' "
                f"en {'todas las columnas' if col_destino == '__TODAS__' else col_destino}."
            )
        except Exception as e:
            st.error(f"No se pudo aplicar el reemplazo: {e}")

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
            "Listo. Calidad de Datos y Dashboard ahora usarán "
            "esta versión transformada del archivo."
        )