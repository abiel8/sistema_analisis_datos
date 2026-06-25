import re
import unicodedata
import string

import pandas as pd
import phonenumbers


# ═══════════════════════════════════════════════════════════════
# Extracción de país desde texto
# ═══════════════════════════════════════════════════════════════

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


def _normalizar_texto(texto):

    texto = str(texto).lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto

def limpiar_texto_columna(serie):

    def _limpiar_valor(valor):

        if pd.isna(valor):
            return valor

        texto = str(valor).strip()

        # Quitar tildes y diacríticos (á→a, é→e, etc.), pero preservar la ñ
        # temporalmente para convertirla explícitamente después
        texto = texto.replace("ñ", "{{enie}}").replace("Ñ", "{{ENIE}}")

        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(c for c in texto if not unicodedata.combining(c))

        texto = texto.replace("{{enie}}", "n").replace("{{ENIE}}", "N")

        # Quitar todos los signos de puntuación
        texto = texto.translate(str.maketrans("", "", string.punctuation))

        # Quitar espacios extremos y colapsar espacios múltiples internos
        texto = " ".join(texto.split())

        return texto

    return serie.apply(_limpiar_valor)


def extraer_codigo_pais(texto):

    texto_normalizado = _normalizar_texto(texto)

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


# ═══════════════════════════════════════════════════════════════
# Métricas generales de calidad de datos
# ═══════════════════════════════════════════════════════════════

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


def caracteres_especiales(df, columna):

    return (
        df[columna]
        .astype(str)
        .str.contains(r"[^A-Za-z0-9 ]", regex=True)
        .sum()
    )


# ═══════════════════════════════════════════════════════════════
# Validación de correos electrónicos
# ═══════════════════════════════════════════════════════════════

def _diagnosticar_email(valor):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    correo = str(valor).strip()

    if correo != str(valor):
        return "Espacios extra"

    if "@" not in correo:
        return "Falta @"

    if correo.count("@") > 1:
        return "Más de un @"

    usuario, _, dominio = correo.partition("@")

    if not usuario:
        return "Falta usuario antes del @"

    if not dominio:
        return "Falta dominio después del @"

    if "." not in dominio:
        return "Dominio sin extensión (falta .com, .net, etc.)"

    extension = dominio.rsplit(".", 1)[-1]

    if len(extension) < 2 or not extension.isalpha():
        return "Extensión de dominio inválida"

    patron = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

    if not patron.match(correo):
        return "Caracteres inválidos"

    return "Válido"


def diagnosticar_columna_email(df, columna):

    return df[columna].apply(_diagnosticar_email)


def resumen_validacion_email(df, columna):

    diagnostico = diagnosticar_columna_email(df, columna)

    total = len(diagnostico)
    validos = (diagnostico == "Válido").sum()
    invalidos = total - validos

    return {
        "total": total,
        "validos": validos,
        "invalidos": invalidos,
        "porcentaje_validos": round(validos / total * 100, 2) if total else 0,
        "detalle": diagnostico
    }


# ═══════════════════════════════════════════════════════════════
# Validación de teléfonos (Honduras, 8 dígitos)
# ═══════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════
# Evaluación de condiciones por fila (para Dashboard)
# ═══════════════════════════════════════════════════════════════

def mascara_vacios(df, columna):

    return df[columna].isna() | (df[columna].astype(str).str.strip() == "")


def mascara_duplicados(df, columna):

    return df[columna].duplicated(keep=False)


def mascara_contiene_texto(df, columna, texto_buscado):

    return df[columna].astype(str).str.contains(texto_buscado, case=False, na=False, regex=False)


def mascara_no_contiene_texto(df, columna, texto_buscado):

    return ~mascara_contiene_texto(df, columna, texto_buscado)


def mascara_longitud_mayor(df, columna, n):

    return df[columna].astype(str).str.len() > n


def mascara_longitud_menor(df, columna, n):

    return df[columna].astype(str).str.len() < n


def mascara_contiene_numeros(df, columna):

    return df[columna].astype(str).str.contains(r"\d", regex=True, na=False)


def mascara_contiene_letras(df, columna):

    return df[columna].astype(str).str.contains(r"[A-Za-z]", regex=True, na=False)


def mascara_solo_numeros(df, columna):

    return df[columna].astype(str).str.isnumeric()


def mascara_solo_letras(df, columna):

    return df[columna].astype(str).str.isalpha()


def mascara_caracteres_especiales(df, columna):

    return df[columna].astype(str).str.contains(r"[^A-Za-z0-9 ]", regex=True, na=False)


CONDICIONES_DASHBOARD = {
    "Vacíos": {
        "funcion": mascara_vacios,
        "necesita_parametro": None
    },
    "Duplicados": {
        "funcion": mascara_duplicados,
        "necesita_parametro": None
    },
    "Contiene un valor específico": {
        "funcion": mascara_contiene_texto,
        "necesita_parametro": "texto"
    },
    "No contiene un valor específico": {
        "funcion": mascara_no_contiene_texto,
        "necesita_parametro": "texto"
    },
    "Longitud mayor a N": {
        "funcion": mascara_longitud_mayor,
        "necesita_parametro": "numero"
    },
    "Longitud menor a N": {
        "funcion": mascara_longitud_menor,
        "necesita_parametro": "numero"
    },
    "Contiene números": {
        "funcion": mascara_contiene_numeros,
        "necesita_parametro": None
    },
    "Contiene letras": {
        "funcion": mascara_contiene_letras,
        "necesita_parametro": None
    },
    "Solo números": {
        "funcion": mascara_solo_numeros,
        "necesita_parametro": None
    },
    "Solo letras": {
        "funcion": mascara_solo_letras,
        "necesita_parametro": None
    },
    "Caracteres especiales / símbolos": {
        "funcion": mascara_caracteres_especiales,
        "necesita_parametro": None
    },
}

# ═══════════════════════════════════════════════════════════════
# Validación de teléfonos internacionales (phonenumbers)
# Detecta automáticamente si es nacional (8 dígitos) o ya trae
# código de país pegado (más de 8 dígitos)
# ═══════════════════════════════════════════════════════════════

def _diagnosticar_telefono_internacional(valor, region_default="HN"):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto_original = str(valor).strip()

    solo_digitos = re.sub(r"[\s\-\.\(\)]", "", texto_original)

    if not solo_digitos.replace("+", "").isdigit():
        return "Contiene caracteres inválidos"

    if texto_original.strip().startswith("+"):
        texto_a_parsear = texto_original

    elif len(solo_digitos) > 8:
        texto_a_parsear = "+" + solo_digitos

    else:
        texto_a_parsear = texto_original

    try:
        numero = phonenumbers.parse(texto_a_parsear, region_default)

    except phonenumbers.NumberParseException as e:

        if e.error_type == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE:
            return "Código de país inválido"

        elif e.error_type == phonenumbers.NumberParseException.NOT_A_NUMBER:
            return "No es un número válido"

        elif e.error_type == phonenumbers.NumberParseException.TOO_SHORT_NSN:
            return "Muy corto"

        elif e.error_type == phonenumbers.NumberParseException.TOO_LONG:
            return "Muy largo"

        else:
            return "Formato no reconocido"

    if not phonenumbers.is_valid_number(numero):
        return "Número con formato inválido para su país"

    return "Válido"


def diagnosticar_columna_telefono_internacional(df, columna, region_default="HN"):

    return df[columna].apply(
        lambda valor: _diagnosticar_telefono_internacional(valor, region_default)
    )


def resumen_validacion_telefono_internacional(df, columna, region_default="HN"):

    diagnostico = diagnosticar_columna_telefono_internacional(df, columna, region_default)

    total = len(diagnostico)
    validos = (diagnostico == "Válido").sum()
    invalidos = total - validos

    return {
        "total": total,
        "validos": validos,
        "invalidos": invalidos,
        "porcentaje_validos": round(validos / total * 100, 2) if total else 0,
        "detalle": diagnostico
    }