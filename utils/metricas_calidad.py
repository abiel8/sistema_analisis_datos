def contar_vacios(df, columna):

    return df[columna].isna().sum()


def contar_duplicados(df, columna):

    return df[columna].duplicated().sum()


def contar_unicos(df, columna):

    return df[columna].nunique()


def longitud_mayor(df, columna, n):

    return (
        df[columna]
        .astype(str)
        .str.len()
        .gt(n)
        .sum()
    )


def longitud_menor(df, columna, n):

    return (
        df[columna]
        .astype(str)
        .str.len()
        .lt(n)
        .sum()
    )


def contiene_numeros(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.contains(r"\d", regex=True)
        .sum()
    )


def contiene_letras(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.contains(r"[A-Za-z]", regex=True)
        .sum()
    )


def solo_numeros(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.isnumeric()
        .sum()
    )


def solo_letras(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.isalpha()
        .sum()
    )


def espacios_inicio_final(df, columna):

    return (
        df[columna]
        .astype(str)
        .apply(lambda x: x != x.strip())
        .sum()
    )


def caracteres_especiales(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.contains(r"[^A-Za-z0-9 ]", regex=True)
        .sum()
    )