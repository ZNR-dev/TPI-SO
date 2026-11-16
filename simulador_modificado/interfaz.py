"""Menú principal del simulador: iniciar, créditos o salir."""
from main import ejecucion
opc=0

def asignar_valor():
  """Pide un número por consola y repite si el usuario escribe otra cosa."""
  while True:
    try:
      return int(input())
    except ValueError:
      print("opción no existe, por favor reintente con alguna de las opciones en pantalla\n")
      opciones()

def opciones():
  """Muestra las opciones disponibles."""
  print("\n por favor, ingrese una de las opciones para continuar \n")
  print("1. Iniciar con el simulador")
  print("2. Créditos")
  print("3. Cerrar programa")


print(f"\n BIENVENIDO AL SIMULADOR \n")
opciones()
opc = asignar_valor()
val=False
while (val==False):
  if (opc==1):
    ejecucion()                    # selección de archivo + simulación
    print("\ndesea probar algo mas?")
    opciones()
    opc = asignar_valor()
    
  elif (opc==2):
    print(" Autores:Benitez, Francisco Ezequiel\n" \
    "Cardozo, Lucas Tisiano\n" \
    "Gomez, Bastacini Guido\n" \
    "Halier, Fiorella Estefania\n"\
    "Lavia Ferrero, Matias Daniel\n" \
    "Ramirez, Zahira Nahir\n"\
    "Sosa, Tomás\n"
    )
    print("\ndesea probar algo mas?\n")
    opciones()
    opc = asignar_valor()
    
  elif (opc==3):
    break                          # cierra el programa

  else:   
    print("opción no existe, por favor reintente con alguna de las opciones en pantalla\n")
    opciones()
    opc = asignar_valor()
