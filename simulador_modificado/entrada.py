"""Lectura del lote de procesos desde un archivo CSV."""
import csv
 
from config import MAX_PROCESOS, TAM_USUARIO
from proceso import Proceso
 
# Nombres de las columnas numéricas, en el orden en que vienen en el CSV
COLUMNAS = ("arribo", "tamaño", "irrupción")
 
 
def _leer_numeros(linea):
    """Convierte arribo, tamaño e irrupción a enteros.
    Devuelve (valores, motivos): si algo falla, motivos explica qué y por qué."""
    valores, motivos = [], []
    for i, nombre in enumerate(COLUMNAS, start=1):
        if i >= len(linea) or not linea[i].strip():
            motivos.append(f"falta el valor de {nombre}")
            continue
        try:
            valores.append(int(linea[i]))
        except ValueError:
            motivos.append(f"{nombre}='{linea[i].strip()}' no es un número entero")
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
    """Columnas del CSV: id, arribo, tamaño, irrupción (con encabezado).
    Las filas inválidas se descartan con un aviso que explica el motivo."""
    procesos = []
    linea_de_id = {}          # id -> línea donde apareció por primera vez
 
    with open(archivo, "r", encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)
        if next(lector, None) is None:
            return procesos
 
        for n, linea in enumerate(lector, start=2):
            if not any(c.strip() for c in linea):
                continue
 
            if len(procesos) == MAX_PROCESOS:
                print(f"Aviso: el lote tiene más de {MAX_PROCESOS} procesos; "
                      f"se ignoran las líneas {n} en adelante.")
                break
 
            id = linea[0].strip()
            if not id:
                print(f"Aviso (línea {n}): se descarta porque no tiene identificador.")
                continue
 
            if id in linea_de_id:
                print(f"Aviso (línea {n}): se descarta {id} porque ese ID ya apareció "
                      f"en la línea {linea_de_id[id]} y debe ser único.")
                continue
 
            valores, motivos = _leer_numeros(linea)
            if motivos:
                print(f"Aviso (línea {n}): se descarta {id} porque "
                      + "; ".join(motivos) + ".")
                continue
 
            arr, tam, irr = valores
            motivos = _motivos_de_rango(arr, tam, irr)
            if motivos:
                print(f"Aviso (línea {n}): se descarta {id} porque "
                      + "; ".join(motivos) + ".")
                continue
 
            if tam > TAM_USUARIO:
                print(f"Aviso (línea {n}): se descarta {id} porque pide {tam}K y la "
                      f"memoria de usuario es de {TAM_USUARIO}K: nunca podría entrar.")
                continue
 
            linea_de_id[id] = n
            procesos.append(Proceso(id, arr, tam, irr))
 
    return procesos
