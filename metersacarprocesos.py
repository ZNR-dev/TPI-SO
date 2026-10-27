#pruebas de lista para gestion de memoria  
class nodo():  #aunque se contradigan los nombres, nodo es el proceso a pelo, proc es el nodo para la lista
    def __init__(self,valor,id):
        self.tam=valor
        self.id=id

class proc(nodo):
    def __init__(self, valor,id,dir):
        super().__init__(valor,id)
        self.est=False #False:libre True:ocupado
        self.inicio=None #donde comienza el proc en la memoria o algo asi
        self.prox=dir         

class listaenlazada():
    prim:proc
    def __init__(self):
        self.prim=proc(None,None,None)
        self.tamanio= 500

    def meter_proc(self, coso:nodo):
        p=proc(None,None,None)
        q=proc(None,None,None)
        aux1=proc(None,None,None)
        aux2=proc(None,None,None)
        hv=10000 #HV para best fit
        if (self.prim.inicio==None):
            self.prim.est=True
            self.prim.id=coso.id
            self.prim.tam=coso.tam
            self.prim.inicio=0
            self.prim.prox=p
            p.id=None
            p.est=False
            p.prox=None
            p.inicio=self.prim.tam
            p.tam=(self.tamanio - coso.tam)
            self.tamanio=(self.tamanio - coso.tam )
        else:
            p=self.prim

            while (p!=None): #se recorre toda la lista
                while ((coso.tam>p.tam) or (p.est==True)) and (p.prox!=None): 
                    q=p
                    p=p.prox 
                if ((p.tam - coso.tam) < hv) and (p.est==False):
                    aux1=p
                    aux2=q
                    hv= p.tam - coso.tam  #espacio sobrante luego de la colocacion del proceso, se usa para comparar con otras particiones
                q=p
                p=p.prox


            q=aux2
            p=aux1 #no hace falta resetear porque despues todo se termina sobreescribiendo
            aux1=proc(None,None,None)
            aux2=proc(None,None,None)
            if (p!=None):
                if (p.prox==None): #caso, se ubica en el ultimo nodo de la lista
                    if (p.tam==coso.tam):
                        p.est=True
                        p.id=coso.id
                        self.tamanio= self.tamanio - coso.tam 
                    else:    
                        aux1.est=True
                        aux1.inicio=(p.inicio)
                        aux1.tam=coso.tam
                        aux1.prox=p
                        aux1.id=coso.id
                        p.inicio=(p.inicio + coso.tam)
                        p.tam= p.tam-coso.tam  
                        q.prox=aux1
                        self.tamanio= self.tamanio - coso.tam

                elif (p==self.prim): #se ubica en el primero
                    if (p.tam==coso.tam):
                        p.est=True
                        p.id=coso.id
                        self.tamanio= self.tamanio - coso.tam 
                    else:
                        q.prox=self.prim
                        q.tam=coso.tam
                        q.est=True
                        q.inicio=(p.inicio)
                        q.id=coso.id
                        self.prim=q
                        p.inicio(p.inicio + coso.tam)
                        p.tam= (p.tam - coso.tam)
                        self.tamanio= self.tamanio - coso.tam
                else: #se ubica en algun lugar del medio
                    if (p.tam==coso.tam):
                        p.est=True
                        p.id=coso.id
                        self.tamanio=self.tamanio - coso.tam
                    else:
                        aux1.id=coso.id
                        aux1.est= True
                        aux1.tam= coso.tam
                        aux1.inicio=(p.inicio)
                        aux1.prox=p
                        p.inicio= p.inicio + coso.tam
                        p.tam= p.tam - coso.tam
                        q.prox= aux1
                        self.tamanio= self.tamanio - coso.tam 
            else: 
                print("\n no hay memoria disponible para el proceso para el proceso", coso.id )

    def desalojo(self,aid):
        q=proc(None,None,None)
        p=proc(None,None,None)
        p=self.prim
        while ((p.id!=aid) and (p!=None)):
            q=p
            p=p.prox
        if (p!=None):
            if (p==self.prim):
                self.prim.id=None
                self.prim.est=False
                self.tamanio= self.tamanio + self.prim.tam
                if (self.prim.prox.est==False): #se buscará unir dos particiones libres en memoria
                    self.prim.tam= self.prim.tam + self.prim.prox.tam
                    self.prim.prox= self.prim.prox.prox
            elif (p.prox==None):
                p.id=None
                p.est=False
                self.tamanio= self.tamanio + p.tam
                if (q.est==False):
                    q.tam=q.tam + p.tam
                    q.prox=None 
            else:
                p.id=None
                p.est=False
                self.tamanio= self.tamanio + p.tam
                if (q.est==False):
                    q.tam= q.tam + p.tam
                    q.prox=p.prox
                    p=q
                if (p.prox.est==False):
                    p.tam= p.tam + p.prox.tam
                    p.prox=p.prox.prox
        else:
            print("\n valor no encontrado en la lista de nuevo \n")

    def mostrar(self):
        p=proc(None,None,None)
        p=self.prim
        print("\n")
        while (p!=None):
            if (p.prox!=None):    
                print(f"id del proceso: {p.id}, estado:{p.est}, memoria del proc.:{p.tam}, proximo: {p.prox.id}")
                p=p.prox
            else:
                print(f"id del proceso: {p.id}, estado:{p.est}, memoria del proc.:{p.tam}, proximo: {p.prox}")
                p=p.prox
        print("\n")
#pruebas 
v1=nodo(20,1)
v2=nodo(75,2)
v3=nodo(150,3)
v4=nodo(100,4)
v5=nodo(90,5)
listo=listaenlazada()
listo.meter_proc(v1)
listo.meter_proc(v2)
listo.meter_proc(v3)
listo.meter_proc(v4)
listo.meter_proc(v5)
listo.mostrar()
listo.desalojo(3)
listo.desalojo(2)
listo.meter_proc(v1)
listo.mostrar()



















    
