"""Modelo de un proceso y su estado dentro de la simulación."""


class Proceso:
    """Representa un trabajo del lote.

    `arribo` es el instante en que llega al sistema; `arribo_efectivo` es el
    instante en que consigue entrar a memoria por primera vez. La diferencia
    entre ambos permite comparar las métricas originales con las efectivas.
    """

    def __init__(self, id, arribo, tam, irrupcion):
        self.id = id                  # identificador único dentro del lote
        self.arribo = arribo          # instante de llegada (TA)
        self.tam = tam                # tamaño solicitado en K
        self.irr = irrupcion          # tiempo total de CPU (TI)
        self.rest = irrupcion         # tiempo de CPU restante (TIr)
        self.estado = "Nuevo"         # Nuevo, Listo, Listo y Suspendido, Ejecución, Terminado
        self.fin = None               # instante en que termina; None mientras no terminó
        self.arribo_efectivo = None   # primer instante en que ocupa memoria

    def __str__(self):
        # Se usa en la línea "Procesador: ..." del estado.
        return f"{self.id}(TIr={self.rest})"
