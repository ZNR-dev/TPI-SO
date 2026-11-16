"""Memoria con particiones variables (MVT) y Best-Fit.

Lista simplemente enlazada ORDENADA POR DIRECCIÓN: los nodos están en el mismo
orden físico en que están en memoria. Por eso los vecinos físicos son vecinos
en la lista y la fusión de libres solo mira el nodo anterior y el siguiente.
"""
from config import TAM_USUARIO, GRANULARIDAD


def _tam_requerido(tam):
    """Redondea hacia arriba al múltiplo de GRANULARIDAD.

    La memoria se asigna en bloques de 10K, así que un pedido de 149K ocupa
    150K. Esa diferencia (1K) es la fragmentación interna del bloque.
    """
    return max(GRANULARIDAD, ((tam + GRANULARIDAD - 1) // GRANULARIDAD) * GRANULARIDAD)


class NodoMem:
    """Bloque de memoria: ocupado (proc tiene id) o libre (proc is None)."""

    def __init__(self, id, base, tam, proc=None):
        self.id = id
        self.base = base       # dirección de comienzo (relativa a la zona de usuario)
        self.tam = tam
        self.proc = proc       # id del proceso o None si está libre
        self.prox = None       # siguiente bloque en orden de dirección


class Memoria:
    """Administra la zona de usuario como una lista de bloques contiguos."""

    def __init__(self):
        self.sig_id = 1
        self.prim = NodoMem(self.sig_id, 0, TAM_USUARIO)   # un único hueco libre
        self.sig_id += 1

    def asignar(self, proc):
        """Best-Fit: recorre toda la lista y elige el hueco libre con menor sobrante."""
        requerido = _tam_requerido(proc.tam)   # tamaño real a ocupar (redondeado)
        mejor = None
        p = self.prim
        while p is not None:
            # Solo sirven bloques libres que alcancen para el pedido.
            if p.proc is None and p.tam >= requerido:
                if mejor is None or p.tam < mejor.tam:   # best fit: el más chico
                    mejor = p
            p = p.prox
        if mejor is None:
            return False                                   # no hay hueco: queda suspendido

        if mejor.tam > requerido:                          # se divide el hueco
            # El sobrante queda como bloque libre inmediatamente después.
            resto = NodoMem(self.sig_id, mejor.base + requerido, mejor.tam - requerido)
            self.sig_id += 1
            resto.prox = mejor.prox                        # el resto libre va justo después
            mejor.prox = resto
            mejor.tam = requerido
        mejor.proc = proc.id
        return True

    def liberar(self, id_proc):
        """Libera el bloque del proceso y fusiona con los vecinos libres."""
        ant, p = None, self.prim
        while p is not None and p.proc != id_proc:         # busca el bloque del proceso
            ant, p = p, p.prox
        if p is None:
            return
        p.proc = None                                      # el bloque queda libre en su lugar

        if p.prox is not None and p.prox.proc is None:     # fusionar con el siguiente libre
            p.tam += p.prox.tam
            p.prox = p.prox.prox
        if ant is not None and ant.proc is None:           # fusionar con el anterior libre
            ant.tam += p.tam
            ant.prox = p.prox

    def fragmentacion_externa(self, esperando=()):
        """Fragmentación externa: hay huecos libres NO adyacentes que, sumados,
        alcanzarían para un proceso que lo necesita, pero ningún hueco por sí
        solo alcanza. Devuelve la suma de los huecos libres si algún proceso de
        `esperando` está en esa situación; si no, 0.
        esperando: procesos que no pudieron entrar a memoria (Listos/Suspendidos)."""
        total = 0
        mayor = 0
        p = self.prim
        while p is not None:
            if p.proc is None:                 # acumula huecos libres
                total += p.tam
                if p.tam > mayor:
                    mayor = p.tam
            p = p.prox
        for proc in esperando:
            # El proceso no entra en el hueco más grande, pero la suma de todos
            # los huecos sí le alcanzaría: eso es fragmentación externa.
            if mayor < _tam_requerido(proc.tam) <= total:
                return total
        return 0

    def filas(self, tam_procesos):
        """Datos para la tabla, ya por dirección: (id, inicio, tamaño, proceso, frag. interna).
        tam_procesos: dict {id_proceso: tamaño}."""
        filas = []
        p = self.prim
        while p is not None:
            # Frag. interna = lo asignado (redondeado) menos lo pedido por el proceso.
            frag = p.tam - tam_procesos[p.proc] if p.proc else 0
            filas.append((p.id, p.base, p.tam, p.proc, frag))
            p = p.prox
        return filas
