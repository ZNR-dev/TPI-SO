"""Presentación por consola: estado en cada evento e informe final."""
from config import TAM_SO


def mostrar_estado(sim):
    print("\n" + "=" * 60)
    print(f"Tiempo {sim.t}: " + " | ".join(sim.eventos))
    print("=" * 60)
    print("Procesador:", sim.cpu if sim.cpu else "ocioso")

    print("\nTabla de particiones:")
    print(f"{'Part':>4} {'Inicio':>7} {'Tamaño':>7} {'Proceso':>8} {'Frag.int':>9}")
    print(f"{'SO':>4} {0:>6}K {TAM_SO:>6}K {'-':>8} {'-':>9}")
    tam_procesos = {p.id: p.tam for p in sim.procesos}
    for id, base, tam, proc, frag in sim.mem.filas(tam_procesos):
        print(f"{id:>4} {base + TAM_SO:>6}K {tam:>6}K {proc or 'libre':>8} {frag:>8}K")

    print("\nCola de Listos:             ", sim.listos)
    print("Cola de Listos/Suspendidos: ", sim.susp)
    print("Nuevos (esperando admisión):", sim.nuevos)
    input("\n[ENTER para continuar]")


def mostrar_informe(sim):
    print("\n" + "=" * 60)
    print("INFORME ESTADÍSTICO")
    print("=" * 60)
    print(f"{'Proceso':>8} {'Arribo':>7} {'Irrup.':>7} {'Fin':>5} {'Retorno':>8} {'Espera':>7}")
    tot_ret = tot_esp = 0
    for p in sorted(sim.terminados, key=lambda p: p.id):
        retorno = p.fin - p.arribo
        espera = retorno - p.irr
        tot_ret += retorno
        tot_esp += espera
        print(f"{p.id:>8} {p.arribo:>7} {p.irr:>7} {p.fin:>5} {retorno:>8} {espera:>7}")
    n = len(sim.terminados)
    print(f"\nRetorno promedio: {tot_ret / n:.2f}")
    print(f"Espera promedio:  {tot_esp / n:.2f}")
    print(f"Rendimiento: {n} trabajos / {sim.t} u.t. = {n / sim.t:.3f} trabajos por unidad de tiempo")
