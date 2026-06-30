import re

import pandas as pd
import plotly.express as px


# ═══════════════════════════════════════════════════════════════
# Gráficos básicos
# ═══════════════════════════════════════════════════════════════

def grafico_barras(df, x, y):

    return px.bar(df, x=x, y=y, title=f"{y} por {x}")


def grafico_lineas(df, x, y):

    return px.line(df, x=x, y=y, title=f"{y} por {x}")


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


def grafico_dispersion(df, x, y):

    return px.scatter(df, x=x, y=y)


# ═══════════════════════════════════════════════════════════════
# Calidad de datos: comparación entre columnas
# ═══════════════════════════════════════════════════════════════

def _porcentaje_vacios(serie):

    vacios = serie.isna() | (serie.astype(str).str.strip() == "")
    return round(vacios.sum() / len(serie) * 100, 2) if len(serie) else 0


def _porcentaje_duplicados(serie):

    duplicados = serie.duplicated(keep=False)
    return round(duplicados.sum() / len(serie) * 100, 2) if len(serie) else 0


def _porcentaje_longitud_menor(serie, n):

    cortos = serie.astype(str).str.len() < n
    return round(cortos.sum() / len(serie) * 100, 2) if len(serie) else 0


def calcular_calidad_columna(df, columna, n_caracteres):

    return {
        "Vacíos (%)": _porcentaje_vacios(df[columna]),
        "Duplicados (%)": _porcentaje_duplicados(df[columna]),
        f"Longitud < {n_caracteres} (%)": _porcentaje_longitud_menor(df[columna], n_caracteres),
    }


def calcular_calidad_archivo(df, n_caracteres):

    filas = []

    for columna in df.columns:
        filas.append({
            "columna": columna,
            "Vacíos (%)": _porcentaje_vacios(df[columna]),
            "Duplicados (%)": _porcentaje_duplicados(df[columna]),
            f"Longitud < {n_caracteres} (%)": _porcentaje_longitud_menor(df[columna], n_caracteres),
        })

    return pd.DataFrame(filas)


def grafico_calidad_columna(resultados, titulo):

    df_resultado = pd.DataFrame(list(resultados.items()), columns=["condicion", "porcentaje"])

    return px.bar(
        df_resultado, x="condicion", y="porcentaje", title=titulo,
        labels={"condicion": "Condición", "porcentaje": "Porcentaje (%)"},
        range_y=[0, 100]
    )


def grafico_calidad_archivo(df_calidad, condicion, titulo):

    return px.bar(
        df_calidad, x="columna", y=condicion, title=titulo,
        labels={"columna": "Columna", condicion: "Porcentaje (%)"},
        range_y=[0, 100]
    )


# ═══════════════════════════════════════════════════════════════
# Distribución por categorías dentro de una columna
# ═══════════════════════════════════════════════════════════════

def _clasificar_valor(valor):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto = str(valor).strip()

    tiene_numero = bool(re.search(r"\d", texto))
    tiene_letra = bool(re.search(r"[A-Za-z]", texto))
    tiene_especial = bool(re.search(r"[^A-Za-z0-9\s]", texto))

    if tiene_especial:
        return "Caracteres especiales"

    if tiene_numero and tiene_letra:
        return "Alfanumérico (letras y números)"

    if tiene_numero:
        return "Solo números"

    if tiene_letra:
        return "Solo letras"

    return "Otro"


def clasificar_columna(df, columna):

    return df[columna].apply(_clasificar_valor)


def calcular_distribucion_columna(df, columna):

    clasificacion = clasificar_columna(df, columna)

    conteo = clasificacion.value_counts().reset_index()
    conteo.columns = ["categoria", "cantidad"]
    conteo["porcentaje"] = round(conteo["cantidad"] / len(df) * 100, 2)

    return conteo


def grafico_distribucion_columna(df_distribucion, titulo, tipo="Pastel"):

    if tipo == "Pastel":
        return px.pie(
            df_distribucion, names="categoria", values="cantidad",
            title=titulo, hover_data=["porcentaje"]
        )

    return px.bar(
        df_distribucion, x="categoria", y="cantidad", title=titulo,
        text="porcentaje", labels={"categoria": "Categoría", "cantidad": "Cantidad"}
    )


# ═══════════════════════════════════════════════════════════════
# Resumen general: comparación de % de error entre columnas
# ═══════════════════════════════════════════════════════════════

def grafico_resumen_general(resumen_porcentajes):
    """resumen_porcentajes: lista de dicts [{'columna': ..., 'porcentaje_error': ...}, ...]"""

    df_resumen = pd.DataFrame(resumen_porcentajes)

    return px.bar(
        df_resumen,
        x="columna",
        y="porcentaje_error",
        title="Porcentaje de error por columna analizada",
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