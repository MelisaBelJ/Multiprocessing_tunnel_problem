from time import sleep
from multiprocessing import Value, Lock, Condition, Process
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
            t = [0, 10] # normal 1s, 0.5s
        return t

class Monitor():
    def __init__(self):
        self.lock = Lock() #Candado para modificar los valores del número dentro del túnel (del tipo que sea)
        self.cond = {tipo: Condition(self.lock) for tipo in Tipos} #Condición para entrar al túnel de cada tipo
        self.num  = {tipo: Value('i',0)         for tipo in Tipos} #Número de cada tipo que está dentro del túnel, Empieza en 0, está vacío
    
    #Cuando llega al túnel, se espera a que los otros salgan del túnel (si es que hay alguno) y se añade uno al número de este tipo dentro
    def esperaEntrar(self, tipo: Tipos):
        with self.lock: #Evita que el valor del número que hay dentro se modifique simultaneamente (y se necesita para esperar)
            self.cond[tipo].wait_for(lambda: [self.num[nt].value for nt in tipo.no()].count(0) == 2) #Espera a que el valor dentro de los otros tipos sea 0
            #Invariante: El número dentro del túnel de los otros tipos será 0
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

def generaTipo(tipos: list, cantidad: int, tiempo: int, monitor: Monitor, t: list):    
    pid = [0] * len(tipos)
    plst = []
    s = np.random.normal(t[0], t[1], cantidad)
    for i in range(cantidad):
        num = random.randint(0, len(tipos)-1)
        pid[num] += 1
        p = Process(target=Vehiculo(tipos[num], pid[num], monitor, abs(s[i])).entrarTunel, args=())
        p.start()
        plst.append(p)
        sleep(random.expovariate(1/tiempo))

    for p in plst:
        p.join()
        
def prueba():
    N  = {Tipos.CocheA: 50, Tipos.CocheB: 50, Tipos.Peaton: 10} #10 coches en dir A, 10 coches en dir B, 20 peatones
    monitor  = Monitor()
    v = {Vehiculo(t, pid, monitor) for t in Tipos for pid in range(N[t])} #Crea los objetos vehículo que pasarán por el túnel, Se meten en un set para que no estén ordenados, no lleguen seguidos los de cada tipo
    for aux in v: #Crea e inicia los procesos
        p = Process(target = aux.entrarTunel, args=()) 
        p.start()
        sleep(1.5) #Se da algo de tiempo entre procesos para que no lleguen todos de golpe
        
def main():
    monitor = Monitor()
    gcars = Process(target=generaTipo, args=([Tipos.CocheA, Tipos.CocheB], 100, 0.5, monitor, Tipos.tiempo(Tipos.CocheA)))
    gped = Process(target=generaTipo, args=([Tipos.Peaton], 10, 5, monitor, Tipos.tiempo(Tipos.Peaton)))
    gcars.start()
    gped.start()
    gcars.join()
    gped.join()
                                       
if __name__ == "__main__":
    main()
