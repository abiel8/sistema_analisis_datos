import streamlit as st
import pandas as pd

from utils.carga_archivos import cargar_archivo
from utils.perfilado import perfil_columna


def mostrar_perfilado():

    st.header("Perfilado de Datos")

    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["xlsx", "csv"]
    )

    if archivo:

        df = cargar_archivo(archivo)

        perfiles = []

        for columna in df.columns:

            perfiles.append(
                perfil_columna(
                    df,
                    columna
                )
            )

        perfil_df = pd.DataFrame(
            perfiles
        )

        st.dataframe(
            perfil_df,
            use_container_width=True
        )