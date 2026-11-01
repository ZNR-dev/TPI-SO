"""Simulador: admisión de procesos + planificación SRTF sobre la memoria MVT."""
from config import MAX_EN_SISTEMA
from lista import ListaEnlazada
from memoria import Memoria


class Simulador:
    def __init__(self, procesos, al_evento=None):
        """al_evento(sim): función que se llama ante cada llegada o terminación."""
        self.procesos = procesos
        self.al_evento = al_evento
        self.pendientes = ListaEnlazada()      # todavía no llegaron
        for p in sorted(procesos, key=lambda p: p.arribo):
            self.pendientes.agregar(p)
        self.nuevos = ListaEnlazada()
        self.listos = ListaEnlazada()
        self.susp = ListaEnlazada()            # Listos y Suspendidos
        self.terminados = ListaEnlazada()
        self.cpu = None
        self.mem = Memoria()
        self.t = 0
        self.eventos = []
        self.fe_max = 0          # mayor fragmentación externa observada
        self.fe_max_t = 0        # instante en que se alcanzó
        self.fe_suma = 0         # acumulado para el promedio temporal
        self.fe_muestras = 0

    def en_sistema(self):
        return len(self.listos) + len(self.susp) + (1 if self.cpu else 0)

    # ---- etapas de cada instante
    def _recibir_llegadas(self):
        while not self.pendientes.vacia() and self.pendientes.primero().arribo <= self.t:
            p = self.pendientes.quitar_primero()
            p.estado = "Nuevo"
            self.nuevos.agregar(p)
            self.eventos.append(f"llegó {p.id}")

    def _reanudar_suspendidos(self):
        """Los suspendidos tienen prioridad para entrar a memoria."""
        for p in list(self.susp):
            if self.mem.asignar(p):
                self.susp.quitar(p)
                p.estado = "Listo"
                self.listos.agregar(p)

    def _admitir_nuevos(self):
        while not self.nuevos.vacia() and self.en_sistema() < MAX_EN_SISTEMA:
            p = self.nuevos.quitar_primero()
            if self.mem.asignar(p):
                p.estado = "Listo"
                self.listos.agregar(p)
            else:
                p.estado = "Listo y Suspendido"
                self.susp.agregar(p)

    def _planificar_srtf(self):
        """Expropiativo: solo desplaza a la CPU si el candidato es estrictamente menor."""
        mejor = self.listos.minimo(lambda p: p.rest)
        if mejor is None:
            return
        if self.cpu is None or mejor.rest < self.cpu.rest:
            if self.cpu:
                self.cpu.estado = "Listo"
                self.listos.agregar(self.cpu)
            self.listos.quitar(mejor)
            mejor.estado = "Ejecución"
            self.cpu = mejor

    def _notificar(self):
        if self.eventos:
            if self.al_evento:
                self.al_evento(self)
            self.eventos = []

    def _ejecutar_unidad(self):
        self.t += 1
        if self.cpu:
            self.cpu.rest -= 1
            if self.cpu.rest == 0:
                self.cpu.fin = self.t
                self.cpu.estado = "Terminado"
                self.mem.liberar(self.cpu.id)
                self.terminados.agregar(self.cpu)
                self.eventos.append(f"terminó {self.cpu.id}")
                self.cpu = None

    def _registrar_frag_externa(self):
        """Muestrea la fragmentación externa al final de cada instante."""
        fe = self.mem.fragmentacion_externa()
        self.fe_suma += fe
        self.fe_muestras += 1
        if fe > self.fe_max:
            self.fe_max = fe
            self.fe_max_t = self.t

    # ---- ciclo principal
    def ejecutar(self):
        total = len(self.procesos)
        while len(self.terminados) < total:
            self._recibir_llegadas()
            self._reanudar_suspendidos()
            self._admitir_nuevos()
            self._planificar_srtf()
            self._notificar()
            self._ejecutar_unidad()
            self._registrar_frag_externa()
        self._notificar()

