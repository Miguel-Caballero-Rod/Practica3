# Práctica 3 de Programación Paralela: Juego Distribuido

#### Trabajo realizado por Manuel Pablo Bejarano Galeano, Miguel Caballero Rodríguez y Pedro Corral Ortiz-Coronado

## Descripción básica del juego:
Hay dos jugadores que pueden desplazar horizontalmente sus plataformas a lo largo de la mitad correspondiente de la pantalla, y deben hacer rebotar la pelota sin que toque el borde inferior con el objetivo de destruir todos los asteroides sin que se queden sin vidas. Un jugador pierde una vida cuando la pelota toca el borde inferior de la pantalla en la mitad en la que se encuentra el jugador. Para destruir los asteroides debe colisionar la pelota con ellos, y cualquier choque de la pelota con uno de los bordes o los asteroides hará que rebote cambiando la dirección de su movimiento.

## Ejecución del programa:
Los programas a ejecutar son: `salaFINAL.py` y `playerFINAL.py`. Para que se ejecuten correctamente, es necesario que el orden de ejecución sea el siguiente:

1. Se debe ejecutar en la terminal el archivo `salaFINAL.py` añadiendo como parámetro la ip del ordenador en el que se ejecute, que denominaremos ipSALA; i.e:  
```
python3  salaFINAL.py ipSALA
```
2. El siguiente paso es ejecutar en dos terminales diferentes, conectadas a una misma red, el archivo `playerFINAL.py` y como segundo parámetro poner, de nuevo, ipSALA. De esta manera, se consigue que los ordenadores se conecten a la sala, que será el nodo central en la ejecución del juego, pasando la información del jugador a la sala constantemente. Ejemplo de ejecución:   
```
python3  playerFINAL.py ipSALA
```

## Fin de la ejecución: 
Un juego puede terminar, por norma general, por una de las siguientes tres razones, o bien los jugadores han conseguido destruir todos los asteroides, en cuyo caso sale un mensaje felicitándoles por pantalla, o bien uno de los jugadores ha perdido su última vida restante, en cuyo caso sale un mensaje de derrota indicando el jugador perdedor, o bien se desea interrumpir el juego mediante la tecla *esc*, en cuyo caso se detiene inmediatamente la ejecución. Sin embargo, en todos los casos son los programas de los jugadores los que se interrumpirán, mientras que la terminal con la ejecución del programa sala seguirá en funcionamiento, esperando dos nuevos jugadores que se conecten a ella, comenzando un nuevo juego.
