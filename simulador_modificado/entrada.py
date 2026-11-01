"""Lectura del lote de procesos desde CSV."""
import csv
from config import MAX_PROCESOS, TAM_USUARIO
from proceso import Proceso


def leer_procesos(archivo):
    """Columnas del CSV: id, arribo, tamaño, irrupción (con encabezado)."""
    procesos = []
    with open(archivo, "r") as f:
        lector = csv.reader(f)
        next(lector)
        for linea in lector:
            if not linea:
                continue
            if len(procesos) == MAX_PROCESOS:
                print(f"Aviso: se ignoran procesos extra (máximo {MAX_PROCESOS}).")
                break
            id, arr, tam, irr = linea[0].strip(), int(linea[1]), int(linea[2]), int(linea[3])
            if tam > TAM_USUARIO:
                print(f"Aviso: {id} pide {tam}K y nunca entra en {TAM_USUARIO}K. Se descarta.")
                continue
            procesos.append(Proceso(id, arr, tam, irr))
    return procesos
