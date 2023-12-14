# distributed-file-editor

*Se eligio como proyecto final de aprobacion la creacion un sistema distribuido para la
edicion en tiempo real de archivos.*

## Autores

**Gonzalez Ignacio - Nolasco Agustin**

### Setup

`virtualenv venv`

`source venv/bin/activate`

`pip3 install -r requirements.txt`

De aqui en mas siempre se debera ingresar al ambiente virtual para
utilizar el sistema.

### How to use

1. En el archivo ```nodes.js``` se encuentra la informacion
acerca de los nodos que conforman en la red. Esta puede ser modificada
segun se lo requiera para agregar o quitar nuevo nodos.
2. Una vez seteado los nodos de la red se puede proceder a
iniciarlos ejecutando ```python3 server.py [ip] [port]```, por ejemplo 
```python3 server.py localhost 5001```. Este proceso puede repetirse para
cada uno de los nodos definidos en ```nodes.js```.
3. Una vez levantados los nodos deseados se puede proceder a realizar conexion
de la aplicacion con alguno de los mismos, para ellos se debera ejecutar 
```python3 app.py [ip] [port]```, por ejemplo ```python3 app.py localhost 5001```

Nota: los nodos pueden irse levantando mientras se va usando la aplicacion, 
lo importante es que siempre exista al menos uno para que los usuarios de 
la aplicacion puedan conectarse a el. Pero a medida que haya mas nodos
conectados los usuarios de la aplicacion podran conectarse a los distintos
nodo y editar en conjunto el contenido del documento.

## Deciciones de implementacion

* Se opto de momento por la edicion de un unico archivo.
Para la edicion de multiples archivos simplemente bastaria
solicitar un archivo especifico a partir de la aplicacion, y
,en caso de que no exista, crearlo. Por cuestion de simplicidad
es que se ha tomado esta decision.
* Cuando se inicia un nuevo nodo este se presenta ante aquellos
que ya forman parte de la red para que estos pueda registrarlo
un nodo activo, mientras que el nodo en cuestion registra como
nodos activos a todos aquellos que le respondan.
  * Durante este proceso el nodo, en caso de que no sea el primer
  nodo de la red, solicita la informacion del documento a alguno
  de los nodos que si forman parte de esta. En caso de que este
  sea el primer nodo de la red, la informacion sera levantada de
  un archivo local, en caso de existir, sino sera creado.
