import streamlit as st

from modules.dashboard import mostrar_dashboard
from modules.calidad_datos import mostrar_calidad_datos
from modules.etl import mostrar_etl
from utils.estilos import cargar_css


st.set_page_config(
    page_title="ZVMD",
    page_icon="assets/logo.png",
    layout="wide"
)

cargar_css("static/styles.css")

# ── Logo en el área beige, arriba a la izquierda ───
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    st.image("assets/Universidad-Zamorano-Logo-1024x220.png", use_container_width=True)

with col_titulo:
    st.title("VALIDADOR DE MIGRACIÓN DE DATOS (ZVMD)")

opcion = st.sidebar.radio(
    "Módulo",
    [
        "Metodos",
        "Calidad de Datos",
        "Dashboard"
    ]
)

if opcion == "Calidad de Datos":
    mostrar_calidad_datos()

elif opcion == "Metodos":
    mostrar_etl()

elif opcion == "Dashboard":
    mostrar_dashboard()
    
    