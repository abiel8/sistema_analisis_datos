import re
import unicodedata


PAISES = {
    "alemania": "DE",
    "canada": "CA",
    "china": "CN",
    "chile": "CL",
    "colombia": "CO",
    "corea del sur": "KR",
    "costa rica": "CR",
    "dinamarca": "DK",
    "ecuador": "EC",
    "el salvador": "SV",
    "espana": "ES",
    "estados unidos": "US",
    "usa": "US",
    "u.s.a.": "US",
    "u. s. a.": "US",
    "united states": "US",
    "francia": "FR",
    "guatemala": "GT",
    "honduras": "HN",
    "islas virgenes britanicas": "VG",
    "british virgin islands": "VG",
    "mexico": "MX",
    "noruega": "NO",
    "paises bajos": "NL",
    "netherlands": "NL",
    "panama": "PA",
    "peru": "PE",
    "puerto rico": "PR",
    "reino unido": "GB",
    "uk": "GB",
    "united kingdom": "GB",
    "gran bretana": "GB",
    "romania": "RO",
    "suecia": "SE",
    "suiza": "CH",
    "switzerland": "CH",
    "uruguay": "UY",
    "germany": "DE",
    "france": "FR",
    "norway": "NO",
    "sweden": "SE",
    "denmark": "DK",
    "republic of korea": "KR",
    "tegucigalpa": "HN",
    "san pedro sula": "HN",
    "sps": "HN",
}



def _normalizar_texto(texto):

    texto = str(texto).lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto


def extraer_codigo_pais(texto):

    texto_normalizado = _normalizar_texto(texto)

    # Ordenar por longitud descendente para que "republica dominicana"
    # se detecte antes que coincidencias parciales más cortas
    paises_ordenados = sorted(
        PAISES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for nombre_pais, codigo in paises_ordenados:
        if nombre_pais in texto_normalizado:
            return codigo

    return None


def columna_a_codigo_pais(df, columna):

    return df[columna].apply(extraer_codigo_pais)


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


def validar_email(df, columna):

    patron = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    return (
        ~df[columna]
        .astype(str)
        .str.match(patron)
    ).sum()