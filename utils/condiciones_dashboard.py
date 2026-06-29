from utils.validaciones_email import mascara_email_invalido
from utils.validaciones_telefono import mascara_telefono_invalido


# ═══════════════════════════════════════════════════════════════
# Máscaras booleanas básicas, evaluadas fila por fila
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


def mascara_id_con_problema(df, columna):

    return mascara_vacios(df, columna) | mascara_duplicados(df, columna)


def mascara_texto_con_problema(df, columna):

    return mascara_vacios(df, columna) | mascara_caracteres_especiales(df, columna)


# ═══════════════════════════════════════════════════════════════
# Catálogo unificado: condiciones genéricas + tipos especializados
# (email, teléfono, ID, texto). Una sola fuente de verdad para
# el selector del Dashboard.
# ═══════════════════════════════════════════════════════════════

CONDICIONES_GENERICAS = {
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


TIPOS_VALIDACION = {
    "Sin validar": None,

    "Email": {
        "funcion": mascara_email_invalido,
        "necesita_parametro": None,
        "descripcion": "Marca correos con formato inválido"
    },
    "Teléfono": {
        "funcion": mascara_telefono_invalido,
        "necesita_parametro": None,
        "descripcion": "Marca teléfonos con formato inválido (HN o internacional)"
    },
    "ID (vacíos + duplicados)": {
        "funcion": mascara_id_con_problema,
        "necesita_parametro": None,
        "descripcion": "Marca vacíos o duplicados"
    },
    "Texto general (vacíos + símbolos)": {
        "funcion": mascara_texto_con_problema,
        "necesita_parametro": None,
        "descripcion": "Marca vacíos o caracteres especiales"
    },

    **CONDICIONES_GENERICAS
}