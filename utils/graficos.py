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