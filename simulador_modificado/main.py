"""Punto de entrada del simulador: elige el lote CSV por nombre o con ventana"""
import tkinter as tk
from tkinter import filedialog, messagebox

from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe

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
    """Pide el nombre o la ruta por consola. limpia espacios y comillas"""
    texto = input(
            "Ingrese el nombre del csv con su extension "
            "(debe estar en la misma carpeta que main.py)\n"
            "o su ubicacion completa (puede arrastrar el archivo a la consola): "
    )
    return texto.strip().strip("\"'")

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
            print("No escribio ningun nombre.")
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
    archivo = menu_archivo()
    if not archivo:
        return

    try:
        procesos = leer_procesos(archivo)
    except (OSError, UnicodeError, ValueError, IndexError) as error:
        print(f"\n No se puede leer el archivo:{error}")
        return
    if not procesos:
        print("El archivo no contiene procesos validos. No se ejecuto la Simulacion.")
        return

    print(f"\n Archivo Seleccionado: {archivo}")
    sim = Simulador(procesos, al_evento=mostrar_estado)
    sim.ejecutar()
    mostrar_informe(sim)