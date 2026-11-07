"""Tests automáticos del simulador.

Ejecutar desde la carpeta del proyecto:
    python -m unittest test_simulador -v
"""
import os
import tempfile
import unittest

import contextlib
import io

from config import MAX_EN_SISTEMA, TAM_USUARIO
from entrada import leer_procesos
from memoria import Memoria
from planificador import Simulador
from proceso import Proceso


def proc(id, tam, arribo=0, irr=3):
    return Proceso(id, arribo, tam, irr)


def memoria_llena_de_5(tam=90):
    """Memoria con A,B,C,D,E de 90K cada uno (ocupa los 450K completos)."""
    mem = Memoria()
    for letra in "ABCDE":
        assert mem.asignar(proc(letra, tam))
    return mem


def bloques(mem):
    """Lista simple de (base, tamaño, proceso) para comparar fácil."""
    resultado = []
    nodo = mem.prim
    while nodo is not None:
        resultado.append((nodo.base, nodo.tam, nodo.proc))
        nodo = nodo.prox
    return resultado


# --------------------------------------------------------------- MEMORIA
class TestBestFit(unittest.TestCase):
    def test_elige_el_hueco_mas_justo(self):
        mem = Memoria()
        for id, tam in [("A", 100), ("B", 50), ("C", 200), ("D", 30), ("E", 70)]:
            mem.asignar(proc(id, tam))
        mem.liberar("B")   # hueco de 50K en base 100
        mem.liberar("D")   # hueco de 30K en base 350
        self.assertTrue(mem.asignar(proc("F", 25)))
        # F debe ir al hueco de 30K (el que menos sobra), no al de 50K
        self.assertIn((350, 25, "F"), bloques(mem))
        self.assertIn((100, 50, None), bloques(mem))

    def test_sin_hueco_devuelve_false(self):
        mem = memoria_llena_de_5()
        self.assertFalse(mem.asignar(proc("X", 10)))

    def test_proceso_exacto_no_deja_sobrante(self):
        mem = Memoria()
        self.assertTrue(mem.asignar(proc("A", TAM_USUARIO)))
        self.assertEqual(len(bloques(mem)), 1)


class TestFusionDeHuecos(unittest.TestCase):
    def test_fusion_con_el_siguiente(self):
        mem = memoria_llena_de_5()
        mem.liberar("C")
        mem.liberar("B")   # B libera y su siguiente (C) ya está libre
        self.assertIn((90, 180, None), bloques(mem))

    def test_fusion_con_el_anterior(self):
        mem = memoria_llena_de_5()
        mem.liberar("B")
        mem.liberar("C")   # C libera y su anterior (B) ya está libre
        self.assertIn((90, 180, None), bloques(mem))

    def test_fusion_con_ambos_vecinos(self):
        mem = memoria_llena_de_5()
        mem.liberar("B")
        mem.liberar("D")
        mem.liberar("C")   # une los 3 huecos en uno solo
        self.assertEqual(
            bloques(mem),
            [(0, 90, "A"), (90, 270, None), (360, 90, "E")],
        )
        self.assertEqual(mem.fragmentacion_externa(), 0)

    def test_huecos_separados_generan_fragmentacion_externa(self):
        mem = memoria_llena_de_5()
        mem.liberar("B")
        mem.liberar("D")
        self.assertEqual(mem.fragmentacion_externa(), 90)  # 180 libres - 90 mayor


# ----------------------------------------------------------- PLANIFICADOR
class TestLimiteDeProcesos(unittest.TestCase):
    def test_nunca_hay_mas_de_5_en_sistema(self):
        procesos = [proc(f"P{i}", 10, arribo=0, irr=3) for i in range(1, 9)]
        sim = Simulador(procesos)
        maximos = []
        original = sim._ejecutar_unidad

        def espia():
            maximos.append(sim.en_sistema())
            original()

        sim._ejecutar_unidad = espia
        sim.ejecutar()
        self.assertEqual(max(maximos), MAX_EN_SISTEMA)
        self.assertEqual(len(sim.terminados), 8)


class TestSuspensionYReanudacion(unittest.TestCase):
    def test_suspende_y_reanuda_cuando_se_libera_memoria(self):
        p1 = proc("P1", 300, irr=5)
        p2 = proc("P2", 200, irr=2)   # no entra: quedan solo 150K
        sim = Simulador([p1, p2])

        # un solo instante, a mano, antes de ejecutar
        sim._recibir_llegadas()
        sim._reanudar_suspendidos()
        sim._admitir_nuevos()
        self.assertIn(p2, list(sim.susp))
        self.assertEqual(p2.estado, "Listo y Suspendido")

        sim.ejecutar()
        self.assertEqual(p1.fin, 5)
        self.assertEqual(p2.fin, 7)   # entra recién cuando P1 libera su memoria


class TestSRTF(unittest.TestCase):
    def test_orden_de_finalizacion_y_expropiacion(self):
        p1 = proc("P1", 10, arribo=0, irr=6)
        p2 = proc("P2", 10, arribo=1, irr=2)
        p3 = proc("P3", 10, arribo=2, irr=1)
        sim = Simulador([p1, p2, p3])
        sim.ejecutar()
        # P2 expropia a P1 (2 < 5). P3 llega con igual restante que P2 (1 = 1):
        # no expropia, porque la comparación es estricta. Termina primero P2.
        self.assertEqual((p2.fin, p3.fin, p1.fin), (3, 4, 9))


# ---------------------------------------------------------------- ENTRADA
class TestLecturaCSV(unittest.TestCase):
    def csv(self, filas):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                        encoding="utf-8", newline="")
        f.write("id,arribo,tam,irrupcion\n" + "\n".join(filas) + "\n")
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_lee_lote_valido(self):
        ps = leer_procesos(self.csv(["P1,0,100,5", "P2,1,50,3"]))
        self.assertEqual([p.id for p in ps], ["P1", "P2"])
        self.assertEqual((ps[0].arribo, ps[0].tam, ps[0].irr), (0, 100, 5))

    

    def test_descarta_proceso_mas_grande_que_la_memoria(self):
        ps = leer_procesos(self.csv(["P1,0,999,3", "P2,0,100,3"]))
        self.assertEqual([p.id for p in ps], ["P2"])

    def leer_en_silencio(self, filas):
        """Lee el CSV sin mostrar los avisos en pantalla."""
        with contextlib.redirect_stdout(io.StringIO()):
            return leer_procesos(self.csv(filas))

    def test_descarta_irrupcion_cero(self):
        ps = self.leer_en_silencio(["P1,0,100,0", "P2,0,50,3"])
        self.assertEqual([p.id for p in ps], ["P2"])

    def test_descarta_tamano_negativo(self):
        ps = self.leer_en_silencio(["P1,0,-5,3", "P2,0,50,3"])
        self.assertEqual([p.id for p in ps], ["P2"])

    def test_descarta_id_duplicado(self):
        ps = self.leer_en_silencio(["P1,0,100,3", "P1,1,50,3"])
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0].tam, 100)   # se queda con el primero

    def test_descarta_dato_no_numerico(self):
        ps = self.leer_en_silencio(["P1,0,abc,3", "P2,0,50,3"])
        self.assertEqual([p.id for p in ps], ["P2"])

    def test_descarta_fila_incompleta(self):
        ps = self.leer_en_silencio(["P1,0,100", "P2,0,50,3"])
        self.assertEqual([p.id for p in ps], ["P2"])

if __name__ == "__main__":
    unittest.main()