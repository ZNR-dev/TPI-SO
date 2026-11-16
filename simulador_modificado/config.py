"""Constantes globales del simulador.

El modelo de memoria es MVT (particiones variables): el SO ocupa una zona fija
y el resto se reparte entre los procesos según lo que cada uno pide.
"""

TAM_SO = 100          # K reservados al Sistema Operativo (zona fija, no se asigna)
TAM_USUARIO = 450     # K disponibles para procesos de usuario
MAX_PROCESOS = 10     # máximo de procesos que se cargan desde un CSV
MAX_EN_SISTEMA = 5    # Ejecución + Listos + Listos/Suspendidos
GRANULARIDAD = 10     # K mínimos por asignación (la memoria se redondea a múltiplos)
