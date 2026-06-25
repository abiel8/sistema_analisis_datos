import streamlit as st

from modules.dashboard import mostrar_dashboard
from modules.calidad_datos import mostrar_calidad_datos
#from modules.perfilado import mostrar_perfilado
from modules.etl import mostrar_etl
#from modules.reportes import mostrar_reportes
#from modules.datos_maestros import mostrar_datos_maestros
from modules.reglas_dinamicas import mostrar_reglas_dinamicas
from utils.estilos import cargar_css


st.set_page_config(
    page_title="Datos Maestros",
    page_icon="assets/logo.png",
    layout="wide"
)

cargar_css("static/styles.css")

# ── Logo en la barra lateral, con fondo propio para contraste ───
with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/logo.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("Gobernanza de Datos")

opcion = st.sidebar.selectbox(

    "Seleccione módulo",

    [
        "Calidad de Datos",
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

#elif opcion == "Reglas Dinámicas":

 #   mostrar_reglas_dinamicas()

elif opcion == "Dashboard":

    mostrar_dashboard()