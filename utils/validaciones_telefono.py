import re

import pandas as pd
import phonenumbers


# ═══════════════════════════════════════════════════════════════
# Validación estricta de teléfonos de Honduras (8 dígitos)
# ═══════════════════════════════════════════════════════════════

def _diagnosticar_telefono_hn(valor):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto = str(valor).strip()

    solo_digitos = re.sub(r"[\s\-\.\(\)]", "", texto)

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
# Validación internacional con phonenumbers.
# Detecta automáticamente si es nacional (8 dígitos) o ya trae
# código de país pegado (más de 8 dígitos). Exige formato "limpio":
# solo dígitos, espacios, guiones y paréntesis, sin terminar en un
# separador suelto.
# ═══════════════════════════════════════════════════════════════

_PATRON_FORMATO_PERMITIDO = re.compile(r"^\+?[\d\s\-\(\)]+$")
_PATRON_TERMINA_EN_SEPARADOR = re.compile(r"[\s\-\(\)]$")


def _diagnosticar_telefono_internacional(valor, region_default="HN"):

    if pd.isna(valor) or str(valor).strip() == "":
        return "Vacío"

    texto_original = str(valor).strip()

    if not _PATRON_FORMATO_PERMITIDO.match(texto_original):
        return "Formato no permitido (use solo espacios, guiones o paréntesis)"

    if _PATRON_TERMINA_EN_SEPARADOR.search(texto_original):
        return "Formato inválido (termina en separador sin dígito)"

    solo_digitos = re.sub(r"[\s\-\(\)]", "", texto_original)

    if not solo_digitos.replace("+", "").isdigit():
        return "Contiene caracteres inválidos"

    if texto_original.startswith("+"):
        texto_a_parsear = texto_original
    elif len(solo_digitos) > 8:
        texto_a_parsear = "+" + solo_digitos
    else:
        # Número de 8 dígitos sin código de país: usar validación local HN
        # en vez de phonenumbers, porque su base de datos tiene los rangos
        # de números fijos de Honduras (prefijo 2x) desactualizados
        return _diagnosticar_telefono_hn(valor)

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

    # phonenumbers tiene los rangos de números fijos de Honduras (prefijo 2x)
    # desactualizados — si el número parseado es de Honduras y tiene 8 dígitos
    # con prefijo 2, lo validamos con nuestra lógica local en vez de rechazarlo
    numero_nacional = str(numero.national_number)
    es_numero_hn = phonenumbers.region_code_for_number(numero) == "HN"

    if es_numero_hn and len(numero_nacional) == 8 and numero_nacional[0] == "2":
        return _diagnosticar_telefono_hn(numero_nacional)

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


def mascara_telefono_invalido(df, columna):
    """Máscara booleana: True donde el teléfono NO es válido (nacional o
    internacional, detección automática). Para TIPOS_VALIDACION."""

    return diagnosticar_columna_telefono_internacional(df, columna, "HN") != "Válido"