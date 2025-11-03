# Actividad: Escribiendo infraestructura como código en un entorno local con Terraform

##  Contexto

Imagina que gestionas docenas de entornos de desarrollo locales para distintos proyectos (app1, app2, ...). En lugar de crear y parchear manualmente cada carpeta, construirás un generador en Python que produce automáticamente:

* **`network.tf.json`** (variables y descripciones)
* **`main.tf.json`** (recursos que usan esas variables)

Después verás cómo Terraform identifica cambios, remedia desvíos manuales y permite migrar configuraciones legacy a código. Todo sin depender de proveedores en la nube, Docker o APIs externas.

## Fase 0: Preparación 

1. **Revisa** el laboratorio correspondiente:

   ```
   modules/simulated_app/
     ├─ network.tf.json
     └─ main.tf.json
   generate_envs.py
   ```
2. **Verifica** que puedes ejecutar:

   ```bash
   python3 generate_envs.py
   cd environments/app1
   terraform init
   terraform apply
   ```
3. **Objetivo**: conocer la plantilla base y el generador en Python.

##  Fase 1: Expresando el cambio de infraestructura

* **Concepto**
Cuando cambian variables de configuración, Terraform los mapea a **triggers** que, a su vez, reconcilian el estado (variables ->triggers ->recursos).

* **Actividad**

   - Modifica en `enviroments/app1/network.tf.json` el `default` de `"network"` a `"lab-net"`.
   - `terraform plan` observa que **solo** cambia el trigger en `null_resource`.

* **Preguntas**

   - `terraform plan` antes del cambio y antes de `terraform apply`

      ```
      jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app1$ terraform plan

      Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following
      symbols:
      + create

      Terraform will perform the following actions:

      # null_resource.app1 will be created
      + resource "null_resource" "app1" {
            + id       = (known after apply)
            + triggers = {
               + "name"    = "app1"
               + "network" = "net1"
            }
         }

      # null_resource.network_sim will be created
      + resource "null_resource" "network_sim" {
            + id       = (known after apply)
            + triggers = {
               + "name"    = "hello-world"
               + "network" = "local-network"
            }
         }

      Plan: 2 to add, 0 to change, 0 to destroy.

      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

      Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run
      "terraform apply" now.
      ```
   - `terraform apply`

      ```
      jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app1$ terraform apply

      Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following
      symbols:
      + create

      Terraform will perform the following actions:

      # null_resource.app1 will be created
      + resource "null_resource" "app1" {
            + id       = (known after apply)
            + triggers = {
               + "name"    = "app1"
               + "network" = "net1"
            }
         }

      # null_resource.network_sim will be created
      + resource "null_resource" "network_sim" {
            + id       = (known after apply)
            + triggers = {
               + "name"    = "hello-world"
               + "network" = "local-network"
            }
         }

      Plan: 2 to add, 0 to change, 0 to destroy.

      Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

      null_resource.app1: Creating...
      null_resource.network_sim: Creating...
      null_resource.app1: Provisioning with 'local-exec'...
      null_resource.app1 (local-exec): Executing: ["/bin/sh" "-c" "echo 'Arrancando servidor app1 en red net1'"]
      null_resource.app1 (local-exec): Arrancando servidor app1 en red net1
      null_resource.app1: Creation complete after 0s [id=4259121708513663781]
      null_resource.network_sim: Creation complete after 0s [id=4010562518234862503]

      Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
      ```
   - `terraform plan` antes del cambio

      ```
      jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app1$ terraform plan
      null_resource.app1: Refreshing state... [id=4259121708513663781]
      null_resource.network_sim: Refreshing state... [id=4010562518234862503]

      No changes. Your infrastructure matches the configuration.

      Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
      ```

   - `terraform plan` despues del cambio

      ```
      jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app1$ terraform plan
      null_resource.app1: Refreshing state... [id=4259121708513663781]
      null_resource.network_sim: Refreshing state... [id=4010562518234862503]

      Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following
      symbols:
      -/+ destroy and then create replacement

      Terraform will perform the following actions:

      # null_resource.network_sim must be replaced
      -/+ resource "null_resource" "network_sim" {
            ~ id       = "4010562518234862503" -> (known after apply)
            ~ triggers = { # forces replacement
               ~ "network" = "local-network" -> "lab-net"
                  # (1 unchanged element hidden)
            }
         }

      Plan: 1 to add, 0 to change, 1 to destroy.

      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

      Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run
      "terraform apply" now.
      ```

* ¿Cómo interpreta Terraform el cambio de variable?

   Cuando cambié el valor de la variable network de "local-network" a "lab-net", Terraform lo detectó como una modificación en los triggers del recurso null_resource.network_sim, se dio cuenta de que algo en la configuración cambió y, como ese trigger forma parte del estado del recurso, decidió reemplazarlo. No recreó todo, solo ese recurso específico, porque solo ahí vio una diferencia entre lo que está en el código y lo que guarda en el terraform.tfstate.

* ¿Qué diferencia hay entre modificar el JSON vs. parchear directamente el recurso?

   Si modifico la plantilla, puedo regenerar todos los entornos de forma reproducible. Pero si edito directamente el recurso, ese cambio se pierde la próxima vez que ejecute terraform apply, porque los recursos se generan en diversos entornos según la configuración terraform.

* ¿Por qué Terraform no recrea todo el recurso, sino que aplica el cambio "in-place"?

   Terraform solo recrea lo que realmente cambió, el único cambio fue en el valor del trigger de network_sim, así que solo destruyó y volvió a crear ese recurso. Todo lo demás (como el recurso app1) siguió igual, por lo que Terraform no lo tocó, Terraform analiza cada parte y actúa solo donde hay diferencias, sin rehacer todo desde cero.

* ¿Qué pasa si editas directamente `main.tf.json` en lugar de la plantilla de variables?

   main.tf.json describe la infraestructura final (los recursos) asi que si edito el main.tf.json directamente significa que estamos cambiando la lógica o estructura del módulo, no solo sus entradas. Terraform vería ese cambio como una modificación estructural y podría recrear recursos.

## Fase 2: Entendiendo la inmutabilidad

### A. Remediación de 'drift' (out-of-band changes)

1. **Simulación**

   ```bash
   cd environments/app2
   terraform init
   terraform apply
   # edita manualmente terraform.tfstate: cambiar "name":"app2" ->"hacked-app"
   ```
2. Ejecuta:

   ```bash
   terraform plan
   ```

   Ahora Terraform verá que el estado real (modificado) no coincide con el código (main.tf.json) y propondrá corregirlo.

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app2$ terraform plan
   null_resource.network_sim: Refreshing state... [id=7187014476437573362]
   null_resource.hacked-app: Refreshing state... [id=4059072469876814575]

   Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following
   symbols:
   + create
   - destroy

   Terraform will perform the following actions:

   # null_resource.app2 will be created
   + resource "null_resource" "app2" {
         + id       = (known after apply)
         + triggers = {
            + "name"    = "app2"
            + "network" = "net2"
         }
      }

   # null_resource.hacked-app will be destroyed
   # (because null_resource.hacked-app is not in configuration)
   - resource "null_resource" "hacked-app" {
         - id       = "4059072469876814575" -> null
         - triggers = {
            - "name"    = "app2"
            - "network" = "net2"
         } -> null
      }

   Plan: 1 to add, 0 to change, 1 to destroy.

   ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

   Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run
   "terraform apply" now.
   ```

3. **Aplica**

   ```bash
   terraform apply
   ```
   Terraform restaurará el estado a "app2".
   
### B. Migrando a IaC

* **Mini-reto**
1. Crea en un nuevo directorio `legacy/` un simple `run.sh` + `config.cfg` con parámetros (por ejemplo, puertos, rutas).

   ```sh
   echo 'PORT=8080' > legacy/config.cfg
   echo '#!/bin/bash' > legacy/run.sh
   echo 'echo "Arrancando $PORT"' >> legacy/run.sh
   chmod +x legacy/run.sh
   ```
2. Escribe un script Python que:

   * Lea `config.cfg` y `run.sh`.
   * Genere **automáticamente** un par `network.tf.json` + `main.tf.json` equivalente.
   * Verifique con `terraform plan` que el resultado es igual al script legacy.

   El script creado es [`migracion_IaC.py`](./Laboratorio/migracion_IaC.py).

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app_legacy$ terraform apply

   Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following
   symbols:
   + create

   Terraform will perform the following actions:

   # null_resource.legacy_app will be created
   + resource "null_resource" "legacy_app" {
         + id       = (known after apply)
         + triggers = {
            + "port" = "8080"
         }
      }

   Plan: 1 to add, 0 to change, 0 to destroy.

   Do you want to perform these actions?
   Terraform will perform the actions described above.
   Only 'yes' will be accepted to approve.

   Enter a value: yes

   null_resource.legacy_app: Creating...
   null_resource.legacy_app: Provisioning with 'local-exec'...
   null_resource.legacy_app (local-exec): Executing: ["/bin/sh" "-c" "echo 'Arrancando 8080'"]
   null_resource.legacy_app (local-exec): Arrancando 8080
   null_resource.legacy_app: Creation complete after 0s [id=1306315554674875942]

   Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
   ```

## Fase 3: Escribiendo código limpio en IaC 

| Conceptos                       | Ejercicio rápido                                                                                               |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Control de versiones comunica contexto** | - Haz 2 commits: uno que cambie `default` de `name`; otro que cambie `description`. Revisar mensajes claros. |
| **Linting y formateo**                     | - Instala `jq`. Ejecutar `jq . network.tf.json > tmp && mv tmp network.tf.json`. ¿Qué cambió?                 |
| **Nomenclatura de recursos**               | - Renombra en `main.tf.json` el recurso `null_resource` a `local_server`. Ajustar generador Python.           |
| **Variables y constantes**                 | - Añade variable `port` en `network.tf.json` y usarla en el `command`. Regenerar entorno.                     |
| **Parametrizar dependencias**              | - Genera `env3` de modo que su `network` dependa de `env2` (por ejemplo, `net2-peered`). Implementarlo en Python.    |
| **Mantener en secreto**                    | - Marca `api_key` como **sensitive** en el JSON y leerla desde `os.environ`, sin volcarla en disco.           |

### Desarrollo 

- Control de versiones comunica contexto

   Primer cambio:

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ git diff Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   diff --git a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   index 1afdf03..77384cc 100644
   --- a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   +++ b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   @@ -2,7 +2,7 @@
      "variable": {
            "name": {
               "type": "string",
   -            "default": "hello-world",
   +            "default": "Actividad13-Server",
               "description": "Nombre del servidor local"
            },
            "network": {
   ```

   Segundo Cambio:

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ git diff Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   diff --git a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   index 77384cc..ce82b29 100644
   --- a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   +++ b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   @@ -3,7 +3,7 @@
            "name": {
               "type": "string",
               "default": "Actividad13-Server",
   -            "description": "Nombre del servidor local"
   +            "description": "Nombre del servidor simulado (Actividad 13)"
            },
            "network": {
               "type": "string",
   ```

   Registro de commits:

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ git log -n 4
   commit 9f82206d69a9a17916c42e06b4cf03381ca0c04c (HEAD -> main)
   Author: RenzoQuispe <renzo123cd@gmail.com>
   Date:   Sun Nov 2 16:13:12 2025 -0500

      actualizar descripción de la variable name en network.tf.json

   commit b508644b3a4cf806355156bd3cab6e063aa658c0
   Author: RenzoQuispe <renzo123cd@gmail.com>
   Date:   Sun Nov 2 16:11:24 2025 -0500

      actualizar nombre por defecto del servidor a Actividad13-Server

   commit d9c770a1cb2b7861b3ae7691e697e690e9ffa0a7
   Author: RenzoQuispe <renzo123cd@gmail.com>
   Date:   Sun Nov 2 16:08:20 2025 -0500

      agregar desarrollo Fase 2 de la Actividad 13

   commit f33b6f1b7d9e8b910a19ecf2666580ac8d270bfc
   Author: RenzoQuispe <renzo123cd@gmail.com>
   Date:   Sun Nov 2 14:16:17 2025 -0500

      agregar desarrollo Fase0 y Fase1 Actividad 13
   ```

- Linting y formateo

   Después de ejecutar jq, lo que cambió en el archivo fue principalmente la presentación: la indentación de todas las claves anidadas se estandarizó y se alineó uniformemente, se agregó un salto de línea al final del archivo, y el contenido lógico del JSON permaneció igual; es decir, nada de los valores o estructura interna se modificó, solo se hizo más legible y consistente.

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ git diff modules/simulated_app/network.tf.json
   diff --git a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   index ce82b29..e5bbeab 100644
   --- a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   +++ b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/network.tf.json
   @@ -1,24 +1,24 @@
   {
   -    "variable": {
   -        "name": {
   -            "type": "string",
   -            "default": "Actividad13-Server",
   -            "description": "Nombre del servidor simulado (Actividad 13)"
   -        },
   -        "network": {
   -            "type": "string",
   -            "default": "local-network",
   -            "description": "Nombre de la red local"
   -        }
   +  "variable": {
   +    "name": {
   +      "type": "string",
   +      "default": "Actividad13-Server",
   +      "description": "Nombre del servidor simulado (Actividad 13)"
      },
   -    "resource": {
   -        "null_resource": {
   -            "network_sim": {
   -                "triggers": {
   -                    "network": "${var.network}",
   -                    "name": "${var.name}"
   -                }
   -            }
   +    "network": {
   +      "type": "string",
   +      "default": "local-network",
   +      "description": "Nombre de la red local"
   +    }
   +  },
   +  "resource": {
   +    "null_resource": {
   +      "network_sim": {
   +        "triggers": {
   +          "network": "${var.network}",
   +          "name": "${var.name}"
            }
   +      }
      }
   -}
   \ No newline at end of file
   +  }
   +}
   ```

- Nomenclatura de recursos

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ git diff modules/simulated_app/main.tf.json
   diff --git a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/main.tf.json b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/main.tf.json
   index 944a05f..4a3ddba 100644
   --- a/Actividad13-CC3S2/Laboratorio/modules/simulated_app/main.tf.json
   +++ b/Actividad13-CC3S2/Laboratorio/modules/simulated_app/main.tf.json
   @@ -1,7 +1,7 @@
   {
      "resource": [
      {
   -      "null_resource": [
   +      "local-server": [
            {
            "hello-server": [
               {
   ```

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ git diff generate_envs.py
   diff --git a/Actividad13-CC3S2/Laboratorio/generate_envs.py b/Actividad13-CC3S2/Laboratorio/generate_envs.py
   index 0e7c6f0..cc67510 100644
   --- a/Actividad13-CC3S2/Laboratorio/generate_envs.py
   +++ b/Actividad13-CC3S2/Laboratorio/generate_envs.py
   @@ -23,7 +23,7 @@ def render_and_write(env):
      config = {
            "resource": [
               {
   -                "null_resource": [
   +                "local-server": [
                        {
                           env["name"]: [
                              {
   ```
   
   Para este caso, local-server no es un tipo de recurso válido. Por eso cuando ejecutamos terraform init, Terraform intenta buscar un proveedor llamado local-server y falla.

- Variables y constantes

   ```json
   {
   "variable": {
      "name": {
         "type": "string",
         "default": "Actividad13-Server",
         "description": "Nombre del servidor simulado (Actividad 13)"
      },
      "network": {
         "type": "string",
         "default": "local-network",
         "description": "Nombre de la red local"
      },
      "port": {
         "type": "string",
         "default": "8080",
         "description": "Puerto de la aplicación"
      }
   },
   "resource": {
      "null_resource": {
         "network_sim": {
         "triggers": {
            "network": "${var.network}",
            "name": "${var.name}",
            "port": "${var.port}"
         },
         "provisioner": [
            {
               "local-exec": {
               "command": "echo 'Arrancando servidor ${var.name} en red ${var.network} en puerto ${var.port}'"
               }
            }
         ]
         }
      }
   }
   }
   ```

- Parametrizar dependencias

   Se agregó el script `generate_envs2.py` el cual genera entornos Terraform a partir de la plantilla base. Para cada entorno definido en la lista ENVS, copia la plantilla network.tf.json y genera un main.tf.json con un recurso null_resource que incluye triggers y un provisioner local-exec que imprime un mensaje de arranque usando las variables name, network y port. También permite que unas redes dependan de otras, como env3 que hereda y modifica la red de env2, haciendo que toda la configuración sea declarativa y reproducible.

- Mantener en secreto

   En network.tf.json definimos la variables sensible:

   ```json
   {
   "variable": {
      "name": {
         "type": "string",
         "default": "Actividad13-Server",
         "description": "Nombre del servidor simulado (Actividad 13)"
      },
      "network": {
         "type": "string",
         "default": "local-network",
         "description": "Nombre de la red local"
      },
      "api_key": {
         "type": "string",
         "sensitive": true,
         "description": "Clave secreta de la API"
      }
   }
   }
   ```

   La clave api_key es "sensitive": true, que le indica a Terraform que no la muestre en plan ni en state de forma legible.

   Usamos la variables sensible en main.tf.json con local-exec, editamos:

   ```
   "command": "echo 'Usando API key secreta... ${var.api_key}'"
   ```

   Terraform permite pasar variables por el entorno usando el prefijo TF_VAR_

   ```
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app2$ TF_VAR_api_key=clave12345abc terraform plan

   Terraform used the selected providers to generate the following execution plan. Resource actions are indicated
   with the following symbols:
   + create

   Terraform will perform the following actions:

   # null_resource.app2 will be created
   + resource "null_resource" "app2" {
         + id       = (known after apply)
         + triggers = {
            + "name"    = "app2"
            + "network" = "net2"
         }
      }

   # null_resource.network_sim will be created
   + resource "null_resource" "network_sim" {
         + id       = (known after apply)
         + triggers = {
            + "name"    = "Actividad13-Server"
            + "network" = "local-network"
            + "port"    = "8080"
         }
      }

   Plan: 2 to add, 0 to change, 0 to destroy.

   ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────

   Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these
   actions if you run "terraform apply" now.
   jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/environments/app2$ TF_VAR_api_key=clave12345abc terraform apply

   Terraform used the selected providers to generate the following execution plan. Resource actions are indicated
   with the following symbols:
   + create

   Terraform will perform the following actions:

   # null_resource.app2 will be created
   + resource "null_resource" "app2" {
         + id       = (known after apply)
         + triggers = {
            + "name"    = "app2"
            + "network" = "net2"
         }
      }

   # null_resource.network_sim will be created
   + resource "null_resource" "network_sim" {
         + id       = (known after apply)
         + triggers = {
            + "name"    = "Actividad13-Server"
            + "network" = "local-network"
            + "port"    = "8080"
         }
      }

   Plan: 2 to add, 0 to change, 0 to destroy.

   Do you want to perform these actions?
   Terraform will perform the actions described above.
   Only 'yes' will be accepted to approve.

   Enter a value: yes

   null_resource.app2: Creating...
   null_resource.network_sim: Creating...
   null_resource.app2: Provisioning with 'local-exec'...
   null_resource.app2 (local-exec): Executing: ["/bin/sh" "-c" "echo 'Arrancando servidor app2 en red net2'"]
   null_resource.network_sim: Provisioning with 'local-exec'...
   null_resource.network_sim (local-exec): Executing: ["/bin/sh" "-c" "echo 'Arrancando servidor Actividad13-Server en red local-network en puerto 8080'"]
   null_resource.app2 (local-exec): Arrancando servidor app2 en red net2
   null_resource.app2: Creation complete after 0s [id=9054091989904731003]
   null_resource.network_sim (local-exec): Arrancando servidor Actividad13-Server en red local-network en puerto 8080
   null_resource.network_sim: Creation complete after 0s [id=7237694080402379702]

   Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
   ```

## Fase 4: Integración final y discusión

1. **Recorrido** por:

   * Detección de drift (*remediation*).
   * Migración de legacy.
   * Estructura limpia, módulos, variables sensibles.
   
2. **Preguntas abiertas**:

* ¿Cómo extenderías este patrón para 50 módulos y 100 entornos?

   Organizaría los módulos de manera que cada uno sea independiente y tenga su propia plantilla network.tf.json y main.tf.json. Luego usaría un generador en Python que recorra una lista de entornos y módulos para crear automáticamente las carpetas y archivos, aplicando variables diferentes por entorno. Así puedo mantener todo reproducible sin tener que tocar cada archivo manualmente, y si cambio algo en la plantilla base, se propaga a todos los entornos.

* ¿Qué prácticas de revisión de código aplicarías a los `.tf.json`?

   Le pondría énfasis a la consistencia y legibilidad, verificaria que las claves estén bien indentadas, usaria jq para formateo automático, y revisar que los valores por defecto y descripciones sean claros. También que los commits tengan mensajes específicos explicando los cambios de infraestructura, y que no se modifiquen directamente los JSON generados, solo las plantillas o el generador Python.

* ¿Cómo gestionarías secretos en producción (sin Vault)?

   Usaría variables sensibles en Terraform ("sensitive": true) y pasaría los secretos mediante variables de entorno (TF_VAR_*) o archivos .tfvars que no se suban a git, nunca los pondría en los JSON ni en el código.

* ¿Qué workflows de revisión aplicarías a los JSON generados?

   Para los JSON generados, revisaría siempre el generador Python y las plantillas, no los JSON directamente, porque en este caso son artefactos dependientes. Se puede usar hooks de pre-commit que corran jq para formatearlos automáticamente y que verifiquen que no se cambien valores sensibles accidentalmente.

## Ejercicios

### 1. Drift avanzado

Crea un recurso "load_balancer" que dependa de dos `local_server`. Simula drift en uno de ellos y observa el plan.

#### Desarrollo

- Ampliamos main.tf.json con varios recursos dependientes

```json
{
  "resource": [
    {
      "null_resource": [
        {
          "server1": [
            {
              "triggers": {
                "name": "srv1",
                "network": "netA"
              },
              "provisioner": [
                {
                  "local-exec": {
                    "command": "echo 'Iniciando servidor srv1 en red netA'"
                  }
                }
              ]
            }
          ],
          "server2": [
            {
              "triggers": {
                "name": "srv2",
                "network": "netA"
              },
              "provisioner": [
                {
                  "local-exec": {
                    "command": "echo 'Iniciando servidor srv2 en red netA'"
                  }
                }
              ]
            }
          ],
          "load_balancer": [
            {
              "triggers": {
                "depends_on": "srv1,srv2",
                "mode": "active"
              },
              "provisioner": [
                {
                  "local-exec": {
                    "command": "echo 'Balanceador activo gestionando srv1 y srv2'"
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Hacemos `terraform apply`

- Para simular el drift modificamos terraform.tfstate. Luego para detectar el drift ejecutamos terraform plan.

```
jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/modules/simulated_app$ terraform plan
var.api_key
  Clave secreta de la API

  Enter a value: 

null_resource.load_balancer: Refreshing state... [id=4335614650467243007]
null_resource.server2: Refreshing state... [id=7602506153947056517]
null_resource.network_sim: Refreshing state... [id=8060113344873722084]
null_resource.server1: Refreshing state... [id=7533359670905045215]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated
with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # null_resource.server1 must be replaced
-/+ resource "null_resource" "server1" {
      ~ id       = "7533359670905045215" -> (known after apply)
      ~ triggers = { # forces replacement
          ~ "network" = "netB" -> "netA"
            # (1 unchanged element hidden)
        }
    }

Plan: 1 to add, 0 to change, 1 to destroy.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these
actions if you run "terraform apply" now.
```

- Corregimos el estado

Al hacer terraform apply, terraform corrigió el estado eliminando el recurso alterado y recreándolo correctamente. Así comprobé que Terraform puede detectar y remediar cambios hechos fuera de su control (“drift”) sin que yo tenga que editar manualmente los archivos otra vez.

```
jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio/modules/simulated_app$ terraform apply
var.api_key
  Clave secreta de la API

  Enter a value: 

null_resource.load_balancer: Refreshing state... [id=4335614650467243007]
null_resource.server2: Refreshing state... [id=7602506153947056517]
null_resource.network_sim: Refreshing state... [id=8060113344873722084]
null_resource.server1: Refreshing state... [id=7533359670905045215]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated
with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # null_resource.server1 must be replaced
-/+ resource "null_resource" "server1" {
      ~ id       = "7533359670905045215" -> (known after apply)
      ~ triggers = { # forces replacement
          ~ "network" = "netB" -> "netA"
            # (1 unchanged element hidden)
        }
    }

Plan: 1 to add, 0 to change, 1 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

null_resource.server1: Destroying... [id=7533359670905045215]
null_resource.server1: Destruction complete after 0s
null_resource.server1: Creating...
null_resource.server1: Provisioning with 'local-exec'...
null_resource.server1 (local-exec): Executing: ["/bin/sh" "-c" "echo 'Iniciando servidor srv1 en red netA'"]
null_resource.server1 (local-exec): Iniciando servidor srv1 en red netA
null_resource.server1: Creation complete after 0s [id=3811140612461234218]

Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

###  2. CLI Interactiva

Refactoriza `generate_envs.py` con `click` para aceptar:

   ```bash
   python3 generate_envs.py --count 3 --prefix staging --port 3000
   ```

#### Desarrollo

Archivo `generate_envs.py`:

```python
import os, json
from shutil import copyfile
import shutil
import click

MODULE_DIR = "modules/simulated_app"
OUT_DIR = "environments"

def render_and_write(env):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    # 1) Copia la definición de variables (network.tf.json)
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )

    # 2) Genera main.tf.json con el puerto incluido
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        env["name"]: [
                            {
                                "triggers": {
                                    "name":    env["name"],
                                    "network": env["network"],
                                    "port":    str(env["port"])
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": (
                                                f"echo 'Arrancando servidor "
                                                f"{env['name']} en red {env['network']} en puerto {env['port']}'"
                                            )
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)

@click.command()
@click.option('--count', default=3, help='Cantidad de entornos a crear')
@click.option('--prefix', default='app', help='Prefijo de los entornos')
@click.option('--port', default=8080, help='Puerto base simulado')
def main(count, prefix, port):
    """Genera entornos Terraform simulados."""

    ENVS = [
        {"name": f"{prefix}{i}", "network": f"net{i}", "port": port}
        for i in range(1, count + 1)
    ]

    for env in ENVS:
        render_and_write(env)

    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/' con prefijo '{prefix}' y puerto {port}")

if __name__ == "__main__":
    main()
```

Ejecución:

```
jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ python3 generate_envs.py --count 3 --prefix staging --port 3000
Generados 3 entornos en 'environments/' con prefijo 'staging' y puerto 3000
jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ tree -L 3 environments/
environments/
├── staging1
│   ├── main.tf.json
│   └── network.tf.json
├── staging2
│   ├── main.tf.json
│   └── network.tf.json
└── staging3
    ├── main.tf.json
    └── network.tf.json

4 directories, 6 files
```

###  3. Validación de Esquema JSON

- Diseña un JSON Schema que valide la estructura de ambos TF files. 
- Lanza la validación antes de escribir cada archivo en Python.

#### Desarrollo

JSON Schema que valida la estructura de ambos TF files. 

```json
NETWORK_SCHEMA = {
    "type": "object",
    "properties": {
        "variable": {
            "type": "object",
            "properties": {
                "name": {"type": "object"},
                "network": {"type": "object"},
                "port": {"type": "object"},
                "api_key": {"type": "object"}
            },
            "required": ["name", "network"]
        },
        "resource": {"type": "object"}
    },
    "required": ["variable"]
}

MAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "resource": {
            "type": "array",
            "items": {
                "type": "object"
            }
        }
    },
    "required": ["resource"]
}
```

Esto es una validación básica, lo suficiente para detectar errores de formato, se agregará en el mismo script. Modificaciónes de generate_envs.py con respecto a la version del anterior ejercicio:

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad13-CC3S2/Laboratorio$ git diff generate_envs.py
diff --git a/Actividad13-CC3S2/Laboratorio/generate_envs.py b/Actividad13-CC3S2/Laboratorio/generate_envs.py
index 18ec33c..c640ac2 100644
--- a/Actividad13-CC3S2/Laboratorio/generate_envs.py
+++ b/Actividad13-CC3S2/Laboratorio/generate_envs.py
@@ -2,21 +2,54 @@ import os, json
 from shutil import copyfile
 import shutil
 import click
+from jsonschema import validate, ValidationError
 
 MODULE_DIR = "modules/simulated_app"
 OUT_DIR = "environments"
 
+# Esquemas JSON Schema
+NETWORK_SCHEMA = {
+    "type": "object",
+    "properties": {
+        "variable": {"type": "object"},
+        "resource": {"type": "object"}
+    },
+    "required": ["variable"]
+}
+
+MAIN_SCHEMA = {
+    "type": "object",
+    "properties": {
+        "resource": {"type": "array"},
+    },
+    "required": ["resource"]
+}
+
+# Función para validar JSON
+def validate_json(data, schema, filename):
+    try:
+        validate(instance=data, schema=schema)
+    except ValidationError as e:
+        raise SystemExit(f"Error: {filename} no pasa la validación JSON Schema:\n{e.message}")
+    else:
+        print(f"{filename} validado correctamente.")
+
+# Render y escritura
 def render_and_write(env):
     env_dir = os.path.join(OUT_DIR, env["name"])
     os.makedirs(env_dir, exist_ok=True)
 
-    # 1) Copia la definición de variables (network.tf.json)
-    copyfile(
-        os.path.join(MODULE_DIR, "network.tf.json"),
-        os.path.join(env_dir, "network.tf.json")
-    )
+    # 1) Copiar network.tf.json
+    src_file = os.path.join(MODULE_DIR, "network.tf.json")
+    dst_file = os.path.join(env_dir, "network.tf.json")
 
-    # 2) Genera main.tf.json con el puerto incluido
+    with open(src_file) as f:
+        net_data = json.load(f)
+        validate_json(net_data, NETWORK_SCHEMA, "network.tf.json")
+
+    copyfile(src_file, dst_file)
+
+    # 2) Generar main.tf.json
     config = {
         "resource": [
             {
@@ -47,6 +80,8 @@ def render_and_write(env):
         ]
     }
 
+    validate_json(config, MAIN_SCHEMA, "main.tf.json")
+
     with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
         json.dump(config, fp, sort_keys=True, indent=4)
 
@@ -55,7 +90,7 @@ def render_and_write(env):
 @click.option('--prefix', default='app', help='Prefijo de los entornos')
 @click.option('--port', default=8080, help='Puerto base simulado')
 def main(count, prefix, port):
-    """Genera entornos Terraform simulados."""
+    """Genera entornos Terraform simulados con validación de esquema."""
 
     ENVS = [
         {"name": f"{prefix}{i}", "network": f"net{i}", "port": port}
```

###  4. GitOps Local

- Implementa un script que, al detectar cambios en `modules/simulated_app/`, regenere **todas** las carpetas bajo `environments/`.
- Añade un hook de pre-commit que ejecute `jq --check` sobre los JSON.

#### Desarrollo

SSe agregó el script [`auto_regen_envs.py`](./Laboratorio/auto_regen_envs.py) que calcula un hash SHA256 de todos los archivos en modules/simulated_app/.  y compara con el hash guardado en .modules_hash_cache.json. Si detecta un cambio entonces ejecuta generate_envs.py con los parámetros predefinidos y actualiza el hash.

```python
#!/usr/bin/env python3
import os
import subprocess
import time
import hashlib
import json

MODULE_DIR = "modules/simulated_app"
ENV_DIR = "environments"
GENERATE_CMD = ["python3", "generate_envs.py", "--count", "3", "--prefix", "app", "--port", "3000"]
CACHE_FILE = ".modules_hash_cache.json"

def hash_directory(path):   # Devuelve un hash SHA256 de todos los archivos dentro del directorio.
    h = hashlib.sha256()
    for root, _, files in os.walk(path):
        for f in sorted(files):
            fp = os.path.join(root, f)
            with open(fp, "rb") as file:
                h.update(file.read())
    return h.hexdigest()

def load_cached_hash():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f).get("hash", "")
    return ""

def save_cached_hash(h):
    with open(CACHE_FILE, "w") as f:
        json.dump({"hash": h}, f)

def regen_envs():
    print("Cambios detectados en modules/simulated_app — Regenerando entornos...")
    subprocess.run(GENERATE_CMD, check=True)
    print("Entornos regenerados correctamente.\n")

def main():
    current_hash = hash_directory(MODULE_DIR)
    cached_hash = load_cached_hash()

    if current_hash != cached_hash:
        regen_envs()
        save_cached_hash(current_hash)
    else:
        print("No hay cambios en modules/simulated_app. Nada que regenerar.")

if __name__ == "__main__":
    main()
```

Ejemplo de un `.modules_hash_cache.json` generado:

```json
{"hash": "2e19da53ac981840d516984afaec67631c89265618afa7e01479e7c0c9357b44"}
```

Hook de pre-commit para validar JSONs con jq

```yaml
repos:
  - repo: local
    hooks:
      - id: check-json
        name: "Verificar sintaxis JSON con jq"
        entry: bash -c 'find . -type f -name "*.json" -exec jq --exit-status . {} \;'
        language: system
        types: [json]
```

Ejemplo de uso:

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ git add modules/ environments/
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2$ git commit -m "agregar modules y enviroments"
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/jquispe/.cache/pre-commit/patch1762129000-30167.
Verificar sintaxis JSON con jq...........................................Passed
[INFO] Restored changes from /home/jquispe/.cache/pre-commit/patch1762129000-30167.
[main c9882e0] agregar modules y enviroments
 18 files changed, 578 insertions(+)
 create mode 100644 environments/app1/main.tf.json
 create mode 100644 environments/app1/network.tf.json
 create mode 100644 environments/app_legacy/main.tf.json
 create mode 100644 environments/app_legacy/network.tf.json
 create mode 100644 environments/env1/main.tf.json
 create mode 100644 environments/env1/network.tf.json
 create mode 100644 environments/env2/main.tf.json
 create mode 100644 environments/env2/network.tf.json
 create mode 100644 environments/env3/main.tf.json
 create mode 100644 environments/env3/network.tf.json
 create mode 100644 environments/staging1/main.tf.json
 create mode 100644 environments/staging1/network.tf.json
 create mode 100644 environments/staging2/main.tf.json
 create mode 100644 environments/staging2/network.tf.json
 create mode 100644 environments/staging3/main.tf.json
 create mode 100644 environments/staging3/network.tf.json
 create mode 100644 modules/simulated_app/main.tf.json
 create mode 100644 modules/simulated_app/network.tf.json
```