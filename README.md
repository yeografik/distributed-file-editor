# distributed-file-editor

Se eligió como proyecto final de aprobación la creacion un sistema distribuido para la
edicion en tiempo real de archivos.

## Autores

**Gonzalez Ignacio - Nolasco Agustin**

### Requirements

Tener instalada python3.8 o una version mas nueva. Tener instalado y actualizado pip3.

### Setup

`pip3 install virtualenv`

`virtualenv venv`

`source venv/bin/activate`

`pip3 install -r requirements.txt`

De aqui en mas siempre se debera ingresar al ambiente virtual para
utilizar el sistema.

### How to use

0. Pararse en el directorio ```src```
1. En el archivo ```nodes.js``` se encuentra la informacion
acerca de los nodos que conforman la red. Esta puede ser modificada
segun se requiera para agregar o quitar nuevos nodos.
2. Una vez seteado los nodos de la red se puede proceder a
iniciarlos ejecutando ```python3 server.py [ip] [port]```, por ejemplo 
```python3 server.py localhost 5001```. Este proceso puede repetirse para
cada uno de los nodos definidos en ```nodes.js```.
3. Una vez levantados los nodos deseados se puede proceder a realizar conexion
de la aplicacion con alguno de los mismos, para ellos se debera ejecutar 
```python3 client.py [ip] [port]```, por ejemplo ```python3 client.py localhost 5001```

Nota: los nodos pueden irse levantando mientras se va usando la aplicacion, 
lo importante es que siempre exista al menos uno para que los usuarios de 
la aplicacion pueda conectarse a el. Pero a medida que haya más nodos
conectados los usuarios de la aplicacion podran conectarse a los distintos
nodo y editar en conjunto el contenido del documento.

## Decisiones de implementacion

* Se optó de momento por la edición de un único archivo.
Para la edicion de multiples archivos simplemente bastaría con
solicitar un archivo especifico a partir de la aplicación, y, en
caso de que no existe, crearlo. Por cuestiones de simplicidad
es que se ha tomado esta decisión.
* Cuando se inicia un nuevo nodo este se presenta ante aquellos
que ya forman parte de la red para que estos pueda registrarlo
un nodo activo, mientras que el nodo en cuestión registra como
nodos activos a todos aquellos que le respondan.
  * Durante este proceso el nodo, en caso de que no sea el primer
  nodo de la red, solicita la información del documento a todos los
  nodos de la red, mientras que estos esperando a la respuesta del
  nuevo nodo, el nuevo nodo se queda con la informacion del nodo
  que tenga la version mas actializada del documento, de esta forma
  garantizamos que la red no sigue su curso mientras un nodo se conecta
  y ademas, el nuevo nodo conectado tiene la informacion mas reciente
  * En caso de que este sea el primer nodo de la red, la información será 
  levantada de un archivo local, en caso de existir, sino será creado.
* Los nodos tienen la capacidad de detectar cuando otro esta caido, esto
se hace durante algun envio de mensaje, si este falla entonces se considera
al nodo receptor como caido.
* Para realizar broadcasting se crea un nuevo thread que maneja una cola
mientras esa cola este vacia el thread estara a la espera de que algun
comando a ser envia por broadcast sea agregado a la misma.
* El servidor puede recibir diversos mensajes, entre ellos la ejecucion de
un comando, que puede provenir de un cliente (`client.py`) o de otro servidor
por medio de un broadcast. En caso de que el mensaje sea de un client, el
comando sera ejecutado localmente para luego ser agregado a la cola de broadcasting,
el cual enviara dicho comando a todos sus nodos vecinos. En caso de que el comando 
recibido provenga de un vecino (`server.py`) solo se ejecuta el comando localmente.
  * Para garantizar consistencia eventual se desarrollo un mecanismo de rollback.
  Utilizando relojes de Lamport se lleva un clock general de la red para mantenerla
  sincronizada, ademas los mensajes de broadcasting son etiquetados con el momento en
  que sucedieron localmente, de esta forma, si se hace broadcast de un comando antiguo
  quien lo recibe hara rollback de las operaciones que en el tiempo (logico) sucedieron
  despues para aplicar el comando recibido, finalmente volvera a aplicar las operaciones
  que fueron deshechas. Ademas, si dos comandos suceden en el mismo momento (logico),
  entonces se realiza un desempate, y sucedera primero aquel que provenga del servidor
  con menor numero de puerto.
  * Algo a destacar es la eliminacion de potenciales comandos duplicados. Durante la 
  conexion de un nuevo nodo, puede ocurrir que, al quedarse este con la version mas actualizada
  de los nodos, de todas formas queden mensajes a procesar pendientes, que para el nuevo
  nodo serian repetidos. Esto se resuelve simplemente verificando el comando recibido de otro
  servidor no haya sucesido antes. Basicamente se observa si en el log de operaciones hay una entrada
  que tenga el mismo tiempo y el mismo emisor, cosa que no puede suceder.

## Contenido por archivo

* `client`: toma como argumentos la **ip** y **puerto** del servidor/nodo al cual
deseamos conectarnos, una vez conectado pide por entrada estandar
comandos para aplicar sobre el archivo. CTRL+C termina su ejecucion. Ante cada ejecucion
de un comando, mostrara como quedo el contenido al momento de ejecutarlo. Si el comando a
ejecutar es invalido (o se invalida durante se ejecucion), nos lo hara saber.
* `server`: tome como argumentos la **ip** y **puerto** donde escuchara el servidor.
El servidor espera por el envio de algun comando para ejecutar sobre el documento. Tambien 
espera a las conexiones de otros servidores vecinos.
* `components/node`: provee una clase para representar a los nodos, cada servidor (Editor) tiene
un nodo asociado. Esta clase posee rutinas para notificar la conexion y solicitar la informacion
a los nodos de la red, por ello, tambien lleva cuales son los nodos activos de la red y cuales
podrian ser estos. Los posibles nodos de la red son configurables (`components/config/nodes.json`).
* `components/broadcast`: nos provee de una clase que genera un nuevo hilo de ejecucion para
realizar la operacion de broadcasting manteniendo el orden de los comandos.

Se cuanta ademas con pequeñas clases para mejorar el manejo de determinados elementos:

* `clock`: nos provee de una clase para el manejo del reloj logico de la red. Este es
independiente entre cada servidor y sus rutinas utilizan locks para garantizar que los
correctos incrementos del mismo.
* `document`: nos provee de una abstraccion para el manejo del documento. Esta nos permite
aplicar operaciones sobre el mismo, ademas de ir llevando registro (log) de las mismas.
  * `logger`: fuertemente relacionado a `document`, nos provee una abstraccion para el
  manejo del log de los comandos aplicados al documento.
  * `command`: nos brinda una abstraccion para las operaciones a aplicar sobre el documento
  asi como tambien facilitar la obtencion de inversas (utilizadas durante el rollback) y tambien
  para registrarlas facilmente en el log.