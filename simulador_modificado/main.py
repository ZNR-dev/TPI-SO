"""Punto de entrada del simulador: elige el lote CSV por nombre o con ventana"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe, set_sin_pausa

# Tecla que, en el pedido de nombre, vuelve al menú de selección de archivo.
TECLA_VOLVER = "0"

def seleccionar_lote():
    """Abre el explorador de archivos y devuelve la ruta (o '' si se cancela)."""
    ventana = tk.Tk()
    ventana.withdraw()
    ventana.attributes("-topmost", True) #Evita que el dialogo quede detras de la consola

    archivo = filedialog.askopenfilename(
        parent = ventana,
        title = "Seleccionar archivo LOTE",
        filetypes = [("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
    )
    ventana.destroy()
    return archivo

def pedir_nombre_archivo():
    """Pide el nombre o la ruta por consola y lo valida.

    Repite el pedido mientras el archivo no exista, mostrando el error.
    Devuelve la ruta elegida, o None si el usuario escribe 0 para volver.
    """
    while True:
        texto = input(
            "Ingrese el nombre del csv con su extension "
            "(debe estar en la misma carpeta que main.py)\n"
            "o su ubicacion completa (puede arrastrar el archivo a la consola)\n"
            f"(escriba {TECLA_VOLVER} para volver al menu de seleccion): "
        )
        archivo = texto.strip().strip("\"'")

        if archivo == TECLA_VOLVER:
            return None
        if not archivo:
            print("No escribio ningun nombre. Intente de nuevo.\n")
            continue
        if not os.path.isfile(archivo):
            print(f"No se encontro el archivo: {archivo}")
            print("Verifique el nombre y la extension (.csv) e intente de nuevo.\n")
            continue
        return archivo

def menu_archivo():
    """Segundo menu. Devuelva la ruta elegida, o None si el usuario vuelve atrás."""
    while True:
        print("\n-------Modo de seleccion de Archivo-------")
        print("1. Escribir el nombre del archivo")
        print("2. Seleccionar desde una carpeta (abre una ventana)")
        print("3. Volver")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            archivo = pedir_nombre_archivo()
            if archivo:
                return archivo
            print("Volviendo al menu de seleccion de archivo.")
        elif opcion == "2":
                archivo = seleccionar_lote()
                if archivo:
                    return archivo
                print("Seleccion Cancelada.")
        elif opcion == "3":
            return None
    
        else:
            print("Opcion no existe, intente de nuevo.")

def ejecucion():
    """Pide un archivo y lo ejecuta. Si el lote no sirve, vuelve a pedirlo."""
    while True:
        archivo = menu_archivo()
        if not archivo:
            return
        print(f"\n Archivo Seleccionado: {archivo}")

        try:
            procesos = leer_procesos(archivo)
        except (OSError, UnicodeError, ValueError, IndexError) as error:
            print(f"\n No se puede leer el archivo: {error}")
            print("Vuelva a intentarlo con otro archivo.")
            continue

        if not procesos:
            print("\n El archivo no contiene procesos validos.")
            print("Vuelva a intentarlo con otro archivo.")
            continue

        break

    set_sin_pausa(False)
    sim = Simulador(procesos, al_evento=mostrar_estado)
    sim.ejecutar()
    mostrar_informe(sim)
