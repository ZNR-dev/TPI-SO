"""Punto de entrada del simulador: elige el lote CSV por nombre o con ventana."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe

# Tecla que, en el pedido de nombre, vuelve al menú de selección de archivo. En este caso vuelve presionando la tecla 0
TECLA_VOLVER = "0"

def seleccionar_lote():                                                             #Funcion que se encarga de seleccionar el archivo de una carpeta
    """Abre el explorador de archivos y devuelve la ruta (o '' si se cancela)."""
    ventana = tk.Tk()                                  #Crea la ventana principal de Tkinter
    ventana.withdraw()                                  #Oculta la ventana principal para que no se vea en pantalla
    ventana.attributes("-topmost", True) #Evita que el dialogo quede detras de la consola

    #Abre un cuadro de dialogo que permite al usuario seleccionar el archivo
    archivo = filedialog.askopenfilename(
        parent = ventana,
        title = "Seleccionar archivo LOTE",
        filetypes = [("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],     #Establece los tipos de archivos que se pueden visualizar
    )
    #Cierra y libera los recursos de la ventana de Tkiknter
    ventana.destroy()
    #Devuelve la ruta del archivo seleccinado por el usuario
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
        # Se limpian los espacios y las comillas que agrega Windows al arrastrar.
        archivo = texto.strip().strip("\"'")

        if archivo == TECLA_VOLVER:
            return None
        if not archivo:                                                 #si se dejo vacio el campo y se presiono Enter, Vuelve a pedir nombre dela archivo
            print("No escribio ningun nombre. Intente de nuevo.\n") 
            continue
        if not os.path.isfile(archivo):                                 #Si el archivo buscado no se encuentra, Vuelve a pedir nombre del archivo
            print(f"No se encontro el archivo: {archivo}")
            print("Verifique el nombre y la extension (.csv) e intente de nuevo.\n")
            continue
        #Devuelve la ruta del archivo seleccinado por el usuario
        return archivo

def menu_archivo():
    """Segundo menu. Devuelve la ruta elegida, o None si el usuario vuelve atrás."""
    while True:
        print("\n-------Modo de seleccion de Archivo-------")               #Muestra menu de modo de seleccion del archivo
        print("1. Escribir el nombre del archivo")
        print("2. Seleccionar desde una carpeta (abre una ventana)")
        print("3. Volver")
        opcion = input("Opcion: ").strip()

        if opcion == "1":                           #La opcion 1 llama a la funcion pedir_nombre_archivo()
            archivo = pedir_nombre_archivo()
            if archivo:
                return archivo
            print("Volviendo al menu de seleccion de archivo.")
        elif opcion == "2":                         #La opcion 2 llama a la funcion seleccionar_lote()
                archivo = seleccionar_lote()
                if archivo:                         #Si se selecciono archivo lo usa para la simulacion
                    return archivo
                print("Seleccion Cancelada.")       #Si no se selecciono nada se manda un mensaje avisando lo sucedido
        elif opcion == "3":                         #Si selecciona opcion 3 vuelve al menu principal
            return None
    
        else:
            print("Opcion no existe, intente de nuevo.")        #Si no selecciona una de las opciones, manda un mensaje de aviso y pide devuelta 

def ejecucion():
    """Pide un archivo y lo ejecuta. Si el lote no sirve, vuelve a pedirlo."""
    #inicia el bucle para permitir que el usuario vuelva a seleccionar un archivo di rl aanterior presenta algun problema.
    while True:
        #llama a la funcion menu_archivo(), para mostrar el menu de modo de seleccion de archivo
        #y permitir que el usuario seleccione un archivo
        archivo = menu_archivo()
        if not archivo:                 # el usuario eligió "Volver"
            return
        print(f"\n Archivo Seleccionado: {archivo}")    #Muentra por pantalla que el usuario eligio un archivo y el nombre de dicho archivo

        #lee y procesa el contenido del archivo seleccionado
        try:
            procesos = leer_procesos(archivo)
        # Captura posibles errores que pueden ocurrir durante la lectura:
        # OSError: problemas al abrir o acceder al archivo.
        # UnicodeError: problemas con la codificación del archivo.
        # ValueError: datos con valores incorrectos.
        # IndexError: intento de acceder a una posición inexistente.
        except (OSError, UnicodeError, ValueError, IndexError) as error:
            #Muestra el mensaje de error que se produjo y pide al usuario que debe seleccionar otro archivo
            print(f"\n No se puede leer el archivo: {error}")
            print("Vuelva a intentarlo con otro archivo.")
            continue
        #comprueba si la lista de procesos esta vacia o si no se encontraron procesos validos en el archivo
        if not procesos:                #Si todas las filas resultaron inválidas, se solicita al usuario que vuelta a intentarlo coln otro archivo
            print("\n El archivo no contiene procesos validos.")
            print("Vuelva a intentarlo con otro archivo.")
            continue
        #Si el archivo contiene procesos validos y se leyo correctamente,
        #sale del bucle y continua on la ejecucion del simulador
        break

    #Indica que La pausa entre eventos es obligatoria: se avanza con ENTER.
    sim = Simulador(procesos, al_evento=mostrar_estado)
    #Inicia la ejecucion de la simulacion 
    sim.ejecutar()
    #Una vez finalizada la simulacion, genera y muestra un infirme con los resultados obtenidos.
    mostrar_informe(sim)
