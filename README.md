# TPI-SO

Simulador de gestión de memoria para sistemas operativos, desarrollado en Python. El proyecto modela la administración de memoria de un SO con particiones variables, planificación de procesos y métricas de rendimiento para analizar comportamiento bajo carga.

El repositorio contiene una implementación educativa de un simulador orientado a la asignación de memoria y la planificación de CPU, con enfoque en políticas de memoria tipo Best-Fit y procesos con tiempos de arribo, tamaño y duración.

## Descripción del proyecto

El sistema simula una pequeña memoria del sistema con las siguientes características:

- Zona fija reservada para el Sistema Operativo: 100K.
- Zona de usuario disponible: 450K.
- Granularidad de asignación: 10K.
- Límite de procesos activos en el sistema: 5.
- Carga de datos desde archivos CSV.
- Planificación de CPU por SRTF (Shortest Remaining Time First).
- Medición de tiempos de retorno, espera y fragmentación externa.

La simulación permite observar cómo los procesos llegan, son admitidos en memoria, se ejecutan conforme a una política de menor tiempo restante, y cómo el sistema reacciona cuando hay falta de espacio o cuando se liberan bloques de memoria.

## Objetivo

El objetivo principal es estudiar, visualizar y comprender:

- cómo se asigna memoria a procesos en un sistema con particiones variables,
- cómo se comporta la política Best-Fit,
- cómo afecta la fragmentación externa a la admisión de procesos,
- cómo la planificación SRTF impacta el tiempo de respuesta,
- cómo medir la eficiencia del sistema a partir de métricas estadísticas.

## Características principales

- Simulación de memoria con lista enlazada de bloques.
- Política de asignación Best-Fit.
- Control de huecos libres y fusión de particiones contiguas.
- Admitidos y suspendidos por falta de memoria.
- Reanudación automática de procesos suspendidos cuando hay espacio disponible.
- Soporte de lectura de lotes desde CSV con validación de datos.
- Salida por consola con tablas informativas del estado del sistema.
- Informe final con métricas acumuladas por proceso.
- Pruebas automáticas unitarias.

## Estructura del repositorio

```text
TPI-SO/
├── simulador_modificado/
│   ├── config.py            # constantes del sistema y memoria
│   ├── entrada.py           # lectura y validación de CSV
│   ├── interfaz.py          # menú principal del programa
│   ├── lista.py             # estructura de lista enlazada usada por el simulador
│   ├── main.py              # punto de entrada principal
│   ├── memoria.py           # administración de la memoria y fragmentación
│   ├── planificador.py      # ciclo de simulación y política de planificación
│   ├── proceso.py           # modelo del proceso
│   ├── salida.py            # tablas y reportes de salida
│   ├── Test.py              # pruebas automáticas
│   ├── *.csv                # lotes de prueba
│   ├── interfaz.spec       # configuración de PyInstaller
│   ├── interfaz.exe         # ejecutable generado
│   ├── build/               # artefactos de compilación
│   └── __pycache__/        # caché de Python
└── README.md                # documentación del proyecto
```

> Importante: el código principal se encuentra dentro de la carpeta `simulador_modificado/`.

## Modelo de memoria

El simulador utiliza un modelo de memoria tipo MVT (Multiprogramming with Variable Tasks / particiones variables):

- La memoria total disponible para procesos de usuario es de 450K.
- El SO ocupa 100K reservados.
- El espacio asignado a cada proceso se redondea a múltiplos de 10K.
- La memoria se representa como una lista enlazada ordenada por dirección.
- Cuando un proceso termina, su bloque se libera y se fusiona con vecinos libres si es posible.

### Política de asignación

La implementación actual prioriza la estrategia Best-Fit:

- recorre todos los huecos libres,
- elige el más pequeño que pueda alojar el proceso,
- intenta minimizar el espacio sobrante.

Esto provoca un comportamiento realista de fragmentación, especialmente cuando hay varios huecos de distinto tamaño.

## Planificación de procesos

El simulador usa una política de CPU basada en SRTF (Shortest Remaining Time First):

- cada proceso tiene un tiempo restante de ejecución (`TIr`),
- en cada instante, el proceso listo con menor tiempo restante obtiene la CPU,
- si llega un proceso con menor tiempo restante, puede expropiar al actual.

Esta política favorece tiempos de ejecución más cortos y es útil para estudiar la dinámica de procesos de corta duración.

## Formato de entrada CSV

El lote de procesos se carga desde un archivo CSV. El parser acepta columnas con nombres en español o equivalentes, por ejemplo:

```csv
id,arribo,tam,irrupcion
P1,0,100,5
P2,2,50,3
P3,5,80,6
```

También se aceptan variantes como:

- `Proceso,TA,TI,Tamaño (K)`
- `id,t_arribo,tam,t_irrupcion;`

### Campos requeridos

- `id`: identificador único del proceso.
- `arribo`: instante de llegada al sistema.
- `tam`: tamaño del proceso en KB.
- `irrupcion`: tiempo de CPU requerido.

### Validaciones

Se descartan automáticamente procesos con:

- identificador duplicado,
- tamaño no positivo,
- irrupción no positiva,
- valores no numéricos,
- tamaño mayor que la memoria disponible,
- filas incompletas.

## Ejecución

### Opción 1: ejecutar desde la terminal

Desde la carpeta del proyecto:

```bash
cd simulador_modificado
python main.py
```

### Opción 2: usar la interfaz del programa

```bash
cd simulador_modificado
python interfaz.py
```

### Opción 3: ejecutar pruebas unitarias

```bash
cd simulador_modificado
python -m unittest Test -v
```

## Flujo de ejecución

Cuando se ejecuta el simulador:

1. Se solicita seleccionar o ingresar un archivo CSV.
2. El sistema lee la lista de procesos.
3. Los procesos se van incorporando a la simulación por instantes de tiempo.
4. El planificador decide qué proceso entra en CPU.
5. Se actualiza la memoria y los estados.
6. El sistema muestra el estado actual en cada evento importante.
7. Al finalizar, genera un informe estadístico.

## Salidas del simulador

El programa imprime varias tablas por consola, por ejemplo:

- procesos nuevos,
- tabla de particiones,
- estado de la memoria,
- cola de listos,
- cola de listos/suspendidos,
- información final por proceso,
- métricas de rendimiento.

### Métricas reportadas

- retorno original,
- retorno efectivo,
- espera original,
- espera efectiva,
- rendimiento promedio,
- fragmentación externa máxima y promedio.

Estas métricas permiten comparar el comportamiento del sistema cuando un proceso tarda más en entrar a memoria o cuando el espacio disponible está fragmentado.

## Ejemplo de uso

Supongamos un lote como este:

```csv
id,arribo,tam,irrupcion
A,0,120,5
B,1,80,3
C,3,40,2
D,4,90,4
```

Al ejecutarlo, el simulador:

- valida cada proceso,
- intenta asignarlos a memoria,
- ordena ejecución según el tiempo restante,
- informa cuándo un proceso entra a memoria y cuándo termina,
- calcula métricas finales.

## Dependencias

El proyecto usa únicamente la biblioteca estándar de Python, en particular:

- `csv`
- `tkinter`
- `unittest`
- `os`
- `textwrap`
- `unicodedata`

No requiere paquetes externos adicionales.

## Estado del proyecto

Este repositorio corresponde a un trabajo académico/práctico de sistema operativo orientado a la simulación de memoria y planificación. Está diseñado como herramienta didáctica para estudiar:

- administración de memoria,
- políticas de asignación,
- fragmentación,
- planificación de procesos,
- análisis de rendimiento y tiempos.

## Créditos

El proyecto incluye la siguiente autoría en la interfaz de menú:

- Benitez, Francisco Ezequiel
- Cardozo, Lucas Tisiano
- Gomez, Bastacini Guido
- Halier, Fiorella Estefania
- Lavia Ferrero, Matias Daniel
- Ramirez, Zahira Nahir
- Sosa, Tomás

## Licencia

No se especifica una licencia en este repositorio. Si deseas reutilizar o distribuir el proyecto, conviene consultar primero con los autores o revisar si existe un archivo de licencia en el origen del repositorio.

## Recomendaciones

- Utiliza lotes CSV pequeños para observar el comportamiento paso a paso.
- Experimenta cambiando el orden de llegada y tamaña de los procesos.
- Compara resultados con distintos patrones de carga para analizar fragmentación.
- Revisa el módulo `Test.py` para entender mejor las reglas del simulador y sus casos de prueba.

## Conclusión

Este proyecto ofrece una vista práctica y didáctica sobre cómo un sistema operativo gestiona la memoria y la CPU. Es especialmente útil para comprender conceptos de:

- particiones variables,
- fragmentación externa,
- decisiones de asignación,
- suspensiones por falta de memoria,
- algoritmos de planificación.

Si quieres ampliar este simulador, una siguiente mejora natural sería incluir otras políticas de colocación como First-Fit y Worst-Fit, además de más estadísticas y una interfaz gráfica más completa.

---

Desarrollado como simulador académico de gestión de memoria en Python.
