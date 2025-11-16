# Relaciones Unidireccionales entre Módulos de Red y Servidor

El laboratorio está dividido en dos módulos independientes: network (encargado de generar configuraciones de red) y server (encargado de crear un recurso que depende de la red). La característica principal de esta fase es que la relación entre los módulos es unidireccional, es decir: network -> server.

El módulo del servidor depende del módulo de red, pero la red no depende del servidor. Esta separación permite crear componentes reutilizables y evita dependencias circulares.

## Análisis del módulo network

El archivo `network/network.tf.json` define dos recursos. Estos son `null_resource.network` y `local_file.network_state` (que genera el archivo `network_outputs.json`). Este último recurso incluye una dependencia explícita que dice `"depends_on": ["null_resource.network"]`. Por lo tanto, el orden interno del módulo network es null_resource.network -> local_file.network_state. El archivo generado (`network_outputs.json`) contiene información de subredes, que será utilizada por el módulo principal.

## Análisis del módulo server

El archivo `main.tf.json` define el recurso `null_resource.hello-world`, este recurso no incluye una dependencia explícita hacia el módulo network, por lo que Terraform no detecta automáticamente dicha relación, pero tambien el laboratorio implementa una dependencia operacional a través del Makefile, donde la regla all define el orden se define el orden prepare -> network -> server. Esto fuerza a que el módulo network se ejecute antes de que el servidor sea creado, manteniendo la unidireccionalidad.

## Orden de creación y destrucción

Durante la ejecución de los comandos solicitados (terraform init, terraform apply, make all y posteriormente terraform destroy), se observó el siguiente comportamiento:

### Orden de creación

#### Módulo network

El plan marcó dos recursos con acción + create: null_resource.network y local_file.network_state. Y en la salida del apply quedó el orden real:

```
null_resource.network: Creating...
null_resource.network: Creation complete
local_file.network_state: Creating...
local_file.network_state: Creation complete
```

Esto confirma la dependencia explícita depends_on en el archivo JSON, donde local_file.network_state solo se ejecuta después del recurso null_resource.network.

#### Módulo raíz

Cuando se ejecutó make all, Terraform detectó que debía reemplazar el recurso null_resource.network debido a que el trigger timestamp() había cambiado:

```
null_resource.network must be replaced
Destroying old null_resource.network
Creating new null_resource.network
```

Luego, al ejecutar la fase server:

```
null_resource.hello-world: Refreshing state...
No changes. Your infrastructure matches the configuration.
```

Es decir, el servidor se aplicó después de la red, manteniendo la unidireccionalidad.

### Orden de destrucción

#### Módulo raíz

Al ejecutar terraform destroy. Primero se destruyó el recurso del servidor:

```
null_resource.hello-world: Destroying...
null_resource.hello-world: Destruction complete
```

#### Módulo network

Luego, al destruir el módulo network, local_file.network_state se destruyó primero y null_resource.network se destruyó después. En el orden exacto mostrado:

```
local_file.network_state: Destroying...
local_file.network_state: Destruction complete
null_resource.network: Destroying...
null_resource.network: Destruction complete
```

Esto coincide con el grafo de dependencias, donde `local_file.network_state` depende de `null_resource.network` y por tanto debe eliminarse antes.