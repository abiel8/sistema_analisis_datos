import plotly.express as px


def grafico_pastel(df, nombres, valores):

    return px.pie(
        df,
        names=nombres,
        values=valores
    )
