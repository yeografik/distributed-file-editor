# distributed-file-editor

Se eligió como proyecto final de aprobación la creación de un sistema distribuido 
para la edición en tiempo real de archivos.

## Autores

**Gonzalez Ignacio - Nolasco Agustin**

### Requirements

Tener instalado python 3.8 o una versión más nueva. Tener instalado y actualizado pip3.

### Setup

`pip3 install virtualenv`

`virtualenv venv`

`source venv/bin/activate`

`pip3 install -r requirements.txt`

De aquí en más siempre se deberá ingresar al ambiente virtual para 
utilizar el sistema.

### How to use

0. Pararse en el directorio ```src/```.
1. En el archivo ```nodes.js``` se encuentra la información acerca de 
los nodos que conforman la red. Esta puede ser modificada según se requiera
para agregar o quitar nuevos nodos, cabe destacar que es necesario que los
nodos tengan números de puerto diferentes para que el sistema funcione
correctamente.
2. Una vez seteados los nodos de la red, se puede proceder a 
iniciarlos ejecutando ```python3 server.py [ip] [port]```, por ejemplo 
```python3 server.py localhost 5001```. Este proceso puede repetirse para 
cada uno de los nodos definidos en nodes.js. ```nodes.js```.
3. Una vez levantados los nodos deseados se puede proceder a realizar conexión 
de la aplicación con alguno de los mismos, para ellos se debera ejecutar python3 
```python3 client.py [ip] [port]```, por ejemplo ```python3 client.py localhost 5001```.

Nota: los nodos pueden irse levantando mientras se va usando la aplicación, 
lo importante es que siempre exista al menos uno para que los usuarios de 
la aplicación puedan conectarse a él. Pero a medida que haya más nodos 
conectados los usuarios de la aplicación podrán conectarse a los distintos 
nodos y editar en conjunto el contenido del documento.

#### scripts

Para correr los scripts ubicados en ```src/scripts/```
0. Pararse en ```src/```.
1. En el archivo ```nodes.js``` setear 6 nodos, con los puertos 5001, 5002, 
5003, 5004, 5005 y 5006.
2. Iniciar los nodos ejecutando ```python3 server.py localhost [port]``` con los 
puertos 5001, 5002, 5003, 5004, 5005 y sus respectivas ip.
3. Finalmente ejecutar cualquiera de los scripts como ```./scripts/[script_name].sh```,
en casos de querer correr ```scripts.sh```, se debera proveer como argumento un
puerto.
    

## Decisiones de implementación

* Se optó de momento por la edición de un único archivo. 
Para la edición de múltiples archivos simplemente bastaría con 
solicitar un archivo específico a partir de la aplicación, y, en 
caso de que no existe, crearlo. Por cuestiones de simplicidad 
es que se ha tomado esta decisión.
* Cuando se inicia un nuevo nodo este se presenta ante aquellos 
que ya forman parte de la red para que estos puedan registrarlo
como un nodo activo, mientras que el nodo en cuestión registra 
como nodos activos a todos aquellos que le respondan.
nodos activos a todos aquellos que le respondan.
  * Durante este proceso, el nodo en caso de que no sea el primer 
  nodo de la red, solicita la información del documento a todos 
  los nodos de la red, mientras que estos esperan a la respuesta 
  del nuevo nodo, el nuevo nodo se queda con la información del 
  nodo que tenga la versión más actualizada del documento, de 
  esta forma garantizamos que la red no sigue su curso mientras 
  un nodo se conecta y además, el nuevo nodo conectado tiene la 
  información más reciente.
  * En caso de que este sea el primer nodo de la red, la información será 
  levantada de un archivo local, en caso de existir, sino será creado.
* Los nodos tienen la capacidad de detectar cuando otro está caído, esto 
se hace durante el envío de algún mensaje, si este falla entonces se considera 
al nodo receptor como caído.
* Para realizar broadcasting se crea un nuevo thread que maneja una cola, 
mientras esa cola esté vacía el thread estará a la espera de que algún 
comando a ser enviado por broadcast sea agregado a la misma.
* El servidor puede recibir diversos mensajes, entre ellos la ejecución de 
un comando, que puede provenir de un cliente (client.py) o de otro servidor 
por medio de un broadcast. En caso de que el mensaje sea de un cliente, el 
comando será ejecutado localmente para luego ser agregado a la cola de broadcasting, 
el cual enviará dicho comando a todos sus nodos vecinos. En caso de que el comando 
recibido provenga de un vecino (server.py) solo se ejecuta el comando localmente.
  * Para garantizar consistencia eventual se desarrolló un mecanismo de rollback. 
  Utilizando relojes de Lamport se lleva un clock general de la red para mantenerla 
  sincronizada, además los mensajes de broadcasting son etiquetados con el clock en 
  que sucedieron localmente, de esta forma, si se hace broadcast de un comando antiguo 
  quien lo recibe hará rollback de las operaciones que en el tiempo (lógico) sucedieron 
  después para aplicar el comando recibido, finalmente volverá a aplicar las operaciones 
  que fueron deshechas. Además, si dos comandos suceden en el mismo momento (lógico), 
  entonces se realiza un desempate, y sucederá primero aquel que provenga del servidor 
  con menor número de puerto, tenemos garantizado que, a la hora de desempatar, nunca
  tendremos puertos iguales, ya que los nodos fueron seteados con puertos diferentes.
  * Algo a destacar es la eliminación de potenciales comandos duplicados. Durante la 
  conexión de un nuevo nodo, puede ocurrir que, al quedarse este con la versión más 
  actualizada de los nodos, de todas formas queden mensajes a procesar pendientes, que 
  para el nuevo nodo serían repetidos. Esto se resuelve simplemente verificando que el
  comando recibido de otro servidor no haya sucedido antes. Básicamente se observa si 
  en el log de operaciones hay una entrada que tenga el mismo tiempo y el mismo emisor, 
  cosa que no puede suceder.

## Contenido por archivo

* `client`: toma como argumentos la **ip** y **puerto** del servidor/nodo al cual
deseamos conectarnos, una vez conectado pide por entrada estándar comandos para 
aplicar sobre el archivo. CTRL+C termina su ejecución. Ante cada ejecución de un 
comando, mostrará cómo quedó el contenido al momento de ejecutarlo. Si el comando 
a ejecutar es invalido (o se invalida durante su ejecución), nos lo hará saber 
mostrando un mensaje.
* `server`: toma como argumentos la **ip** y **puerto** donde escuchará el servidor. 
El servidor espera por el envío de algún comando para ejecutar sobre el documento. 
También espera a las conexiones de otros servidores vecinos.
* `components/node`: provee una clase para representar a los nodos, cada servidor 
(Editor) tiene un nodo asociado. Esta clase posee rutinas para notificar la conexión 
y solicitar la información a los nodos de la red, por ello, también lleva cuáles son 
los nodos activos de la red y cuáles podrían ser estos. Los posibles nodos de la red 
son configurables (`components/config/nodes.json`).
* `components/broadcast`: nos provee de una clase que genera un nuevo hilo de ejecución 
para realizar la operación de broadcasting manteniendo el orden de los comandos.

Se cuenta además con pequeñas clases para mejorar el manejo de determinados elementos:

* `clock`: nos provee de una clase para el manejo del reloj lógico de la red. Este es 
independiente entre cada servidor y sus rutinas utilizan locks para garantizar los 
correctos incrementos del mismo.
* `document`: nos provee de una abstracción para el manejo del documento. Esta nos permite 
aplicar operaciones sobre el mismo, además de ir llevando registro (log) de las mismas.
  * `logger`: fuertemente relacionado a `document`, nos provee una abstracción para el 
  manejo del log de los comandos aplicados al documento.
  * `command`: nos brinda una abstracción para las operaciones a aplicar sobre el documento 
  así como también facilitar la obtención de inversas (utilizadas durante el rollback) 
  y también para registrarlas fácilmente en el log.
