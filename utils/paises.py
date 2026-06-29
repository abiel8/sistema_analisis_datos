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
    "francisco morazan": "HN",
    "san pedro sula": "HN",
    "sps": "HN",
    "danli": "HN",
    "comayaguela": "HN",
    "comayagua": "HN",
    "olancho": "HN",
    "zamorano": "HN",
    "ceiba": "HN",
    "boston": "US",
    "chicago": "US",
    "new york": "US",
    "washington": "US",
}

# Ordenado una sola vez al importar el módulo, no en cada llamada
_PAISES_ORDENADOS = sorted(
    PAISES.items(),
    key=lambda item: len(item[0]),
    reverse=True
)


def _normalizar_texto(texto):

    texto = str(texto).lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto


def extraer_codigo_pais(texto):

    texto_normalizado = _normalizar_texto(texto)

    for nombre_pais, codigo in _PAISES_ORDENADOS:
        if nombre_pais in texto_normalizado:
            return codigo

    return None


def columna_a_codigo_pais(df, columna):

    return df[columna].apply(extraer_codigo_pais)