"""Uso: python main.py [archivo.csv]   (por defecto LOTE1.csv)"""
import sys
from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe

def ejecucion():
    archivo = input("ingrese el nombre del csv que desea analizar junto con su extensión(debe estar en la misma carpeta que el codigo main.py)\n" \
    "o ingrese la ubicación del archivo(puede arrastrar el csv dentro del shell para copiar su dirección)\n")
    archivo= archivo.replace("\"","")
    archivo= archivo.replace("\'","")
    if (archivo == None):
        archivo = "Lote1.csv"

    procesos = leer_procesos(archivo)
    if not procesos:
        print("No hay procesos para simular.")
    else:
        sim = Simulador(procesos, al_evento=mostrar_estado)
        sim.ejecutar()
        mostrar_informe(sim)