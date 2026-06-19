import streamlit as st
import pandas as pd

from utils.carga_archivos import cargar_archivo
from utils.exportar_excel import exportar_excel


def mostrar_reportes():

    st.header("Reportes")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv"]
    )

    if archivo:

        df = cargar_archivo(archivo)

        st.subheader("Vista previa")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        st.subheader("Exportación")

        # ========================
        # Excel
        # ========================

        excel_data = exportar_excel(df)

        st.download_button(

            label="📊 Descargar Excel",

            data=excel_data,

            file_name="reporte.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

        # ========================
        # CSV
        # ========================

        csv_data = df.to_csv(
            index=False
        )

        st.download_button(

            label="📑 Descargar CSV",

            data=csv_data,

            file_name="reporte.csv",

            mime="text/csv"

        )

        # ========================
        # Estadísticas
        # ========================

        st.subheader("Resumen")

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Registros",

            len(df)

        )

        col2.metric(

            "Columnas",

            len(df.columns)

        )

        col3.metric(

            "Valores Vacíos",

            df.isna().sum().sum()

        )

        # ========================
        # Información de columnas
        # ========================

        info_columnas = []

        for columna in df.columns:

            info_columnas.append({

                "Columna":
                columna,

                "Tipo":
                str(df[columna].dtype),

                "Vacíos":
                df[columna].isna().sum(),

                "Únicos":
                df[columna].nunique()

            })

        st.subheader(
            "Información de columnas"
        )

        st.dataframe(
            pd.DataFrame(
                info_columnas
            ),
            use_container_width=True
        )