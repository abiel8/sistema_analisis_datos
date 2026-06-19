import streamlit as st
import pandas as pd

from utils.carga_archivos import cargar_archivo


def mostrar_datos_maestros():

    st.header("Datos Maestros")

    tipo_catalogo = st.selectbox(

        "Seleccione el catálogo",

        [
            "Clientes",
            "Proveedores",
            "Productos"
        ]
    )

    archivo = st.file_uploader(

        "Seleccione archivo",

        type=["xlsx", "csv"]

    )

    if archivo:

        df = cargar_archivo(archivo)

        errores = []

        # CLIENTES
        if tipo_catalogo == "Clientes":

            for index, fila in df.iterrows():

                if pd.isna(fila["Nombre"]):

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "Nombre",
                        "Error": "Nombre obligatorio"

                    })

                if pd.isna(fila["Correo"]):

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "Correo",
                        "Error": "Correo obligatorio"

                    })

        # PROVEEDORES
        elif tipo_catalogo == "Proveedores":

            for index, fila in df.iterrows():

                if pd.isna(fila["RTN"]):

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "RTN",
                        "Error": "RTN obligatorio"

                    })

                if pd.isna(fila["Pais"]):

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "Pais",
                        "Error": "País obligatorio"

                    })

        # PRODUCTOS
        elif tipo_catalogo == "Productos":

            for index, fila in df.iterrows():

                if pd.isna(fila["Codigo"]):

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "Codigo",
                        "Error": "Código obligatorio"

                    })

                if fila["Precio"] <= 0:

                    errores.append({

                        "Fila": index + 2,
                        "Campo": "Precio",
                        "Error": "Precio inválido"

                    })

        # RESULTADOS

        st.subheader("Resumen")

        col1, col2 = st.columns(2)

        col1.metric(

            "Registros",

            len(df)

        )

        col2.metric(

            "Errores encontrados",

            len(errores)

        )

        if len(errores) > 0:

            errores_df = pd.DataFrame(

                errores

            )

            st.subheader(

                "Detalle de errores"

            )

            st.dataframe(

                errores_df,

                use_container_width=True

            )

        else:

            st.success(

                "No se encontraron errores"

            )