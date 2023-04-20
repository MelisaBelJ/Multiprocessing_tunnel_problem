# Practica 2

Quieren entrar al túnel coches y peatones. Cuando entran coches, solo pueden pasar en una dirección. Sin embargo, cuando pasan los peatones pueden pasar en ambos sentidos.

De cara a la implementación esto se traduce en que los peatones se ven como un tipo, y los coches con su dirección como otro (3 tipos en total).

Si se quisieran añadir más actores solo sería necesario modificar la enumeración con los tipos para que los incluyera y crear los procesos en el main.

Para simular la entrada de un vehículo al túnel se crea un objeto Vehiculo con si tipo, id, el objeto Monitor que comparten todos los que entran a un túnel y el tiempo que tarda en pasar el túnel. La clase Vehículo tienen una única función: entrarTunel, que simula la entrada al túnel del vehículo, delegando en el monitor la gestión de la entrada y la salida.

El monitor cuenta con una condición para cada tipo de vehículo, que controla si se les permite o no pasar, y un valor entero con la cantidad de cada tipo en el túnel. Una explicación más en detalle del funcionamiento de cada función en cada versión, de los invariantes y del porqué no se producen deadlocks se puede encontrar en el pdf: _Practica2_Funcionamiento.pdf_

## Practica2_v1

Versión básica, asegura que no hay deadlock, pero no evita la inanición. Como tardan mucho más en pasar los peatones, una vez entra uno pasan todos, y los coches se quedan esperando.

## Practica2_v2

Para evitar la inanición se añade un temporizador. Cuando los de un tipo llevan más del tiempo máximo definido, no se dejan pasar a más, aunque siga en uso por ese tipo el túnel (Se ha definido el máximo por defecto en 5).

Como puede causar deadlock cuando solo queda un tipo por pasar se ha añadido un contador de cantidad en espera para cada tipo. De esta forma, si la cantidad en espera del resto de tipos es 0, seguirán pasando los del que ha excedido su tiempo, hasta que haya alguno en espera de los otros o no quede ninguno más.
