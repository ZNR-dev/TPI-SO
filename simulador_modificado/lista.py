"""Lista simplemente enlazada genérica, usada para todas las colas del simulador.

Mantiene punteros al primero y al último para que agregar al final sea O(1).
"""


class NodoLista:
    """Nodo con un dato y un puntero al siguiente."""

    def __init__(self, dato):
        self.dato = dato
        self.prox = None


class ListaEnlazada:
    """Cola FIFO con operaciones de búsqueda y mínimo.

    Se usa para pendientes, nuevos, listos, suspendidos y terminados.
    """

    def __init__(self):
        self.prim = None      # primer nodo
        self.ult = None       # último nodo (para agregar en O(1))
        self.tamanio = 0      # cantidad de elementos

    def __len__(self):
        return self.tamanio

    def __iter__(self):
        """Recorre la lista de principio a fin sin modificarla."""
        p = self.prim
        while p is not None:
            yield p.dato
            p = p.prox

    def vacia(self):
        return self.tamanio == 0

    def agregar(self, dato):
        """Agrega al final (orden de llegada)."""
        nodo = NodoLista(dato)
        if self.prim is None:             # lista vacía: el nuevo es primero y último
            self.prim = self.ult = nodo
        else:                             # se engancha después del último
            self.ult.prox = nodo
            self.ult = nodo
        self.tamanio += 1

    def primero(self):
        """Devuelve el primer dato sin quitarlo (None si la lista está vacía)."""
        return self.prim.dato if self.prim else None

    def quitar_primero(self):
        """Saca y devuelve el primer dato (None si la lista está vacía)."""
        if self.prim is None:
            return None
        nodo = self.prim
        self.prim = nodo.prox
        if self.prim is None:             # se vació: también hay que limpiar el último
            self.ult = None
        self.tamanio -= 1
        return nodo.dato

    def quitar(self, dato):
        """Quita un elemento concreto (por identidad). Devuelve True si estaba."""
        ant, p = None, self.prim
        while p is not None:
            if p.dato is dato:            # identidad, no igualdad: sirve para procesos
                if ant is None:           # era el primero
                    self.prim = p.prox
                else:                     # saltea el nodo
                    ant.prox = p.prox
                if p is self.ult:         # era el último: el anterior pasa a ser último
                    self.ult = ant
                self.tamanio -= 1
                return True
            ant, p = p, p.prox
        return False

    def minimo(self, clave):
        """Elemento con menor clave; en empate gana el que está primero."""
        mejor = None
        for dato in self:
            if mejor is None or clave(dato) < clave(mejor):
                mejor = dato
        return mejor

    def __str__(self):
        return ", ".join(str(d) for d in self) if self.tamanio else "(vacía)"
