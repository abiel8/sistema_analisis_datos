import pandas as pd
import plotly.express as px


def grafico_barras(df, x, y):

    return px.bar(
        df,
        x=x,
        y=y,
        title=f"{y} por {x}"
    )


def grafico_lineas(df, x, y):

    return px.line(
        df,
        x=x,
        y=y,
        title=f"{y} por {x}"
    )


def grafico_pastel(df, nombres, valores):

    return px.pie(
        df,
        names=nombres,
        values=valores
    )


def grafico_dispersion(df, x, y):

    return px.scatter(
        df,
        x=x,
        y=y
    )


# ── Cálculo de condiciones de calidad ───────────────────────────

def _porcentaje_vacios(serie):

    vacios = serie.isna() | (serie.astype(str).str.strip() == "")
    return round(vacios.sum() / len(serie) * 100, 2) if len(serie) else 0


def _porcentaje_duplicados(serie):

    duplicados = serie.duplicated(keep=False)
    return round(duplicados.sum() / len(serie) * 100, 2) if len(serie) else 0


def _porcentaje_longitud_menor(serie, n):

    cortos = serie.astype(str).str.len() < n
    return round(cortos.sum() / len(serie) * 100, 2) if len(serie) else 0


CONDICIONES_CALIDAD = {
    "Vacíos (%)": _porcentaje_vacios,
    "Duplicados (%)": _porcentaje_duplicados,
}


def calcular_calidad_columna(df, columna, n_caracteres):

    return {
        "Vacíos (%)": _porcentaje_vacios(df[columna]),
        "Duplicados (%)": _porcentaje_duplicados(df[columna]),
        f"Longitud < {n_caracteres} (%)": _porcentaje_longitud_menor(df[columna], n_caracteres),
    }


def calcular_calidad_archivo(df, n_caracteres):

    filas = []

    for columna in df.columns:

        fila = {
            "columna": columna,
            "Vacíos (%)": _porcentaje_vacios(df[columna]),
            "Duplicados (%)": _porcentaje_duplicados(df[columna]),
            f"Longitud < {n_caracteres} (%)": _porcentaje_longitud_menor(df[columna], n_caracteres),
        }

        filas.append(fila)

    return pd.DataFrame(filas)


def grafico_calidad_columna(resultados, titulo):

    df_resultado = pd.DataFrame(
        list(resultados.items()),
        columns=["condicion", "porcentaje"]
    )

    return px.bar(
        df_resultado,
        x="condicion",
        y="porcentaje",
        title=titulo,
        labels={"condicion": "Condición", "porcentaje": "Porcentaje (%)"},
        range_y=[0, 100]
    )


def grafico_calidad_archivo(df_calidad, condicion, titulo):

    return px.bar(
        df_calidad,
        x="columna",
        y=condicion,
        title=titulo,
        labels={"columna": "Columna", condicion: "Porcentaje (%)"},
        range_y=[0, 100]
    )