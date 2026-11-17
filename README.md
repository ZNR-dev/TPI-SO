# Simulador de gestión de memoria y planificación de procesos

Proyecto académico desarrollado en Python para estudiar la administración de memoria principal con particiones variables y la planificación de procesos en un sistema operativo. La implementación combina asignación de memoria **Best-Fit** con planificación de CPU **SRTF (Shortest Remaining Time First)** y permite observar, paso a paso, la admisión, suspensión, ejecución y finalización de un lote de procesos.

## Objetivos académicos

El simulador sirve como apoyo para analizar y relacionar los siguientes conceptos:

- particiones variables y administración dinámica de memoria;
- estrategias de selección de huecos libres;
- fragmentación externa y unión de particiones;
- admisión, suspensión y reanudación de procesos;
- planificación expropiativa de CPU;
- tiempos de retorno, espera y rendimiento del sistema.

## Modelo del sistema

Los parámetros se definen en `simulador_modificado/config.py`:

| Parámetro | Valor | Descripción |
| --- | ---: | --- |
| Memoria reservada para el SO | 100 K | Zona fija que no se asigna a procesos de usuario. |
| Memoria de usuario | 450 K | Capacidad disponible para procesos. |
| Granularidad de asignación | 10 K | Cada solicitud se redondea al siguiente múltiplo de 10 K. |
| Máximo de procesos admitidos en el sistema | 5 | Cuenta los procesos en ejecución, listos y listos/suspendidos. |
| Máximo de procesos válidos por lote | 10 | Las filas posteriores al límite se ignoran. |

Las unidades `K` corresponden a las unidades empleadas por el modelo del proyecto; no se realiza conversión entre K, KB u otras unidades.

### Asignación y liberación de memoria

La memoria de usuario se representa mediante una lista enlazada cuyos bloques están ordenados por dirección. La política Best-Fit examina los huecos libres y selecciona el de menor tamaño que pueda satisfacer la solicitud. Si el hueco es mayor que la asignación requerida, se divide y el espacio restante se conserva como bloque libre.

El tamaño solicitado se redondea hacia arriba a múltiplos de 10 K. Por ejemplo, un proceso que solicita 149 K ocupa 150 K. Al terminar el proceso, su bloque se libera; si los bloques contiguos anterior o siguiente también están libres, se fusionan.

Si hay procesos esperando que no caben en ningún hueco individual, pero sí cabrían en la suma de los huecos libres no contiguos, el simulador registra fragmentación externa. La medida informada corresponde al total de memoria libre fragmentada cuando existe al menos un proceso suspendido afectado según ese criterio.

### Planificación de CPU

La CPU se planifica con SRTF, una variante expropiativa de SJF. En cada instante se selecciona entre los procesos listos el que tenga menor tiempo de CPU restante. Un proceso listo expropia al proceso en ejecución únicamente si su tiempo restante es **estrictamente menor**; en caso de igualdad, el actual conserva la CPU.

Para ordenar los procesos listos se usa el criterio `(tiempo restante, instante de arribo, identificador)`, lo que establece desempates deterministas entre candidatos.

### Ciclo de simulación

En cada instante se realizan estas etapas, en orden:

1. Se reciben los procesos cuyo instante de arribo ya se alcanzó.
2. Se intenta reanudar procesos listos/suspendidos, que tienen prioridad sobre los nuevos.
3. Se admiten procesos nuevos mientras haya capacidad según el límite del sistema; si no hay un hueco suficiente, quedan listos/suspendidos.
4. Se selecciona o, cuando corresponde, se expropia el proceso de CPU.
5. Se avanza una unidad de tiempo y se descuenta una unidad de CPU al proceso en ejecución.
6. Si un proceso termina, se libera su memoria y se registra su finalización.
7. Se muestrea la fragmentación externa.

## Estructura del repositorio

```text
TPI-SO/
├── README.md
└── simulador_modificado/
    ├── config.py          # parámetros globales del modelo
    ├── entrada.py         # lectura y validación de lotes CSV
    ├── interfaz.py        # menú principal por consola
    ├── lista.py           # estructura de lista enlazada
    ├── main.py            # selección del lote y ejecución
    ├── memoria.py         # asignación, liberación y fragmentación
    ├── planificador.py    # ciclo de simulación y planificación SRTF
    ├── proceso.py         # modelo y estado de cada proceso
    ├── salida.py          # visualización de eventos e informe final
    ├── Test.py            # pruebas unitarias
    ├── prueba1.csv ... prueba6.csv
    ├── interfaz.spec      # configuración de PyInstaller
    └── interfaz.exe       # ejecutable incluido en el repositorio
```

La carpeta también contiene artefactos generados (`build/` y `__pycache__/`). No son necesarios para ejecutar el proyecto desde el código fuente.

## Requisitos

- Python 3.10 o posterior recomendado.
- Tkinter disponible para utilizar el selector gráfico de archivos. En algunas distribuciones de Linux puede requerir la instalación de un paquete del sistema independiente de Python.
- No se requieren dependencias de terceros para ejecutar el simulador o sus pruebas.

## Instalación y ejecución

Clona el repositorio y entra en el directorio del programa:

```bash
git clone https://github.com/ZNR-dev/TPI-SO.git
cd TPI-SO/simulador_modificado
```

Inicia el menú principal:

```bash
python interfaz.py
```

Desde el menú se puede iniciar una simulación, consultar los créditos o salir. Al iniciar, se ofrece seleccionar el archivo CSV escribiendo su ruta o mediante una ventana del explorador de archivos.

También es posible ejecutar directamente el flujo de selección y simulación, sin el menú principal:

```bash
python main.py
```

El programa muestra el estado del sistema en los eventos relevantes y solicita pulsar **Enter** para continuar entre estados. Al finalizar la ejecución, presenta el informe estadístico.

## Formato del lote CSV

El archivo debe ser CSV delimitado por comas. La primera fila se interpreta como encabezado; los nombres de campo se normalizan para ignorar mayúsculas, acentos, espacios y signos de puntuación. Un formato recomendado es:

```csv
id,arribo,tam,irrupcion
P1,0,100,5
P2,2,50,3
P3,5,80,6
```

Los campos requeridos son:

| Campo | Descripción | Restricción |
| --- | --- | --- |
| `id` | Identificador del proceso. | Obligatorio y único dentro del lote. |
| `arribo` | Instante de llegada al sistema. | Entero no negativo. |
| `tam` | Memoria solicitada en K. | Entero positivo; no puede superar los 450 K de memoria de usuario. |
| `irrupcion` | Tiempo total de CPU requerido. | Entero positivo. |

También se reconocen encabezados como `Proceso,TA,TI,Tamaño (K)` y `id,t_arribo,tam,t_irrupcion`. Cuando no se reconoce un encabezado completo, se utiliza el orden de columnas `id, arribo, tamaño, irrupción`.

Las filas vacías se ignoran. Las filas con datos faltantes, valores no enteros o fuera de rango, identificadores repetidos o solicitudes que exceden la memoria de usuario se descartan con un aviso. El programa procesa como máximo diez procesos válidos por lote.

## Salida y métricas

Durante la simulación se muestran eventos, el proceso en CPU, la cola de nuevos, el mapa de particiones y las colas de listos y listos/suspendidos. La tabla de memoria incluye la zona reservada al SO y los bloques de usuario con sus direcciones.

El informe final presenta por proceso y en promedio:

- **Retorno original:** instante de finalización menos instante de arribo.
- **Retorno efectivo:** instante de finalización menos primer instante de entrada a memoria.
- **Espera original:** retorno original menos tiempo de CPU requerido.
- **Espera efectiva:** retorno efectivo menos tiempo de CPU requerido.
- **Rendimiento:** cantidad de procesos terminados dividida por el tiempo total de simulación, expresada en trabajos por unidad de tiempo.
- **Fragmentación externa máxima y promedio:** valores registrados durante los instantes de la simulación.

El arribo efectivo permite distinguir el tiempo transcurrido desde la llegada al sistema del transcurrido desde la primera admisión en memoria. Las magnitudes temporales se expresan en unidades de tiempo del modelo.

## Pruebas

Desde el directorio `simulador_modificado/`, ejecuta:

```bash
python -m unittest Test -v
```

La suite incluye pruebas de la asignación Best-Fit, fusión de huecos libres, fragmentación externa, límite de procesos admitidos, suspensión y reanudación, planificación SRTF y validación de archivos CSV.

## Créditos

Autores que aparecen en la interfaz del proyecto:

- Benitez, Francisco Ezequiel
- Cardozo, Lucas Tisiano
- Gomez, Bastacini Guido
- Halier, Fiorella Estefania
- Lavia Ferrero, Matias Daniel
- Ramirez, Zahira Nahir
- Sosa, Tomás


## Posibles extensiones

Como trabajo futuro, el simulador podría ampliarse con implementaciones alternativas de First-Fit y Worst-Fit para comparar estrategias bajo los mismos lotes, además de ampliar la cobertura de pruebas o incorporar visualizaciones gráficas de la evolución de la memoria.
