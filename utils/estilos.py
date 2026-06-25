import streamlit as st


def cargar_css(ruta_css):

    with open(ruta_css, "r", encoding="utf-8") as archivo_css:
        css = archivo_css.read()

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)