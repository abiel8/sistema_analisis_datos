import streamlit as st

from modules.dashboard import mostrar_dashboard
from modules.calidad_datos import mostrar_calidad_datos
from modules.etl import mostrar_etl
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

elif opcion == "ETL":

    mostrar_etl()


elif opcion == "Dashboard":

    mostrar_dashboard()