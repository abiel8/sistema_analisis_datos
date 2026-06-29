import re

import pandas as pd


_PATRON_EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


def validar_email(df, columna):
    """Cuenta cuántos valores NO cumplen el formato de email (versión simple,
    sin diagnóstico detallado)."""

    return (
        ~df[columna]
        .astype(str)
        .str.match(_PATRON_EMAIL)
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

    if not _PATRON_EMAIL.match(correo):
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


def mascara_email_invalido(df, columna):
    """Máscara booleana: True donde el email NO es válido. Para uso en
    el catálogo de TIPOS_VALIDACION del dashboard."""

    return diagnosticar_columna_email(df, columna) != "Válido"