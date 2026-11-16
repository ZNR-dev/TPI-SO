"""Simulador: admisión de procesos + planificación SRTF sobre la memoria MVT."""
from config import MAX_EN_SISTEMA
from lista import ListaEnlazada
from memoria import Memoria


class Simulador:
    """Ciclo de simulación por unidades de tiempo.

    En cada instante se ejecutan siempre las mismas etapas, en este orden:
    llegadas -> reanudar suspendidos -> admitir nuevos -> planificar -> ejecutar.
    """

    def __init__(self, procesos, al_evento=None):
        """al_evento(sim): función que se llama ante cada llegada o terminación."""
        self.procesos = procesos
        self.al_evento = al_evento
        self.pendientes = ListaEnlazada()      # todavía no llegaron
        for p in sorted(procesos, key=lambda p: p.arribo):
            self.pendientes.agregar(p)
        self.nuevos = ListaEnlazada()          # llegaron pero no fueron admitidos
        self.listos = ListaEnlazada()          # en memoria, esperando CPU
        self.susp = ListaEnlazada()            # Listos y Suspendidos (sin memoria)
        self.terminados = ListaEnlazada()      # ya finalizaron
        self.cpu = None                        # proceso en ejecución (o None)
        self.mem = Memoria()
        self.t = 0                             # reloj de la simulación
        self.eventos = []                      # eventos del instante actual
        self.hubo_swap_in = False              # para avisar una reanudación
        self.fe_max = 0          # mayor fragmentación externa observada
        self.fe_max_t = 0        # instante en que se alcanzó
        self.fe_suma = 0         # acumulado para el promedio temporal
        self.fe_muestras = 0

    def en_sistema(self):
        """Procesos que cuentan para el límite MAX_EN_SISTEMA."""
        return len(self.listos) + len(self.susp) + (1 if self.cpu else 0)

    # ---- etapas de cada instante
    def _recibir_llegadas(self):
        """Mueve a Nuevos los procesos cuyo instante de arribo ya se alcanzó."""
        while not self.pendientes.vacia() and self.pendientes.primero().arribo <= self.t:
            p = self.pendientes.quitar_primero()
            p.estado = "Nuevo"
            self.nuevos.agregar(p)
            self.eventos.append(f"llegó {p.id}")

    def _reanudar_suspendidos(self):
        """Los suspendidos tienen prioridad para entrar a memoria."""
        for p in list(self.susp):
            if self.mem.asignar(p):
                # Si es la primera vez que entra a memoria, se registra el arribo efectivo.
                if p.arribo_efectivo is None:
                    p.arribo_efectivo = self.t
                
                self.susp.quitar(p)
                p.estado = "Listo"
                self.listos.agregar(p)
                self.hubo_swap_in = True
                self.eventos.append(f"{p.id} pasa de suspendido a listo (entro en memoria)")

    def _admitir_nuevos(self):
        """Admite procesos de Nuevos mientras haya lugar en el sistema y en memoria."""
        while not self.nuevos.vacia() and self.en_sistema() < MAX_EN_SISTEMA:
            p = self.nuevos.quitar_primero()
            if self.mem.asignar(p):
                p.arribo_efectivo = self.t          # primera vez que ocupa memoria
                p.estado = "Listo"
                self.listos.agregar(p)
                self.eventos.append(f"{p.id} pasa de nuevos a listo (entro en memoria)")
            else:
                # Hay lugar en el sistema pero no hueco en memoria: queda suspendido.
                p.estado = "Listo y Suspendido"
                self.susp.agregar(p)
                self.eventos.append(f"{p.id} pasa a listos/suspendido (no hay hueco en memoria)")

    def _planificar_srtf(self):
        """Expropiativo: solo desplaza a la CPU si el candidato es estrictamente menor."""
        # Desempate determinista: menor restante, luego arribo, luego id.
        mejor = self.listos.minimo(lambda p: (p.rest, p.arribo, p.id))
        if mejor is None:
            return
        if self.cpu is None or mejor.rest < self.cpu.rest:
            if self.cpu:
                # El proceso actual vuelve a Listos y el candidato lo expropia.
                self.cpu.estado = "Listo"
                self.listos.agregar(self.cpu)
                self.eventos.append(f"{mejor.id} pasa a ejecucion (expropia a {self.cpu.id})")
            else:
                self.eventos.append(f"{mejor.id} pasa a ejecucion")

            self.listos.quitar(mejor)
            mejor.estado = "Ejecución"
            self.cpu = mejor

    def _notificar(self):
        """Muestra el estado si hubo eventos y limpia la lista de eventos."""
        if self.eventos:
            if self.al_evento:
                self.al_evento(self)
            self.eventos = []

    def _ejecutar_unidad(self):
        """Avanza el reloj una unidad y descuenta CPU al proceso en ejecución."""
        self.t += 1
        if self.cpu:
            self.cpu.rest -= 1
            if self.cpu.rest == 0:              # terminó: libera memoria y pasa a Terminados
                self.cpu.fin = self.t
                self.cpu.estado = "Terminado"
                self.mem.liberar(self.cpu.id)
                self.terminados.agregar(self.cpu)
                self.eventos.append(f"terminó {self.cpu.id}")
                self.cpu = None

    def _registrar_frag_externa(self):
        """Muestrea la fragmentación externa al final de cada instante."""
        fe = self.mem.fragmentacion_externa(self.susp)
        self.fe_suma += fe
        self.fe_muestras += 1
        if fe > self.fe_max:
            self.fe_max = fe
            self.fe_max_t = self.t

    # ---- ciclo principal
    def ejecutar(self):
        """Corre la simulación hasta que terminan todos los procesos."""
        total = len(self.procesos)
        while len(self.terminados) < total:
            self._recibir_llegadas()
            self._reanudar_suspendidos()
            self._admitir_nuevos()
            if self.hubo_swap_in:               # avisa la reanudación antes de planificar
                self._notificar()
                self.hubo_swap_in = False

            self._planificar_srtf()
            self._notificar()
            self._ejecutar_unidad()
            self._registrar_frag_externa()
        self._notificar()
