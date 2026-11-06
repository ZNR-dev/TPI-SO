"""Lectura del lote de procesos desde un archivo CSV."""
import csv

from config import MAX_PROCESOS, TAM_USUARIO
from proceso import Proceso


def leer_procesos(archivo):
    """Lee las columnas id, arribo, tamaño e irrupción (con encabezado)."""
    procesos = []

    # utf-8-sig también permite leer CSV guardados desde Excel con BOM.
    with open(archivo, "r", encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)

        encabezado = next(lector, None)
        if encabezado is None:
            return procesos

        for numero_linea, linea in enumerate(lector, start=2):
            if not linea or all(not campo.strip() for campo in linea):
                continue

            if len(linea) < 4:
                raise ValueError(
                    f"La línea {numero_linea} no tiene las 4 columnas requeridas "
                    "(id, arribo, tamaño, irrupción)."
                )

            if len(procesos) == MAX_PROCESOS:
                print(
                    f"Aviso: se ignoran procesos extra "
                    f"(máximo {MAX_PROCESOS})."
                )
                break

            try:
                id_proceso = linea[0].strip()
                arribo = int(linea[1])
                tam = int(linea[2])
                irrupcion = int(linea[3])
            except ValueError as error:
                raise ValueError(
                    f"Datos inválidos en la línea {numero_linea}: {linea}"
                ) from error

            if not id_proceso:
                raise ValueError(
                    f"La línea {numero_linea} no contiene un identificador."
                )

            if tam > TAM_USUARIO:
                print(
                    f"Aviso: {id_proceso} pide {tam}K y nunca entra en "
                    f"{TAM_USUARIO}K. Se descarta."
                )
                continue

            procesos.append(Proceso(id_proceso, arribo, tam, irrupcion))

    return procesos
