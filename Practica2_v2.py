from time import sleep, time
from multiprocessing import Value, Lock, Condition, Process, Manager
from enum import Enum
import numpy as np
import random

class Tipos(Enum):
    CocheA = "Coche en dirección Norte"
    CocheB = "Coche en dirección Sur"
    Peaton = "Peatón"
    
    #Devuelve Tipos\self, el complementario de self en Tipos
    def no(self):
        return [e for e in Tipos if e!=self]
    
    def tiempo(tipo):
        if tipo == Tipos.CocheA or tipo == Tipos.CocheB:
            t=  [1, 0.5] # normal 1s, 0.5s
        else:
            t = [30, 10] # normal 1s, 0.5s
        return t

class Monitor():
    def __init__(self, tMax = 5):
        self.lock = Lock() #Candado para modificar los valores del número dentro del túnel (del tipo que sea)
        self.cond = {tipo: Condition(self.lock) for tipo in Tipos} #Condición para entrar al túnel de cada tipo
        self.num  = {tipo: Value('i',0)         for tipo in Tipos} #Número de cada tipo que está dentro del túnel, Empieza en 0, está vacío             
        self.numEspera  = {tipo: Value('i',0)         for tipo in Tipos} #Número de cada tipo que está esperando, Empieza en 0, está vacío      
        self.tiempoT  = Value('d', time())   #Tiempo que lleva ocupado el Túnel, Empieza en 0, no hay nadie
        self.ultEnPasar  = {tipo: Value('i',0)         for tipo in Tipos}  #1 el que ha sido el último en pasar, 0 el resto, Empieza en 0, no ha pasado nadie
        self.tMax     = tMax #Ventana de tiempo en la que se deja pasar a los de un tipo desde que entra el primero (para evitar inanición)
    
    #Cuando llega al túnel, se espera a que los otros salgan del túnel (si es que hay alguno) y se añade uno al número de este tipo dentro
    #@post: self.num[nt].value = 0 para nt en tipo.no() (Todos los tipos que no son tipo)
    #       self.num[tipo].value > 0
    #       self.ultEnPasar[nt].value = 0 para nt en tipo.no() (Todos los tipos que no son tipo)
    #       self.ultEnPasar[tipo].value = 1
    def esperaEntrar(self, tipo: Tipos):
        with self.lock: #Evita que el valor del número que hay dentro se modifique simultaneamente (y se necesita para esperar)
            self.numEspera[tipo].value += 1    
            self.cond[tipo].wait_for(lambda: [self.num[nt].value for nt in tipo.no()].count(0) == (len(Tipos)-1) and (self.ultEnPasar[tipo].value  == 0 or (time()-self.tiempoT.value) < self.tMax or [self.numEspera[nt].value for nt in tipo.no()].count(0) == (len(Tipos)-1)))#Espera a que el valor dentro de los otros tipos sea 0 y ,si es el tipo que está en el túnel, comprueba que lleve menos del tiempo máximo
            #Invariante: El número dentro del túnel de los otros tipos será 0
            self.numEspera[tipo].value -= 1  
            if self.ultEnPasar[tipo].value  == 0 or [self.numEspera[nt].value for nt in tipo.no()].count(0) == (len(Tipos)-1):
                self.tiempoT.value = time()
                for t in Tipos:
                    self.ultEnPasar[t].value = (t == tipo)
            self.num[tipo].value += 1 #Añade 1 al número de este tipo en el túnel

    #Cuando termine de cruzar el tunel, se resta 1 al número de este tipo de los que hay dentro y se notifica al resto de tipos
    #@pre: self.num[tipo].value > 0
    def sale(self, tipo: Tipos): 
        with self.lock: #Evita que el valor del número que hay dentro se modifique simultaneamente (y se necesita para notificar)
            self.num[tipo].value -= 1 #Resta 1 al número de este tipo en el túnel       
            for nt in tipo.no(): #Notifica al resto de tipos
                self.cond[nt].notify_all()

class Vehiculo():
    def __init__(self, tipo: Tipos, pid: int, monitor: Monitor, tiempo: int):
        self.tipo    = tipo
        self.pid     = pid
        self.monitor = monitor
        self.tiempo  = tiempo

    #Proceso para esperar a poder entrar en el túnel y pasar
    def entrarTunel(self):
        print(f"{self.tipo.name} {self.pid} esperando", flush = True)
        self.monitor.esperaEntrar(self.tipo)
        print(f"Entrando {self.tipo.name} {self.pid}", flush = True)
        sleep(self.tiempo)
        print(f"Saliendo {self.tipo.name} {self.pid}", flush = True)
        self.monitor.sale(self.tipo)

#Genera aleatoriamente la cantidad dada de los tipos, a los que deja intentar entrar en el tunel con una separacion de variable exponencial tiempo, Estos tipos están en el túnel un tiempo condicionado por la distribución nomal dada por t = (media, desviación típica)
def generaTipo(tipos: list, cantidad: int, tiempo: int, monitor: Monitor, t: list):    
    pid = [0] * len(tipos)
    plst = []
    s = np.random.normal(t[0], t[1], cantidad) #Sacamos las muestras que necesitamos de la distribución normal, para tener el tiempo que estará cada vehículo en el túnel
    for i in range(cantidad):
        num = random.randint(0, len(tipos)-1)
        pid[num] += 1 #Sumamos al contador del tipo que vamos a generar
        p = Process(target=Vehiculo(tipos[num], pid[num], monitor, abs(s[i])).entrarTunel, args=()) #Creamos el procesos de pasar al tunel
        p.start()
        plst.append(p)
        sleep(0 if i == (cantidad-1) else random.expovariate(1/tiempo)) #Esperamos antes de crear un nuevo vehículo

    for p in plst:
        p.join()
            
def main():
    monitor = Monitor()
    gcars = Process(target=generaTipo, args=([Tipos.CocheA, Tipos.CocheB], 100, 0.5, monitor, Tipos.tiempo(Tipos.CocheA))) #Creamos el proceso para generar los coches
    gped = Process(target=generaTipo, args=([Tipos.Peaton], 10, 5, monitor, Tipos.tiempo(Tipos.Peaton))) #Creamos el proceso para generar los peatones
    gcars.start()
    gped.start()
    gcars.join()
    gped.join()
                                       
if __name__ == "__main__":
    main()
