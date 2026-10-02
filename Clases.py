
#Clases para las particiones
class Particion:
  def __init__(self,id_p,tam,dir,proc=None)
      self.id=id_p
      self.tam=tam
      self.dir=dir
      self.proc=proc
      self.frag= 0

  def esta_libre(self) -> bool:
      return self.proceso is None  #Permite saber de foma rapida si el nodo esta libre
  #funcion que muestra por pantalla los datos del proceso al q se le asigno un espacio
  def __repr__(self):
        id_proc = self.proceso.id if self.proceso else "LIBRE"
        return (f"Partición {self.id} | Dir: {self.direccion:03d}K | "
                f"Tam: {self.tamaño:03d}K | Proceso: {id_proc} | "
                f"Frag. Int: {self.fragmentacion_interna}K")

#Clases para los procesos
class Proceso:
    def __init__(self, id_proc,tam,ti,ta):
        self.id = id_proc
        self.tam = tam
        self.estado = "NUEVO"
        self.t_ar = ta
        self.t_ar_efec = 0
        self.t_ir = ti
        self.t_ir_falt = ti   #a este le resto -1 por cada tick de reloj(para aplicar SRTF)
        self.t_retorno = 0  #TR:T_Final-T_Arribo
        self.t_espera = 0  #TE: TR-T_ir
        self.t_final = 0
