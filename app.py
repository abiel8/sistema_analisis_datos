import streamlit as st

from modules.dashboard import mostrar_dashboard
from modules.calidad_datos import mostrar_calidad_datos
#from modules.perfilado import mostrar_perfilado
from modules.etl import mostrar_etl
#from modules.reportes import mostrar_reportes
#from modules.datos_maestros import mostrar_datos_maestros
from modules.reglas_dinamicas import mostrar_reglas_dinamicas


st.set_page_config(
    page_title="Datos Maestros",
    page_icon="assets/logo.png",
    layout="wide"
)

# ── Estilos personalizados ──────────────────────────────────────
st.markdown(
    """
    <style>
        .stApp {
            background-color: #FFF4E5;
        }

        h1, h2, h3 {
            color: #036b39;
        }

        [data-testid="stSidebar"] {
            background-color: #048047;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        .stButton > button {
            background-color: #048047;
            color: #FFFFFF;
            border: none;
        }

        .stButton > button:hover {
            background-color: #036b39;
            color: #FFFFFF;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ── Logo en la barra lateral ────────────────────────────────────
st.sidebar.image("assets/logo.png", use_container_width=True)

st.title("Gobernanza de Datos")

opcion = st.sidebar.selectbox(

    "Seleccione módulo",

    [
        "Calidad de Datos",
        "Reglas Dinámicas",
        "ETL",
        "Dashboard"
    ]
)

if opcion == "Calidad de Datos":

    mostrar_calidad_datos()

#elif opcion == "Perfilado":

 #   mostrar_perfilado()

elif opcion == "ETL":

    mostrar_etl()

#elif opcion == "Reportes":

 #   mostrar_reportes()

#elif opcion == "Datos Maestros":

 #   mostrar_datos_maestros()

elif opcion == "Reglas Dinámicas":

    mostrar_reglas_dinamicas()

elif opcion == "Dashboard":

    mostrar_dashboard()