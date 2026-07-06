import pandas as pd
import plotly.express as px


# ═══════════════════════════════════════════════════════════════
# Gráficos básicos
# ═══════════════════════════════════════════════════════════════

def grafico_pastel(df, nombres, valores):

    return px.pie(df, names=nombres, values=valores)


def grafico_pastel_con_cantidades(df, nombres, valores, titulo=None):
    """Pastel donde cada porción muestra 'etiqueta: cantidad' directamente
    sobre el gráfico, para que esos números queden incluidos al exportar
    la imagen como PNG (las métricas de Streamlit no se capturan en la
    descarga, pero el texto dentro de la figura sí)."""

    fig = px.pie(df, names=nombres, values=valores, title=titulo)

    fig.update_traces(
        textinfo="label+value",
        texttemplate="%{label}: %{value}"
    )

    return fig


# ═══════════════════════════════════════════════════════════════
# Resumen general: comparación de % de error entre columnas
# ═══════════════════════════════════════════════════════════════

def grafico_resumen_general(resumen_porcentajes, titulo_extra=None):

    df_resumen = pd.DataFrame(resumen_porcentajes)

    titulo = "Porcentaje de error por columna analizada"
    if titulo_extra:
        titulo += f"  |  {titulo_extra}"

    return px.bar(
        df_resumen,
        x="columna",
        y="porcentaje_error",
        title=titulo,
        labels={"columna": "Columna", "porcentaje_error": "Porcentaje con error (%)"},
        range_y=[0, 100],
        text="porcentaje_error"
    )

def config_descarga_png(nombre_archivo):
    """Configuración estándar para que los gráficos de Plotly tengan el
    botón nativo de descarga como PNG (sin depender de Chrome/kaleido en
    el servidor, ya que la conversión la hace el navegador del usuario)."""

    return {
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": nombre_archivo,
            "scale": 2
        }
    }
