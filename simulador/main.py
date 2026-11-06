"""Punto de entrada del simulador con selección interactiva del lote CSV.

Al iniciar, se abre un cuadro de diálogo para que el usuario seleccione
el archivo LOTE. La simulación solo comienza después de seleccionar un archivo.
"""
import tkinter as tk
from tkinter import filedialog, messagebox

from entrada import leer_procesos
from planificador import Simulador
from salida import mostrar_estado, mostrar_informe


def seleccionar_lote():
    """Abre el explorador de archivos y devuelve la ruta del CSV seleccionado."""
    ventana = tk.Tk()
    ventana.withdraw()  # Oculta la ventana principal de Tkinter.

    archivo = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar archivo LOTE",
        filetypes=[
            ("Archivos CSV", "*.csv"),
            ("Todos los archivos", "*.*"),
        ],
    )

    ventana.destroy()
    return archivo


def main():
    archivo = seleccionar_lote()

    # Si el usuario cierra el diálogo o presiona Cancelar, no se ejecuta nada.
    if not archivo:
        print("Selección cancelada. No se ejecutó la simulación.")
        return

    try:
        procesos = leer_procesos(archivo)
    except (OSError, UnicodeError, ValueError, IndexError) as error:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror(
            "Error al leer el lote",
            f"No se pudo leer el archivo seleccionado.\n\nDetalle: {error}",
            parent=raiz,
        )
        raiz.destroy()
        return

    if not procesos:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showwarning(
            "Lote vacío",
            "El archivo seleccionado no contiene procesos válidos. "
            "No se ejecutó la simulación.",
            parent=raiz,
        )
        raiz.destroy()
        print("No hay procesos para simular.")
        return

    print(f"Archivo seleccionado: {archivo}")
    sim = Simulador(procesos, al_evento=mostrar_estado)
    sim.ejecutar()
    mostrar_informe(sim)


if __name__ == "__main__":
    main()
