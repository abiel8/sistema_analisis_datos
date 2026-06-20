import io

import streamlit as st
import pandas as pd

from utils.validaciones import columna_a_codigo_pais


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
        try:
            if archivo.name.endswith(".csv"):
                df_crudo = pd.read_csv(archivo, header=None, nrows=15)
            elif archivo.name.endswith(".xls"):
                df_crudo = pd.read_excel(archivo, header=None, nrows=15, engine="xlrd")
            else:
                df_crudo = pd.read_excel(archivo, header=None, nrows=15, engine="openpyxl")

            st.dataframe(df_crudo, use_container_width=True)

        except Exception as e:
            st.warning(f"No se pudo generar la vista previa cruda: {e}")

        finally:
            archivo.seek(0)  # Resetear el puntero tras la vista previa

    # ── Cargar con el encabezado correcto ─────────────────────
    try:
        if archivo.name.endswith(".csv"):
            df_original = pd.read_csv(archivo, header=int(fila_encabezado))
        elif archivo.name.endswith(".xls"):
            df_original = pd.read_excel(archivo, header=int(fila_encabezado), engine="xlrd")
        else:
            df_original = pd.read_excel(archivo, header=int(fila_encabezado), engine="openpyxl")

    except ValueError as e:
        st.error(
            "No se pudo leer el archivo con la configuración indicada. "
            f"Verifique la fila de encabezado. Detalle: {e}"
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

    if df_original.empty:
        st.warning("El archivo se leyó correctamente, pero no contiene datos con esta configuración.")
        return

    df = df_original.copy()

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Transformaciones")

    # ── Limpieza ──────────────────────────────────────────────
   # st.markdown("**Limpieza**")

    #col1, col2, col3 = st.columns(3)

    #eliminar_vacios = col1.checkbox("Eliminar filas vacías")
    #eliminar_duplicados = col2.checkbox("Eliminar duplicados")
    #eliminar_columnas_vacias = col3.checkbox("Eliminar columnas 100% vacías")

    # ── Texto ─────────────────────────────────────────────────
    st.markdown("**Texto**")

    col1, col2, col3 = st.columns(3)

    convertir_mayusculas = col1.checkbox("Convertir a MAYÚSCULAS")
    convertir_minusculas = col2.checkbox("Convertir a minúsculas")
    quitar_espacios     = col3.checkbox("Quitar espacios extremos (strip)")

    # ── Columnas ──────────────────────────────────────────────
    st.markdown("**Columnas**")

    col4, col5 = st.columns(2)

    limpiar_nombres = col4.checkbox("Limpiar nombres de columnas")
    eliminar_cols   = col5.checkbox("Eliminar columnas específicas")

    columnas_a_eliminar = []
    if eliminar_cols:
        columnas_a_eliminar = st.multiselect(
            "Seleccione columnas a eliminar",
            options=df.columns.tolist()
        )

    # ── Tipos de datos ────────────────────────────────────────
    st.markdown("**Tipos de datos**")

    col6, col7 = st.columns(2)

    #inferir_tipos  = col9.checkbox("Inferir tipos automáticamente")
    rellenar_nulos = col6.checkbox("Rellenar nulos con valor personalizado")

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

   # if eliminar_columnas_vacias:
       # df = df.dropna(axis=1, how="all")

    #if eliminar_vacios:
        #df = df.dropna()

    #if eliminar_duplicados:
        #df = df.drop_duplicates()

  #  if columnas_a_eliminar:
   #     df = df.drop(columns=columnas_a_eliminar, errors="ignore")

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

    # if inferir_tipos:
      #  df = df.infer_objects()
       # for col in df.select_dtypes(include="object").columns:
        #    try:
         #       df[col] = pd.to_numeric(df[col])
          #  except (ValueError, TypeError):
           #     pass  # Si no se puede convertir, se deja como está

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
    
    
    