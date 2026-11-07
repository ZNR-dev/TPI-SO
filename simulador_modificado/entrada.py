"""Lectura del lote de procesos desde CSV."""
import csv
from config import MAX_PROCESOS, TAM_USUARIO
from proceso import Proceso


def leer_procesos(archivo):
    """Columnas del CSV: id, arribo, tamaño, irrupción (con encabezado)."""
    procesos = []
    ids_vistos = set()
    try:
            with open(archivo, "r", encoding="utf-8-sig", newline="") as f:
                lector = csv.reader(f)
                if next(lector,None) is None:
                    return procesos
        
        
                for n, linea in enumerate(lector, start=2):
                    if not any(c.strip() for c in linea):
                        continue
                    if len(procesos) == MAX_PROCESOS:
                        print(f"Aviso: se ignoran procesos extra (máximo {MAX_PROCESOS}).")
                        break
        
                    try:
                        id = linea[0].strip()
                        arr, tam, irr = int(linea[1]), int(linea[2]), int(linea[3])
                    except (IndexError, ValueError):
                        print(f"Aviso: linea {n} invalida ({','.join(linea)}). Se descarta.")
                        continue
                    if not id:
                        print(f"Aviso: linea {n} sin id. Se descarta")
                        continue
                    if id in ids_vistos:
                        print(f"Aviso: id duplicado '{id}' en linea {n}. Se descarta")
                        continue
                    if arr < 0 or tam <= 0 or irr<= 0:
                        print(f"Aviso: {id} tiene valores invalidos "
                              f"(arribo={arr}, tam={tam}, irrupcion={irr}). Se descarta.")
        
                        continue
                
                    if tam > TAM_USUARIO:
                        print(f"Aviso: {id} pide {tam}K y nunca entra en {TAM_USUARIO}K. Se descarta.")
                        continue
                    ids_vistos.add(id)
                    procesos.append(Proceso(id, arr, tam, irr))
            return procesos
    except:
        print("Error, el archivo que se intenta buscar no existe en esta carpeta.")

