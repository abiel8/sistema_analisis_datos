def perfil_columna(df, columna):

    return {

        "Columna": columna,

        "Tipo de dato":
        str(df[columna].dtype),

        "Registros":
        len(df),

        "Vacíos":
        df[columna].isna().sum(),

        "Valores únicos":
        df[columna].nunique(),

        "Duplicados":
        df[columna].duplicated().sum()
    }