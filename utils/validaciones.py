import re
import unicodedata

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


def extraer_codigo_pais(texto):

    texto_normalizado = _normalizar_texto(texto)

    # Ordenar por longitud descendente para que las claves más largas
    # (ej. "republica dominicana") se detecten antes que coincidencias
    # parciales más cortas
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


# ═══════════════════════════════════════════════════════════════
# Validación de correos electrónicos
# ═══════════════════════════════════════════════════════════════

def validar_email(df, columna):

    patron = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    return (
        ~df[columna]
        .astype(str)
        .str.match(patron)
    ).sum()


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

def _diagnosticar_telefono_hn(valor):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto = str(valor).strip()

    # Quitar separadores comunes: espacios, guiones, paréntesis, puntos
    solo_digitos = re.sub(r"[\s\-\.\(\)]", "", texto)

    # Quitar el código de país +504 o 504 al inicio, si viene incluido
    if solo_digitos.startswith("+504"):
        solo_digitos = solo_digitos[4:]
    elif solo_digitos.startswith("504") and len(solo_digitos) > 8:
        solo_digitos = solo_digitos[3:]

    if not solo_digitos.isdigit():
        return "Contiene caracteres inválidos"

    if len(solo_digitos) < 8:
        return "Muy corto (menos de 8 dígitos)"

    if len(solo_digitos) > 8:
        return "Muy largo (más de 8 dígitos)"

    primer_digito = solo_digitos[0]

    if primer_digito not in ("2", "3", "7", "8", "9"):
        return "Prefijo no reconocido en Honduras"

    return "Válido"


def diagnosticar_columna_telefono(df, columna):

    return df[columna].apply(_diagnosticar_telefono_hn)


def resumen_validacion_telefono(df, columna):

    diagnostico = diagnosticar_columna_telefono(df, columna)

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
# Validación de teléfonos internacionales (phonenumbers)
# ═══════════════════════════════════════════════════════════════

def _diagnosticar_telefono_internacional(valor, region_default="HN"):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto = str(valor).strip()

    try:
        numero = phonenumbers.parse(texto, region_default)

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