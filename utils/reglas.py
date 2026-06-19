import pandas as pd


def ejecutar_regla(df, columna, tipo, valor=None):

    if tipo == "Vacíos":

        errores = df[df[columna].isna()]

    elif tipo == "Duplicados":

        errores = df[df[columna].duplicated()]

    elif tipo == "Longitud Mayor":

        errores = df[
            df[columna]
            .astype(str)
            .str.len()
            > valor
        ]

    elif tipo == "Longitud Menor":

        errores = df[
            df[columna]
            .astype(str)
            .str.len()
            < valor
        ]

    elif tipo == "Solo números":

        errores = df[
            ~df[columna]
            .astype(str)
            .str.isnumeric()
        ]

    elif tipo == "Solo letras":

        errores = df[
            ~df[columna]
            .astype(str)
            .str.isalpha()
        ]

    else:

        errores = pd.DataFrame()

    return errores