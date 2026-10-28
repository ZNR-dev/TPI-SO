"""Lista simplemente enlazada genérica, usada para todas las colas."""


class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.prox = None


class ListaEnlazada:
    def __init__(self):
        self.prim = None
        self.ult = None
        self.tamanio = 0

    def __len__(self):
        return self.tamanio

    def __iter__(self):
        p = self.prim
        while p is not None:
            yield p.dato
            p = p.prox

    def vacia(self):
        return self.tamanio == 0

    def agregar(self, dato):
        """Agrega al final (orden de llegada)."""
        nodo = NodoLista(dato)
        if self.prim is None:
            self.prim = self.ult = nodo
        else:
            self.ult.prox = nodo
            self.ult = nodo
        self.tamanio += 1

    def primero(self):
        return self.prim.dato if self.prim else None

    def quitar_primero(self):
        if self.prim is None:
            return None
        nodo = self.prim
        self.prim = nodo.prox
        if self.prim is None:
            self.ult = None
        self.tamanio -= 1
        return nodo.dato

    def quitar(self, dato):
        """Quita un elemento concreto (por identidad). Devuelve True si estaba."""
        ant, p = None, self.prim
        while p is not None:
            if p.dato is dato:
                if ant is None:
                    self.prim = p.prox
                else:
                    ant.prox = p.prox
                if p is self.ult:
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
