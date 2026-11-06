"""Punto de entrada del simulador.

El lote CSV se elige así, en este orden:
  1) python main.py LOTE2.csv      -> usa el archivo indicado
  2) python main.py                -> abre el explorador de archivos (Tkinter)
  3) si Tkinter no está disponible -> lo pide por teclado
La simulación solo comienza después de elegir un archivo.
"""
import os
import sys

from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe

ARCHIVO_POR_DEFECTO = "LOTE1.csv"


def elegir_con_ventana():
    """Abre el explorador de archivos.
    Devuelve la ruta, "" si el usuario cancela, o None si no se pudo abrir la ventana."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        ventana = tk.Tk()
    except Exception:                  # sin tkinter o sin entorno gráfico
        return None

    ventana.withdraw()
    ventana.attributes("-topmost", True)   # evita que el diálogo quede detrás de la consola
    ventana.update()
    ventana.lift()
    ventana.focus_force()

    print("Abriendo el selector de archivos... (si no lo ves, buscalo detrás de esta ventana)")
    archivo = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar archivo LOTE",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
    )
    ventana.destroy()
    return archivo


def elegir_por_teclado():
    nombre = input(f"Archivo de procesos [{ARCHIVO_POR_DEFECTO}]: ").strip()
    return nombre or ARCHIVO_POR_DEFECTO


def elegir_archivo():
    if len(sys.argv) > 1:
        return sys.argv[1]
    archivo = elegir_con_ventana()
    if archivo is None:
        print("No se pudo abrir la ventana de selección (Tkinter no disponible).")
        archivo = elegir_por_teclado()
    return archivo


def main():
    print(f"[main] ejecutando: {os.path.abspath(__file__)}")
    archivo = elegir_archivo()

    if not archivo:
        print("Selección cancelada. No se ejecutó la simulación.")
        return

    try:
        procesos = leer_procesos(archivo)
    except FileNotFoundError:
        print(f"No se encontró el archivo '{archivo}'.")
        return
    except (OSError, UnicodeError, ValueError, IndexError) as error:
        print(f"No se pudo leer el archivo seleccionado.\nDetalle: {error}")
        return

    if not procesos:
        print("El archivo no contiene procesos válidos. No se ejecutó la simulación.")
        return

    print(f"Archivo seleccionado: {archivo}")
    sim = Simulador(procesos, al_evento=mostrar_estado)
    sim.ejecutar()
    mostrar_informe(sim)


if __name__ == "__main__":
    main()