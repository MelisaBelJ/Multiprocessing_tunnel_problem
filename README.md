# Practica2

Quieren entrar al túnel coches y peatones. Cuando entran coches, solo pueden pasar en una dirección. Sin embargo, cuando pasan los peatones pueden pasar en ambos sentidos.

De cara a la implementación esto se traduce en que los peatones se ven como un tipo, y los coches con su dirección como otro (3 tipos en total).

Si se quisieran añadir más actores solo sería necesario modificar la enumeración con los tipos para que los incluyera y crear los procesos en el main.

## Practica2_v1

Versión básica, asegura que no hay deadlock, pero no evita la inanición. Como tardan mucho más en pasar los peatones, una vez entra uno pasan todos, y los coches se quedan esperando.

## Practica2_v2

Para evitar la inanición se añade un temporizador. Cuando los de un tipo llevan más del tiempo máximo definido, no se dejan pasar a más, aunque siga en uso por ese tipo el túnel (Se ha definido el máximo por defecto en 5).
