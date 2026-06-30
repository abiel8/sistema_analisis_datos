import pandas as pd
import streamlit as st

from utils.sesion_archivo import obtener_dataframe_sesion
from utils.condiciones_dashboard import TIPOS_VALIDACION
from utils.graficos import grafico_pastel, grafico_pastel_con_cantidades, grafico_resumen_general, config_descarga_png
from utils.excel_export import generar_excel_consolidado


@st.cache_data(show_spinner=False)
def _evaluar_condicion_cacheada(df, columna, tipo, parametro):

    info = TIPOS_VALIDACION[tipo]
    funcion = info["funcion"]

    if info.get("necesita_parametro") == "texto":
        return funcion(df, columna, parametro)

    elif info.get("necesita_parametro") == "numero":
        return funcion(df, columna, int(parametro))

    else:
        return funcion(df, columna)


def mostrar_dashboard():

    st.header("Dashboard")

    df = obtener_dataframe_sesion(
        descripcion_modulo=(
            "Suba un archivo, marque las columnas que quiera validar (email, "
            "teléfono, vacíos, duplicados, etc.) y obtenga gráficos comparativos "
            "más un Excel descargable con el detalle de cada error."
        )
    )

    if df is None:
        return

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)

    # Espacio reservado: el pastel "Bueno/Malo" se llena al final del
    # análisis, pero se muestra aquí arriba, antes de todo lo demás
    placeholder_pastel_general = st.empty()

    # ── Filtrar antes de transformar ───────────────────────────
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

    columnas = df.columns.tolist()

    # ═══════════════════════════════════════════════════════════
    # Sección: Validación por columna (todo el archivo de una vez)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validación de todas las columnas")

    st.caption("Marque las columnas que quiera analizar.")

    # ── Grilla horizontal de checkboxes, una columna de Streamlit por cada
    # columna del archivo, agrupadas en filas de máximo 5 ────────────────
    MAXIMO_POR_FILA = 5
    columnas_marcadas = []

    for inicio in range(0, len(columnas), MAXIMO_POR_FILA):

        bloque = columnas[inicio:inicio + MAXIMO_POR_FILA]
        cols_streamlit = st.columns(len(bloque))

        for col_streamlit, col in zip(cols_streamlit, bloque):

            marcada = col_streamlit.checkbox(col, key=f"marcar_{col}")

            if marcada:
                columnas_marcadas.append(col)

    st.divider()

    # ── Configuración (groupbox) solo para las columnas marcadas ────────

    opciones_tipo = [t for t in TIPOS_VALIDACION.keys() if t != "Sin validar"]

    asignaciones = {}
    parametros_asignacion = {}

    if not columnas_marcadas:
        st.info("Marque al menos una columna arriba para visualizar sus condiciones.")

    for col in columnas_marcadas:

        with st.container(border=True):

            st.markdown(f"**{col}**")

            tipos_elegidos = st.multiselect(
                "Condiciones a evaluar",
                options=opciones_tipo,
                key=f"tipos_validacion_{col}"
            )

            if tipos_elegidos:

                asignaciones[col] = tipos_elegidos

                for tipo in tipos_elegidos:

                    info = TIPOS_VALIDACION[tipo]

                    if info and info.get("necesita_parametro") == "texto":
                        parametros_asignacion[(col, tipo)] = st.text_input(
                            f"Texto a buscar para '{tipo}'",
                            key=f"param_texto_{col}_{tipo}"
                        )

                    elif info and info.get("necesita_parametro") == "numero":
                        parametros_asignacion[(col, tipo)] = st.number_input(
                            f"Valor N para '{tipo}'",
                            min_value=1,
                            value=10,
                            step=1,
                            key=f"param_numero_{col}_{tipo}"
                        )

    ejecutar_analisis = st.button("Analizar todas las columnas marcadas")

    # Acumula el resultado de cada columna para la descarga consolidada
    resultados_para_excel = {}

    # Acumula el % de error de cada columna para el gráfico general final
    resumen_porcentajes = []

    # Acumula, a nivel de TODO el archivo, qué filas tuvieron error en
    # al menos una de las columnas analizadas (para el pastel simple)
    mascara_alguna_columna_mala = pd.Series(False, index=df.index)

    if ejecutar_analisis and asignaciones:

        barra_progreso = st.progress(0, text="Analizando columnas...")
        total_columnas_a_procesar = len(asignaciones)

        for indice_actual, (col, tipos) in enumerate(asignaciones.items()):

            barra_progreso.progress(
                (indice_actual) / total_columnas_a_procesar,
                text=f"Analizando '{col}' ({indice_actual + 1} de {total_columnas_a_procesar})..."
            )

            st.markdown(f"### {col} — *{', '.join(tipos)}*")

            try:
                mascaras_individuales = {}

                for tipo in tipos:

                    info = TIPOS_VALIDACION[tipo]

                    if info.get("necesita_parametro") == "texto":
                        texto = parametros_asignacion.get((col, tipo), "")

                        if not texto:
                            st.info(f"Escriba un texto a buscar para '{tipo}' en '{col}'.")
                            continue

                        mascaras_individuales[tipo] = _evaluar_condicion_cacheada(df, col, tipo, texto)

                    elif info.get("necesita_parametro") == "numero":
                        numero = int(parametros_asignacion.get((col, tipo), 10))
                        mascaras_individuales[tipo] = _evaluar_condicion_cacheada(df, col, tipo, numero)

                    else:
                        mascaras_individuales[tipo] = _evaluar_condicion_cacheada(df, col, tipo, None)

                if not mascaras_individuales:
                    continue

                # Clasificar cada fila con la primera condición que cumple,
                # en el orden en que el usuario las seleccionó
                categoria_por_fila = pd.Series("Correcto", index=df.index)

                for tipo, mascara in mascaras_individuales.items():
                    sin_categoria_aun = categoria_por_fila == "Correcto"
                    categoria_por_fila = categoria_por_fila.where(
                        ~(mascara & sin_categoria_aun), tipo
                    )

                conteo = categoria_por_fila.value_counts().reset_index()
                conteo.columns = ["categoria", "cantidad"]

                cantidad_total = len(df)
                conteo["porcentaje"] = round(conteo["cantidad"] / cantidad_total * 100, 2)

                cantidad_errores_columna = int((categoria_por_fila != "Correcto").sum())
                porcentaje_error_columna = (
                    round(cantidad_errores_columna / cantidad_total * 100, 2)
                    if cantidad_total else 0
                )

                resumen_porcentajes.append({
                    "columna": col,
                    "porcentaje_error": porcentaje_error_columna
                })

                mascara_alguna_columna_mala |= (categoria_por_fila != "Correcto")

                col_metric, col_chart = st.columns([1, 2])

                with col_metric:
                    for _, fila in conteo.iterrows():
                        st.metric(fila["categoria"], f"{fila['cantidad']} ({fila['porcentaje']}%)")

                with col_chart:
                    fig = grafico_pastel(conteo, "categoria", "cantidad")
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_col_{col}")

                df_con_categoria = df.copy()
                df_con_categoria.insert(0, "fila_excel", df_con_categoria.index + 2)
                df_con_categoria["categoria_error"] = categoria_por_fila

                mostrar_solo_errores = st.checkbox(
                    f"Mostrar solo filas con error en '{col}'",
                    value=True,
                    key=f"solo_errores_{col}"
                )

                df_mostrar = df_con_categoria

                if mostrar_solo_errores:
                    df_mostrar = df_mostrar[df_mostrar["categoria_error"] != "Correcto"]

                with st.expander(f"Ver filas de '{col}' ({len(df_mostrar)} filas)"):
                    st.dataframe(df_mostrar, use_container_width=True)

                # Para el Excel final: solo las filas con error en ESTA
                # columna específica (no las correctas), con la fila completa
                resultados_para_excel[col] = df_con_categoria[
                    df_con_categoria["categoria_error"] != "Correcto"
                ]

                st.divider()

            except Exception as e:
                st.error(f"No se pudo validar la columna '{col}': {e}")

        barra_progreso.progress(1.0, text="Análisis completo.")
        barra_progreso.empty()

        # ── Pastel simple arriba: % bueno vs % malo de todo el archivo ──
        cantidad_total_archivo = len(df)
        cantidad_filas_malas = int(mascara_alguna_columna_mala.sum())
        cantidad_filas_buenas = cantidad_total_archivo - cantidad_filas_malas

        df_pastel_general = pd.DataFrame({
            "categoria": ["Bueno", "Malo"],
            "cantidad": [cantidad_filas_buenas, cantidad_filas_malas]
        })

        with placeholder_pastel_general.container():
            st.subheader("Resultado general")

            fig_simple = grafico_pastel_con_cantidades(
                df_pastel_general, "categoria", "cantidad",
                titulo=f"Total de registros: {cantidad_total_archivo}"
            )

            config_pastel_general = config_descarga_png("resultado_general")

            st.plotly_chart(
                fig_simple, use_container_width=True,
                config=config_pastel_general, key="chart_general_simple"
            )

            porcentaje_bueno = round(cantidad_filas_buenas / cantidad_total_archivo * 100, 1) if cantidad_total_archivo else 0
            st.caption(
                f"{porcentaje_bueno}% de las filas no tuvieron ningún error en las "
                f"columnas analizadas ({len(asignaciones)} columna(s)). "
                "Use el ícono de cámara para descargar este gráfico como PNG."
            )

        # ── Resumen claro de lo que se encontró, antes del detalle ─
        total_filas_con_error = sum(len(df_res) for df_res in resultados_para_excel.values())
        columnas_sin_ningun_error = [
            fila["columna"] for fila in resumen_porcentajes
            if fila["porcentaje_error"] == 0
        ]

        st.success(
            f"**Análisis completo:** {len(asignaciones)} columna(s) revisada(s), "
            f"{total_filas_con_error} registro(s) con algún error encontrado en total."
        )

        if columnas_sin_ningun_error:
            st.caption(
                "Sin errores en: " + ", ".join(f"**{c}**" for c in columnas_sin_ningun_error)
            )

        # ── Gráfico general: % de error por columna analizada ──────
        if resumen_porcentajes:

            st.subheader("Resumen general")

            fig_general = grafico_resumen_general(resumen_porcentajes)
            config = config_descarga_png("resumen_general_calidad_datos")

            st.plotly_chart(fig_general, use_container_width=True, config=config)
            st.caption(
                "Pase el cursor sobre el gráfico y use el ícono de cámara "
                "en la barra superior para descargarlo como PNG."
            )

        # ── Descarga consolidada: un solo Excel, una hoja por columna ───
        if resultados_para_excel:

            st.subheader("Descargar todo")

            excel_bytes = generar_excel_consolidado(resultados_para_excel)

            st.download_button(
                label="Descargar Excel con todas las columnas analizadas",
                data=excel_bytes,
                file_name="analisis_calidad_datos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif ejecutar_analisis and not asignaciones:
        st.info("No marcó ninguna columna con condiciones de validación.")