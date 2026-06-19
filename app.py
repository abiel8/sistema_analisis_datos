import streamlit as st

#from modules.dashboard import mostrar_dashboard
from modules.calidad_datos import mostrar_calidad_datos
#from modules.perfilado import mostrar_perfilado
from modules.etl import mostrar_etl
#from modules.reportes import mostrar_reportes
#from modules.datos_maestros import mostrar_datos_maestros
from modules.reglas_dinamicas import mostrar_reglas_dinamicas


st.set_page_config(
    page_title="Datos Maestros",
    page_icon="",
    layout="wide"
)

st.title("Gobernanza de Datos")

opcion = st.sidebar.selectbox(

    "Seleccione módulo",

    [
      
        "Calidad de Datos",
        "Reglas Dinámicas",
        "ETL"
    ]
)

#if opcion == "Dashboard":#

    #mostrar_dashboard()

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
    