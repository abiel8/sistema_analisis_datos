import json
import os
import re
from datetime import datetime


CARPETA_PLANTILLAS = "plantillas"


def _ruta_plantilla(nombre):
    """Convierte el nombre de la plantilla a una ruta de archivo segura."""

    nombre_limpio = re.sub(r"[^a-zA-Z0-9_\-]", "_", nombre.strip())
    return os.path.join(CARPETA_PLANTILLAS, f"{nombre_limpio}.json")


def _asegurar_carpeta():
    """Crea la carpeta de plantillas si no existe."""

    os.makedirs(CARPETA_PLANTILLAS, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# Dashboard: guarda {columna: [lista de condiciones]}
# ═══════════════════════════════════════════════════════════════

def guardar_plantilla_dashboard(nombre, asignaciones):
    """Guarda la configuración del Dashboard como plantilla JSON.

    asignaciones: dict {nombre_columna: [lista_de_tipos_elegidos]}
    """

    _asegurar_carpeta()

    plantilla = {
        "tipo": "dashboard",
        "nombre": nombre.strip(),
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "asignaciones": asignaciones
    }

    with open(_ruta_plantilla(nombre), "w", encoding="utf-8") as f:
        json.dump(plantilla, f, ensure_ascii=False, indent=2)


def cargar_plantilla_dashboard(nombre):
    """Carga una plantilla de Dashboard y devuelve sus asignaciones,
    o None si no existe o es de otro tipo."""

    ruta = _ruta_plantilla(nombre)

    if not os.path.exists(ruta):
        return None

    with open(ruta, encoding="utf-8") as f:
        plantilla = json.load(f)

    if plantilla.get("tipo") != "dashboard":
        return None

    return plantilla.get("asignaciones", {})


# ═══════════════════════════════════════════════════════════════
# Calidad de Datos: guarda {columna, validacion_email, validacion_telefono}
# ═══════════════════════════════════════════════════════════════

def guardar_plantilla_calidad(nombre, columna, validar_email, validar_telefono):
    """Guarda la configuración de Calidad de Datos como plantilla JSON."""

    _asegurar_carpeta()

    plantilla = {
        "tipo": "calidad",
        "nombre": nombre.strip(),
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "columna": columna,
        "validar_email": validar_email,
        "validar_telefono": validar_telefono
    }

    with open(_ruta_plantilla(nombre), "w", encoding="utf-8") as f:
        json.dump(plantilla, f, ensure_ascii=False, indent=2)


def cargar_plantilla_calidad(nombre):
    """Carga una plantilla de Calidad de Datos, o None si no existe."""

    ruta = _ruta_plantilla(nombre)

    if not os.path.exists(ruta):
        return None

    with open(ruta, encoding="utf-8") as f:
        plantilla = json.load(f)

    if plantilla.get("tipo") != "calidad":
        return None

    return {
        "columna": plantilla.get("columna"),
        "validar_email": plantilla.get("validar_email", False),
        "validar_telefono": plantilla.get("validar_telefono", False)
    }


# ═══════════════════════════════════════════════════════════════
# Operaciones comunes
# ═══════════════════════════════════════════════════════════════

def listar_plantillas(tipo=None):
    """Devuelve una lista de dicts con info de todas las plantillas guardadas.
    Si tipo='dashboard' o tipo='calidad', filtra por ese tipo.

    Cada dict tiene: nombre, tipo, fecha.
    """

    _asegurar_carpeta()

    plantillas = []

    for archivo in sorted(os.listdir(CARPETA_PLANTILLAS)):

        if not archivo.endswith(".json"):
            continue

        ruta = os.path.join(CARPETA_PLANTILLAS, archivo)

        try:
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)

            if tipo and datos.get("tipo") != tipo:
                continue

            plantillas.append({
                "nombre": datos.get("nombre", archivo.replace(".json", "")),
                "tipo": datos.get("tipo", "desconocido"),
                "fecha": datos.get("fecha", "—")
            })

        except Exception:
            continue  # Si un archivo está corrupto, se omite sin romper

    return plantillas


def eliminar_plantilla(nombre):
    """Elimina la plantilla con ese nombre. Devuelve True si se eliminó,
    False si no existía."""

    ruta = _ruta_plantilla(nombre)

    if os.path.exists(ruta):
        os.remove(ruta)
        return True

    return False


def nombre_plantilla_existe(nombre):
    """Verifica si ya existe una plantilla con ese nombre."""

    return os.path.exists(_ruta_plantilla(nombre))