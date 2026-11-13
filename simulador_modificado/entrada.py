"""Lectura del lote de procesos desde un archivo CSV."""
import csv
import textwrap
import unicodedata

from config import MAX_PROCESOS, TAM_USUARIO
from proceso import Proceso

# Nombres de columna aceptados para cada campo lógico. Se comparan
# normalizados: sin acentos, sin espacios, sin paréntesis y en minúscula.
ALIAS_COLUMNAS = {
    "id": ("id", "pid", "proceso", "tr", "trabajo", "numerodeproceso"),
    "arribo": ("arribo", "tarribo", "ta", "llegada", "tiempodearribo"),
    "tam": ("tam", "tamano", "tamanok", "tamanokb", "tamkb",
            "tamanodelproceso"),
    "irr": ("irrupcion", "tirrupcion", "ti", "tiempodeirrupcion"),
}

NOMBRES = {"arribo": "arribo", "tam": "tamaño", "irr": "irrupción"}


def _normalizar(texto):
    """'Tamaño (K)' -> 'tamanok'; 't_irrupción;' -> 'tirrupcion'."""
    texto = unicodedata.normalize("NFKD", texto.strip().lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return "".join(c for c in texto if c.isalnum())


def _mapa_columnas(encabezado):
    """Devuelve {campo: índice} leyendo los nombres del encabezado."""
    mapa = {}
    for i, celda in enumerate(encabezado):
        clave = _normalizar(celda)
        for campo, alias in ALIAS_COLUMNAS.items():
            if clave in alias and campo not in mapa:
                mapa[campo] = i
                break
    return mapa


def _aviso(texto):
    """Imprime un aviso sin pasarse del ancho de la consola."""
    for linea in textwrap.wrap(texto, width=60, subsequent_indent="       "):
        print(linea)


def _leer_numeros(linea, mapa):
    """Convierte arribo, tamaño e irrupción a enteros usando los índices del mapa.
    Devuelve (valores, motivos): si algo falla, motivos explica qué y por qué."""
    valores, motivos = [], []
    for campo in ("arribo", "tam", "irr"):
        i = mapa[campo]
        if i >= len(linea) or not linea[i].strip():
            motivos.append(f"falta el valor de {NOMBRES[campo]}")
            continue
        try:
            valores.append(int(linea[i]))
        except ValueError:
            motivos.append(f"{NOMBRES[campo]}='{linea[i].strip()}' no es un número entero")
    return valores, motivos


def _motivos_de_rango(arribo, tam, irr):
    """Valores que son números pero no tienen sentido para un proceso."""
    motivos = []
    if arribo < 0:
        motivos.append(f"el arribo es {arribo} y no puede ser negativo")
    if tam <= 0:
        motivos.append(f"el tamaño es {tam}K y debe ser mayor que 0")
    if irr <= 0:
        motivos.append(f"la irrupción es {irr} y debe ser mayor que 0 "
                       "(sin tiempo de CPU el proceso no podría terminar)")
    return motivos


def leer_procesos(archivo):
    """Lee los procesos de un CSV.

    El orden de las columnas se toma del encabezado, así que acepta tanto
    `id, arribo, tam, irrupcion` como `Proceso, TA, TI, Tamaño (K)`.
    Si el encabezado no se reconoce, usa el orden histórico:
    id, arribo, tamaño, irrupción.
    Las filas inválidas se descartan con un aviso que explica el motivo."""
    procesos = []
    linea_de_id = {}          # id -> línea donde apareció por primera vez

    with open(archivo, "r", encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)
        encabezado = next(lector, None)
        if encabezado is None:
            return procesos

        mapa = _mapa_columnas(encabezado)
        if len(mapa) < 4:      # encabezado desconocido: orden por posición
            mapa = {"id": 0, "arribo": 1, "tam": 2, "irr": 3}

        for n, linea in enumerate(lector, start=2):
            if not any(c.strip() for c in linea):
                continue

            if len(procesos) == MAX_PROCESOS:
                _aviso(f"Aviso: el lote tiene más de {MAX_PROCESOS} procesos; "
                       f"se ignoran las líneas {n} en adelante.")
                break

            if mapa["id"] >= len(linea):
                _aviso(f"Aviso (línea {n}): se descarta porque no tiene identificador.")
                continue
            id = linea[mapa["id"]].strip()
            if not id:
                _aviso(f"Aviso (línea {n}): se descarta porque no tiene identificador.")
                continue

            if id in linea_de_id:
                _aviso(f"Aviso (línea {n}): se descarta {id} porque ese ID ya apareció "
                       f"en la línea {linea_de_id[id]} y debe ser único.")
                continue

            valores, motivos = _leer_numeros(linea, mapa)
            if motivos:
                _aviso(f"Aviso (línea {n}): se descarta {id} porque "
                       + "; ".join(motivos) + ".")
                continue

            arr, tam, irr = valores
            motivos = _motivos_de_rango(arr, tam, irr)
            if motivos:
                _aviso(f"Aviso (línea {n}): se descarta {id} porque "
                       + "; ".join(motivos) + ".")
                continue

            if tam > TAM_USUARIO:
                _aviso(f"Aviso (línea {n}): se descarta {id} porque pide {tam}K y la "
                       f"memoria de usuario es de {TAM_USUARIO}K: nunca podría entrar.")
                continue

            linea_de_id[id] = n
            procesos.append(Proceso(id, arr, tam, irr))

    return procesos
