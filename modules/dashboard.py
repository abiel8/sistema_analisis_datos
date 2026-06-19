import pandas as pd
import streamlit as st

from utils.graficos import (
    grafico_barras,
    grafico_lineas,
    grafico_pastel,
    grafico_dispersion
)


def mostrar_dashboard():

    st.header("Dashboard")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv"]
    )

    if not archivo:
        return

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
                skiprows=filas_a_saltar
            )
        elif archivo.name.endswith(".xls"):
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
                engine="xlrd"
            )
        else:
            df = pd.read_excel(
                archivo,
                header=int(fila_encabezado),
                skiprows=filas_a_saltar,
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

    columnas = df.columns.tolist()
    columnas_numericas = df.select_dtypes(include="number").columns.tolist()

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)

    # ── Configuración del dashboard ─────────────────────────────
    st.subheader("Configurar gráficos")

    num_graficos = st.number_input(
        "¿Cuántos gráficos quiere mostrar?",
        min_value=1,
        max_value=6,
        value=2,
        step=1
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

    # ── Renderizar la cuadrícula de gráficos ────────────────────
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