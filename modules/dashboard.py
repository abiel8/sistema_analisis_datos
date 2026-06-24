import re

import pandas as pd
import streamlit as st

from utils.graficos import (
    grafico_barras,
    grafico_lineas,
    grafico_pastel,
    grafico_dispersion,
    calcular_calidad_columna,
    calcular_calidad_archivo,
    grafico_calidad_columna,
    grafico_calidad_archivo,
    calcular_distribucion_columna,
    grafico_distribucion_columna
)


def _columna_tiene_cero_inicial(serie):

    valores = serie.dropna().astype(str)

    if valores.empty:
        return False

    patron_cero_inicial = re.compile(r"^0\d+$")

    return valores.apply(lambda v: bool(patron_cero_inicial.match(v.strip()))).any()


def _convertir_tipos_preservando_ceros(df):

    columnas_protegidas = []

    for columna in df.columns:

        serie = df[columna]

        if _columna_tiene_cero_inicial(serie):
            df[columna] = serie.astype(str).str.strip()
            columnas_protegidas.append(columna)
            continue

        try:
            df[columna] = pd.to_numeric(serie)
        except (ValueError, TypeError):
            pass  # Se deja como texto

    return df, columnas_protegidas


def mostrar_dashboard():

    st.header("Dashboard")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv", "xls"]
    )

    if not archivo:
        return

    # ── Selección de hoja (solo para Excel) ────────────────────
    hoja_seleccionada = 0

    if not archivo.name.endswith(".csv"):
        try:
            xls = pd.ExcelFile(archivo)
            hojas_disponibles = xls.sheet_names

            if len(hojas_disponibles) > 1:
                hoja_seleccionada = st.selectbox(
                    "El archivo tiene varias hojas. Seleccione cuál usar:",
                    options=hojas_disponibles
                )
            else:
                hoja_seleccionada = hojas_disponibles[0]

        except Exception as e:
            st.error(f"No se pudo leer la lista de hojas del archivo: {e}")
            return

        finally:
            archivo.seek(0)

    # ── Configuración de lectura ───────────────────────────────
    st.subheader("Configuración de lectura")

    col_a, col_b = st.columns(2)

    fila_encabezado = col_a.number_input(
        "¿En qué fila está el encabezado? (0 = primera fila)",
        min_value=0,
        max_value=50,
        value=0,
        step=1
    )

    fila_inicio_datos = col_b.number_input(
        "¿En qué fila empiezan los datos?",
        min_value=int(fila_encabezado) + 1,
        max_value=100,
        value=int(fila_encabezado) + 1,
        step=1
    )

    filas_a_saltar = list(range(int(fila_encabezado) + 1, int(fila_inicio_datos)))

    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                dtype=str
            )
        elif archivo.name.endswith(".xls"):
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                sheet_name=hoja_seleccionada,
                dtype=str,
                engine="xlrd"
            )
        else:
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                sheet_name=hoja_seleccionada,
                dtype=str,
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
            "Falta una librería para leer este tipo de archivo. "
            "Si es un archivo .xls antiguo, instale xlrd con: pip install xlrd"
        )
        return

    except Exception as e:
        st.error(f"Ocurrió un error inesperado al leer el archivo: {e}")
        return

    if df.empty:
        st.warning("El archivo se leyó correctamente, pero no contiene datos con esta configuración.")
        return

    df, columnas_protegidas = _convertir_tipos_preservando_ceros(df)

    if columnas_protegidas:
        st.info(
            "Se detectaron y protegieron como texto estas columnas con ceros a la izquierda: "
            f"{', '.join(columnas_protegidas)}"
        )

    columnas = df.columns.tolist()
    columnas_numericas = df.select_dtypes(include="number").columns.tolist()

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)

    # ═══════════════════════════════════════════════════════════
    # Sección: Calidad de datos
    # ═══════════════════════════════════════════════════════════

    st.subheader("Calidad de datos")

    alcance = st.radio(
        "¿Qué quiere analizar?",
        options=["Una columna específica", "Todo el archivo"],
        horizontal=True,
        key="alcance_calidad"
    )

    n_caracteres = st.number_input(
        "Umbral de longitud mínima (para la condición 'Longitud < N')",
        min_value=1,
        max_value=200,
        value=5,
        step=1,
        key="n_caracteres_calidad"
    )

    if alcance == "Una columna específica":

        columna_calidad = st.selectbox(
            "Seleccione la columna a analizar",
            options=columnas,
            key="columna_calidad"
        )

        try:
            resultados = calcular_calidad_columna(df, columna_calidad, int(n_caracteres))

            c1, c2, c3 = st.columns(3)
            c1.metric("Vacíos", f"{resultados['Vacíos (%)']}%")
            c2.metric("Duplicados", f"{resultados['Duplicados (%)']}%")
            c3.metric(f"Longitud < {int(n_caracteres)}", f"{resultados[f'Longitud < {int(n_caracteres)} (%)']}%")

            tipo_grafico_calidad = st.selectbox(
                "Tipo de gráfico",
                ["Barras", "Pastel"],
                key="tipo_grafico_calidad_columna"
            )

            if tipo_grafico_calidad == "Barras":
                fig = grafico_calidad_columna(resultados, f"Calidad de '{columna_calidad}'")
                st.plotly_chart(fig, use_container_width=True)

            else:
                df_pastel = pd.DataFrame(
                    list(resultados.items()),
                    columns=["condicion", "porcentaje"]
                )
                fig = grafico_pastel(df_pastel, "condicion", "porcentaje")
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"No se pudo calcular la calidad de la columna: {e}")

    else:  # Todo el archivo

        try:
            df_calidad = calcular_calidad_archivo(df, int(n_caracteres))

            st.dataframe(df_calidad, use_container_width=True)

            condicion_a_graficar = st.selectbox(
                "Seleccione qué condición comparar entre columnas",
                options=[c for c in df_calidad.columns if c != "columna"],
                key="condicion_calidad_archivo"
            )

            fig = grafico_calidad_archivo(
                df_calidad,
                condicion_a_graficar,
                f"{condicion_a_graficar} por columna"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"No se pudo calcular la calidad del archivo: {e}")

    # ═══════════════════════════════════════════════════════════
    # Sección: Distribución por columna (categorías)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Distribución de una columna por categoría")

    columnas_distribucion = st.multiselect(
        "Seleccione una o más columnas a analizar",
        options=columnas,
        key="columnas_distribucion"
    )

    tipo_grafico_distribucion = st.radio(
        "Tipo de gráfico",
        options=["Pastel", "Barras"],
        horizontal=True,
        key="tipo_grafico_distribucion"
    )

    if columnas_distribucion:

        cols_dist = st.columns(2)

        for idx, col_dist in enumerate(columnas_distribucion):

            try:
                df_dist = calcular_distribucion_columna(df, col_dist)

                fig_dist = grafico_distribucion_columna(
                    df_dist,
                    f"Distribución de '{col_dist}'",
                    tipo_grafico_distribucion
                )

                cols_dist[idx % 2].plotly_chart(fig_dist, use_container_width=True)

                with cols_dist[idx % 2].expander(f"Ver detalle numérico de '{col_dist}'"):
                    st.dataframe(df_dist, use_container_width=True)

            except Exception as e:
                cols_dist[idx % 2].error(f"No se pudo analizar '{col_dist}': {e}")

    # ═══════════════════════════════════════════════════════════
    # Sección: Gráficos personalizados
    # ═══════════════════════════════════════════════════════════

    st.subheader("Configurar gráficos personalizados")

    num_graficos = st.number_input(
        "¿Cuántos gráficos quiere mostrar?",
        min_value=1,
        max_value=6,
        value=2,
        step=1,
        key="num_graficos_personalizados"
    )

    configuraciones = []

    for i in range(int(num_graficos)):

        with st.expander(f"Gráfico {i + 1}", expanded=True):

            tipo = st.selectbox(
                "Tipo de gráfico",
                ["Barras", "Líneas", "Pastel", "Dispersión"],
                key=f"tipo_{i}"
            )

            if tipo in ("Barras", "Líneas", "Dispersión"):

                col_x = st.selectbox(
                    "Columna X",
                    columnas,
                    key=f"x_{i}"
                )

                col_y = st.selectbox(
                    "Columna Y",
                    columnas_numericas if columnas_numericas else columnas,
                    key=f"y_{i}"
                )

                configuraciones.append({
                    "tipo": tipo,
                    "x": col_x,
                    "y": col_y
                })

            else:  # Pastel

                col_nombres = st.selectbox(
                    "Columna de categorías (nombres)",
                    columnas,
                    key=f"nombres_{i}"
                )

                col_valores = st.selectbox(
                    "Columna de valores",
                    columnas_numericas if columnas_numericas else columnas,
                    key=f"valores_{i}"
                )

                configuraciones.append({
                    "tipo": tipo,
                    "nombres": col_nombres,
                    "valores": col_valores
                })

    # ── Renderizar la cuadrícula de gráficos personalizados ─────
    st.subheader("Resultado")

    columnas_por_fila = 2
    filas = [
        configuraciones[i:i + columnas_por_fila]
        for i in range(0, len(configuraciones), columnas_por_fila)
    ]

    for fila in filas:

        cols_streamlit = st.columns(len(fila))

        for col_streamlit, config in zip(cols_streamlit, fila):

            try:
                if config["tipo"] == "Barras":
                    fig = grafico_barras(df, config["x"], config["y"])

                elif config["tipo"] == "Líneas":
                    fig = grafico_lineas(df, config["x"], config["y"])

                elif config["tipo"] == "Dispersión":
                    fig = grafico_dispersion(df, config["x"], config["y"])

                else:  # Pastel
                    fig = grafico_pastel(df, config["nombres"], config["valores"])

                col_streamlit.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                col_streamlit.error(f"No se pudo generar el gráfico: {e}")