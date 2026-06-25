import re

import pandas as pd
import streamlit as st

from utils.validaciones import CONDICIONES_DASHBOARD, TIPOS_VALIDACION
from utils.graficos import grafico_pastel


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

    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)
                
# ═══════════════════════════════════════════════════════════
    # Sección: Validación por columna (todo el archivo de una vez)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validación de todas las columnas")

    st.caption("Para cada columna que quiera analizar, seleccione una o más condiciones.")

    opciones_tipo = [t for t in TIPOS_VALIDACION.keys() if t != "Sin validar"]

    asignaciones = {}
    parametros_asignacion = {}

    for col in columnas:

        tipos_elegidos = st.multiselect(
            col,
            options=opciones_tipo,
            key=f"tipos_validacion_{col}"
        )

        if tipos_elegidos:

            asignaciones[col] = tipos_elegidos

            for tipo in tipos_elegidos:

                info = TIPOS_VALIDACION[tipo]

                if info and info.get("necesita_parametro") == "texto":
                    parametros_asignacion[(col, tipo)] = st.text_input(
                        f"Texto a buscar para '{tipo}' en '{col}'",
                        key=f"param_texto_{col}_{tipo}"
                    )

                elif info and info.get("necesita_parametro") == "numero":
                    parametros_asignacion[(col, tipo)] = st.number_input(
                        f"Valor N para '{tipo}' en '{col}'",
                        min_value=1,
                        value=10,
                        step=1,
                        key=f"param_numero_{col}_{tipo}"
                    )

    ejecutar_analisis = st.button("Analizar todas las columnas marcadas")
    
    if ejecutar_analisis and asignaciones:

        for col, tipos in asignaciones.items():

            st.markdown(f"### {col} — *{', '.join(tipos)}*")

            try:
                # Evaluar cada condición por separado
                mascaras_individuales = {}

                for tipo in tipos:

                    info = TIPOS_VALIDACION[tipo]
                    funcion = info["funcion"]

                    if info.get("necesita_parametro") == "texto":
                        texto = parametros_asignacion.get((col, tipo), "")

                        if not texto:
                            st.info(f"Escriba un texto a buscar para '{tipo}' en '{col}'.")
                            continue

                        mascaras_individuales[tipo] = funcion(df, col, texto)

                    elif info.get("necesita_parametro") == "numero":
                        numero = int(parametros_asignacion.get((col, tipo), 10))
                        mascaras_individuales[tipo] = funcion(df, col, numero)

                    else:
                        mascaras_individuales[tipo] = funcion(df, col)

                if not mascaras_individuales:
                    continue

                # Clasificar cada fila: la primera condición que cumple, en
                # el orden en que el usuario las seleccionó
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

                    if not df_mostrar.empty:
                        csv_col = df_mostrar.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label=f"Descargar filas de '{col}' (.csv)",
                            data=csv_col,
                            file_name=f"filas_{col}.csv",
                            mime="text/csv",
                            key=f"descargar_col_{col}"
                        )

                st.divider()

            except Exception as e:
                st.error(f"No se pudo validar la columna '{col}': {e}")

   

    elif ejecutar_analisis and not asignaciones:
        st.info("No marcó ninguna columna con condiciones de validación.")