import streamlit as st

from utils.carga_archivos import cargar_archivo
from utils.reglas import ejecutar_regla


def mostrar_reglas_dinamicas():

    st.header("Generador de Reglas Dinámicas")

    archivo = st.file_uploader(
        "Seleccione archivo",
         type=["xlsx", "csv", "xls"]
    )

    if archivo:

        df = cargar_archivo(archivo)

        columna = st.selectbox(
            "Seleccione columna",
            df.columns
        )

        tipo_regla = st.selectbox(

            "Tipo de regla",

            [
                "Vacíos",
                "Duplicados",
                "Longitud Mayor",
                "Longitud Menor",
                "Solo números",
                "Solo letras"
            ]
        )

        valor = None

        if tipo_regla in [

            "Longitud Mayor",
            "Longitud Menor"

        ]:

            valor = st.number_input(

                "Valor",

                min_value=1,

                value=5

            )

        if st.button("Ejecutar"):

            errores = ejecutar_regla(

                df,

                columna,

                tipo_regla,

                valor

            )

            st.subheader(

                "Registros encontrados"

            )

            st.metric(

                "Cantidad",

                len(errores)

            )

            st.dataframe(

                errores,

                use_container_width=True

            )