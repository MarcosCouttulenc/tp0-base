# Informe de trabajo practico 0 - Marcos Couttulenc

## Protocolo de comunicacion entre Client - Server

Para realizar este trabajo escogi un protocolo de texto, el cual envia mensajes compuesto por campos de texto, los cuales se separan por un
caracter especial, un salto de linea. Los mensajes culminan con un doble salto de linea, y comienzan con un primer parametro que indica el tipo de mensaje.

La interaccion entre un cliente y servidor desde que se conecta hasta que se desconecta es la siguiente:

### CONEXION

Mediante socket.accept

### ENVIO DE APUESTAS

El cliente comienza a mandar mensajes de tipo "BET" con las apuestas que lee de su archivo de data. Cada apuesta tiene un total de 6 parametros. El cliente puede
enviar una cantidad maxima de apuestas por mensaje. Este mensaje constara de todas las apuestas, una detras de otra, y cadaapuesta consta de sus parametros,
unos atras de otros, separados por un salto de linea. El final del batch se marca con un doble salto de linea.

"BET\n(param1bet1)\n(param2bet1)\n(...)\n(param6bet1)\n(param1bet2)\n(param2bet2)\n(...)\n(param6bet2)\n(...)\n(param1betN)\n(param2betN)\n(...)\n(param6betN)\n\n"

El server contesta con un mensaje: "Success :) " en caso de que haya leido correctamente las bets, o "Error al recibir msg :(" en caso de que no suceda.

En la version de la parte 2 donde el server acepta solo una conexion por vez, el cliente envia un batch, espera la respuesta del server y se desconecta. Luego de eso se vuelve a conectar para repetir la interaccion. Esto se realiza de esta manera para que todas las agencias puedan ir enviando mensajes de manera mas pareja, sino enviarian todas las apuestas juntas (de a mensajes separados pero uno atras de otro) dejando en espera a las demas.

En la version de la parte 3 donde el server acepta varias conexiones a la vez, el cliente envia un batch atras de otro (siempre esperando la respuesta), ya que el server esta manejando a cada cliente en un proceso aparte y no estaria trabando a las demas agencias de esta manera.

### CONFIRMACION

El cliente le envia una confirmacion de que ya termino de enviar todas sus apuestas con un mensaje: 

"CONFIRMATION\n(agency_ID)\n\n"

El server contesta con un mensaje: "OK"

### ESPERA DE RESULTADOS

En la version de la parte 2 donde el server acepta solo una conexion por vez, el cliente envia un mensaje:

"WINNERS\n(agency_ID)\n\n"

si el server no recibio las confirmaciones de todas las agencias, corta su comunicacion con este cliente, lo que hace que el mismo se duerma por un lapso de tiempo y vuelva a intentar pedir los ganadores. Asi hasta que todas las agencias hayan terminado de enviar sus apuestas y el server le conteste:

"(dniWinner1)\n(dniWinner2)\n(...)\n(dniWinnerN)\n\n"


En la version de la parte 3 donde el server acepta varias conexiones a la vez, el cliente envia el mismo mensaje:

"WINNERS\n(agency_ID)\n\n"

y se queda esperando una respuesta del server, el cual le respondera recien cuando todas las agencias hayan cofnirmado que enviaron todas las apuestas. Una vez que eso suceda, le contesta a ese mensaje con el mismo que el caso anterior:

"(dniWinner1)\n(dniWinner2)\n(...)\n(dniWinnerN)\n\n"


## Mecanismos de sincronizacion utilizados para la parte 3

Para que el server pueda manejar a varios clientes a la vez, utilice los metodos de multiproccessing de la libreria de python. Estos procesos fueron sincronizados con los siguientes metodos:

### Lock

Todos los procesos comparten un recurso, el log de las apuestas. En el se guardan las apuestas entrantes y sobre el se consulta para devolver los ganadores. Necesita que este a salvo de race conditions, por lo que le coloque un lock al recurso. Es decir, un proceso toma el lock y utiliza el recurso. Si otro proceso quiere tomar el recurso al mismo tiempo que ya esta siendo tomado, no podra hacerlo hasta que el proceso original suelte el lock.

### Barrier

Una vez que un cliente termino de enviar sus apuestas, envia una confirmacion de que termino. Seguido a eso, le envia una peticion para que el server le envie los ganadores del sorteo. El server no puede contestarle hasta que todos los clientes hayan confirmado que terminaron de enviar sus apuestas, por lo que implemento una barrera luego de esta confirmacion. Esta barrera frena la ejecucion de los procesos cuando llegan a ella, y los libera solo cuando todos los procesos llegan a ese punto.