"""Modelo de proceso."""


class Proceso:
    def __init__(self, id, arribo, tam, irrupcion):
        self.id = id
        self.arribo = arribo
        self.tam = tam
        self.irr = irrupcion
        self.rest = irrupcion      # tiempo de CPU restante
        self.estado = "Nuevo"      # Nuevo, Listo, Listo y Suspendido, Ejecución, Terminado
        self.fin = None
        self.arribo_efectivo = None

    def __str__(self):
        return f"{self.id}(TIr={self.rest})"
