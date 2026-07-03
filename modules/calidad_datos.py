import streamlit as st

from utils.sesion_archivo import obtener_dataframe_sesion
from utils.metricas_calidad import (
    contar_vacios, contar_duplicados, contar_unicos, longitud_mayor,
    contiene_numeros, contiene_letras, solo_numeros, solo_letras,
    caracteres_especiales
)
from utils.validaciones_email import resumen_validacion_email
from utils.validaciones_telefono import resumen_validacion_telefono_internacional
from utils.plantillas import (
    guardar_plantilla_calidad, cargar_plantilla_calidad,
    listar_plantillas, eliminar_plantilla, nombre_plantilla_existe
)


def mostrar_calidad_datos():

    st.header("Calidad de Datos")

    df = obtener_dataframe_sesion(
        descripcion_modulo=(
            "Suba un archivo y elija una columna para revisar vacíos, duplicados, "
            "formato de texto, y validar correos o números telefónicos."
        )
    )

    if df is None:
        return

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    # ── Plantillas ──────────────────────────────────────────────
    plantillas_disponibles = listar_plantillas(tipo="calidad")
    plantilla_activa = {}

    with st.expander("Plantillas", expanded=False):

        col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
        nombres_plantillas = [p["nombre"] for p in plantillas_disponibles]

        if nombres_plantillas:

            plantilla_elegida = col_p1.selectbox(
                "Plantillas guardadas",
                options=["— Seleccione una plantilla —"] + nombres_plantillas,
                key="plantilla_seleccionada_calidad"
            )

            if col_p2.button("Cargar", key="btn_cargar_calidad", use_container_width=True):
                if plantilla_elegida != "— Seleccione una plantilla —":
                    datos = cargar_plantilla_calidad(plantilla_elegida)
                    if datos:
                        st.session_state["plantilla_calidad_activa"] = datos
                        st.success(f"Plantilla '{plantilla_elegida}' cargada.")
                        st.rerun()
                    else:
                        st.error("No se pudo cargar la plantilla.")

            if col_p3.button("Eliminar", key="btn_eliminar_calidad", use_container_width=True):
                if plantilla_elegida != "— Seleccione una plantilla —":
                    eliminar_plantilla(plantilla_elegida)
                    st.session_state.pop("plantilla_calidad_activa", None)
                    st.success(f"Plantilla '{plantilla_elegida}' eliminada.")
                    st.rerun()

        else:
            col_p1.caption("No hay plantillas guardadas aún.")

        st.divider()

        col_n1, col_n2 = st.columns([3, 1])
        nombre_nueva = col_n1.text_input(
            "Nombre para guardar la configuración actual como plantilla",
            placeholder="ej: Revisión de Contactos",
            key="nombre_nueva_plantilla_calidad"
        )

        if col_n2.button("Guardar", key="btn_guardar_calidad", use_container_width=True):
            if nombre_nueva.strip():
                col_actual = st.session_state.get("columna_calidad_actual", df.columns[0])
                email_actual = st.session_state.get("check_validar_email", False)
                tel_actual = st.session_state.get("check_validar_telefono", False)
                ya_existe = nombre_plantilla_existe(nombre_nueva.strip())
                guardar_plantilla_calidad(nombre_nueva.strip(), col_actual, email_actual, tel_actual)
                msg = "actualizada" if ya_existe else "guardada"
                st.success(f"Plantilla '{nombre_nueva.strip()}' {msg}.")
                st.rerun()
            else:
                st.warning("Escriba un nombre para la plantilla.")

    plantilla_activa = st.session_state.get("plantilla_calidad_activa", {})

    # ── Selección de columna ────────────────────────────────────
    col_default = plantilla_activa.get("columna", df.columns[0])
    col_index = list(df.columns).index(col_default) if col_default in df.columns else 0

    columna = st.selectbox(
        "Seleccione una columna para analizar",
        df.columns,
        index=col_index,
        key="columna_calidad_actual"
    )

    # ═══════════════════════════════════════════════════════════
    # Resumen general de calidad (siempre visible)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Resumen de calidad")

    try:
        c1, c2, c3 = st.columns(3)
        c1.metric("Vacíos",                contar_vacios(df, columna))
        c2.metric("Duplicados",            contar_duplicados(df, columna))
        c3.metric("Únicos",                contar_unicos(df, columna))

        c4, c5, c6 = st.columns(3)
        c4.metric("Longitud > 10",         longitud_mayor(df, columna, 10))
        c5.metric("Contiene números",      contiene_numeros(df, columna))
        c6.metric("Contiene letras",       contiene_letras(df, columna))

        c7, c8, c9 = st.columns(3)
        c7.metric("Solo números",          solo_numeros(df, columna))
        c8.metric("Solo letras",           solo_letras(df, columna))
        c9.metric("Caracteres especiales", caracteres_especiales(df, columna))

    except Exception as e:
        st.error(f"No se pudieron calcular las métricas para la columna '{columna}': {e}")
        return

    # ═══════════════════════════════════════════════════════════
    # Validación de correos electrónicos (opcional)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validar correos electrónicos")

    validar_correos = st.checkbox(
        f"Validar formato de correos en la columna '{columna}'",
        key="check_validar_email",
        value=plantilla_activa.get("validar_email", False)
    )

    if validar_correos:

        try:
            resultado_email = resumen_validacion_email(df, columna)

            ce1, ce2, ce3 = st.columns(3)
            ce1.metric("Total de registros", resultado_email["total"])
            ce2.metric("Válidos", resultado_email["validos"])
            ce3.metric("Inválidos", resultado_email["invalidos"])

            st.progress(resultado_email["porcentaje_validos"] / 100)
            st.caption(f"{resultado_email['porcentaje_validos']}% de correos válidos")

            df_detalle_email = df.copy()
            df_detalle_email.insert(0, "fila_excel", df_detalle_email.index + 2)
            df_detalle_email["diagnostico"] = resultado_email["detalle"]

            mostrar_solo_invalidos_email = st.checkbox(
                "Mostrar solo los inválidos",
                value=True,
                key="solo_invalidos_email"
            )

            if mostrar_solo_invalidos_email:
                df_detalle_email = df_detalle_email[df_detalle_email["diagnostico"] != "Válido"]

            st.dataframe(df_detalle_email, use_container_width=True)

            if not df_detalle_email.empty:
                csv_email = df_detalle_email.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Descargar diagnóstico de correos (.csv)",
                    data=csv_email,
                    file_name="diagnostico_correos.csv",
                    mime="text/csv",
                    key="descargar_diagnostico_email"
                )

        except Exception as e:
            st.error(f"No se pudo validar la columna de correos: {e}")

    # ═══════════════════════════════════════════════════════════
    # Validación de teléfonos (opcional, nacional + internacional)
    # ═══════════════════════════════════════════════════════════

    st.subheader("Validar números telefónicos")

    validar_telefonos = st.checkbox(
        f"Validar formato de teléfono en la columna '{columna}'",
        key="check_validar_telefono",
        value=plantilla_activa.get("validar_telefono", False)
    )

    if validar_telefonos:

        try:
            resultado_tel = resumen_validacion_telefono_internacional(df, columna, "HN")

            ct1, ct2, ct3 = st.columns(3)
            ct1.metric("Total de registros", resultado_tel["total"])
            ct2.metric("Válidos", resultado_tel["validos"])
            ct3.metric("Inválidos", resultado_tel["invalidos"])

            st.progress(resultado_tel["porcentaje_validos"] / 100)
            st.caption(f"{resultado_tel['porcentaje_validos']}% de teléfonos válidos")

            df_detalle_tel = df.copy()
            df_detalle_tel.insert(0, "fila_excel", df_detalle_tel.index + 2)
            df_detalle_tel["diagnostico"] = resultado_tel["detalle"]

            mostrar_solo_invalidos_tel = st.checkbox(
                "Mostrar solo los inválidos",
                value=True,
                key="solo_invalidos_telefono"
            )

            if mostrar_solo_invalidos_tel:
                df_detalle_tel = df_detalle_tel[df_detalle_tel["diagnostico"] != "Válido"]

            st.dataframe(df_detalle_tel, use_container_width=True)

            if not df_detalle_tel.empty:
                csv_tel = df_detalle_tel.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Descargar diagnóstico de teléfonos (.csv)",
                    data=csv_tel,
                    file_name="diagnostico_telefonos.csv",
                    mime="text/csv",
                    key="descargar_diagnostico_telefono"
                )

        except Exception as e:
            st.error(f"No se pudo validar la columna de teléfonos: {e}")