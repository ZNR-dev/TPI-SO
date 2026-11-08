"""Presentación por consola: estado en cada evento e informe final."""
from config import TAM_SO
 
 
def _tabla(titulo, encabezados, filas, vacia="(vacía)"):
    """Dibuja una tabla con bordes. Todas las tablas del simulador usan esta función.
    encabezados: lista de títulos de columna. filas: lista de listas de celdas.
    Si no hay filas, muestra la tabla con una fila que dice `vacia`."""
    print(f"\n{titulo}:")
    filas = [[str(c) for c in fila] for fila in filas]
    anchos = [max([len(h)] + [len(f[i]) for f in filas])
              for i, h in enumerate(encabezados)]
    total = sum(anchos) + 3 * len(anchos) - 1       # ancho interior de toda la tabla
 
    def borde(izq, med, der):
        return izq + med.join("─" * (a + 2) for a in anchos) + der
 
    def fila(celdas):
        return "│" + "│".join(f" {c:^{a}} " for c, a in zip(celdas, anchos)) + "│"
 
    print(borde("┌", "┬", "┐"))
    print(fila(encabezados))
    if filas:
        print(borde("├", "┼", "┤"))
        for f in filas:
            print(fila(f))
        print(borde("└", "┴", "┘"))
    else:
        print(borde("├", "┴", "┤"))
        print("│" + vacia.center(total) + "│")
        print("└" + "─" * total + "┘")
 
 
def _filas_procesos(procesos, restante=False):
    """Filas PID | Arribo | Irrupción (o Restante) | Tamaño para una cola."""
    return [[p.id, p.arribo, p.rest if restante else p.irr, f"{p.tam}K"]
            for p in procesos]
 
 
def _unir(textos):
    """['120K', '10K', '5K'] -> '120K, 10K y 5K'."""
    if len(textos) <= 1:
        return "".join(textos)
    return ", ".join(textos[:-1]) + " y " + textos[-1]
 
 
def _explicar_frag_externa(sim, bloques):
    """Explica por qué hay fragmentación externa y qué procesos quedan afectados.
    bloques: filas de sim.mem.filas(...). Solo se llama si la fragmentación es > 0."""
    libres = [tam for _, _, tam, proc, _ in bloques if proc is None]
    total, mayor = sum(libres), max(libres)
    print(f"  Particiones libres separadas: {_unir([f'{h}K' for h in libres])} "
          f"(suman {total}K, pero la mayor es de {mayor}K).")
    print("  No se pueden unir porque hay procesos ocupando memoria entre ellas.")
    afectados = [f"{p.id} ({p.tam}K)" for p in sim.susp if mayor < p.tam <= total]

    if len(afectados) == 1:
        print(f" Espera aunque la suma alcanzaría: {afectados[0]}.")
    else:
        print(f" Esperan aunque la suma alcanzaría: {_unir(afectados)}. "
            "Cualquiera de ellos entraría, pero no todos a la vez.")


def mostrar_estado(sim):
    print("\n" + "=" * 60)
    print(f"Tiempo {sim.t}: " + " | ".join(sim.eventos))
    print("=" * 60)
    print("Procesador:", sim.cpu if sim.cpu else "ocioso")
 
    # La tabla de Nuevos va arriba de la memoria
    _tabla("Nuevos (esperando admisión)",
           ["PID", "Arribo", "Irrupción", "Tamaño"],
           _filas_procesos(sim.nuevos))
 
    tam_procesos = {p.id: p.tam for p in sim.procesos}
    bloques = sim.mem.filas(tam_procesos)
    filas_mem = [["SO", "0K", f"{TAM_SO}K", "-"]]
    for id, base, tam, proc, frag in bloques:
        filas_mem.append([id, f"{base + TAM_SO}K", f"{tam}K", proc or "libre"])
    _tabla("Tabla de particiones",
           ["Part", "Inicio", "Tamaño", "Proceso"], filas_mem)
 
    fe = sim.mem.fragmentacion_externa(sim.susp)
    print(f"\nFragmentación externa: {fe}K")
    if fe > 0:
        _explicar_frag_externa(sim, bloques)
 
    _tabla("Cola de Listos",
           ["PID", "Arribo", "Restante", "Tamaño"],
           _filas_procesos(sim.listos, restante=True))
    _tabla("Cola de Listos/Suspendidos",
           ["PID", "Arribo", "Restante", "Tamaño"],
           _filas_procesos(sim.susp, restante=True))
    input("\n[ENTER para continuar]")
 
 
def mostrar_informe(sim):
    print("\n" + "=" * 60)
    print("INFORME ESTADÍSTICO")
    print("=" * 60)
    filas = []
    tot_ret = tot_esp = 0
    for p in sorted(sim.terminados, key=lambda p: p.id):
        retorno = p.fin - p.arribo
        espera = retorno - p.irr
        tot_ret += retorno
        tot_esp += espera
        filas.append([p.id, p.arribo, p.irr, p.fin, retorno, espera])
    _tabla("Resultados por proceso",
           ["Proceso", "Arribo", "Irrup.", "Fin", "Retorno", "Espera"], filas)
 
    n = len(sim.terminados)
    print(f"\nRetorno promedio: {tot_ret / n:.2f}")
    print(f"Espera promedio:  {tot_esp / n:.2f}")
    print(f"Rendimiento: {n} trabajos / {sim.t} u.t. = {n / sim.t:.3f} trabajos por unidad de tiempo")
 
    prom_fe = sim.fe_suma / sim.fe_muestras if sim.fe_muestras else 0
    print("\nFragmentación externa (memoria libre no contigua):")
    print(f"  Máxima:   {sim.fe_max:>6}K (en t={sim.fe_max_t})")
    print(f"  Promedio: {prom_fe:>6.2f}K")