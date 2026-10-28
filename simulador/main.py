"""Uso: python main.py [archivo.csv]   (por defecto LOTE1.csv)"""
import sys
from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "LOTE1.csv"
    procesos = leer_procesos(archivo)
    if not procesos:
        print("No hay procesos para simular.")
    else:
        sim = Simulador(procesos, al_evento=mostrar_estado)
        sim.ejecutar()
        mostrar_informe(sim)
