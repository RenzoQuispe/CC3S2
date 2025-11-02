# Actividad: Escribiendo infraestructura como código en un entorno local con Terraform

##  Fase 1: Expresando el cambio de infraestructura

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


   Editamos manualmente terraform.tfstate: cambiar "name":"app2" ->"hacked-app". Ahora tras ejecutar terraform plan, Terraform verá que el estado real (modificado) no coincide con el código (main.tf.json) y propondrá corregirlo.

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

    Tras ejecutar terraform apply, Terraform restaurará el estado a "app2".
   
### B. Migrando a IaC

   El script creado es [`migracion_IaC.py`](./Laboratorio/migracion_IaC.py)

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

    Se agregó el script [`generate_envs2.py`](./Laboratorio/generate_envs2.py) el cual genera entornos Terraform a partir de la plantilla base. Para cada entorno definido en la lista ENVS, copia la plantilla network.tf.json y genera un main.tf.json con un recurso null_resource que incluye triggers y un provisioner local-exec que  imprime un mensaje de arranque usando las variables name, network y port. También permite que unas redes dependan de otras, como env3 que hereda y modifica la red de env2, haciendo que toda la configuración sea declarativa y reproducible.

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

* ¿Cómo extenderías este patrón para 50 módulos y 100 entornos?

   Organizaría los módulos de manera que cada uno sea independiente y tenga su propia plantilla network.tf.json y main.tf.json. Luego usaría un generador en Python que recorra una lista de entornos y módulos para crear automáticamente las carpetas y archivos, aplicando variables diferentes por entorno. Así puedo mantener todo reproducible sin tener que tocar cada archivo manualmente, y si cambio algo en la plantilla base, se propaga a todos los entornos.

* ¿Qué prácticas de revisión de código aplicarías a los `.tf.json`?

   Le pondría énfasis a la consistencia y legibilidad, verificaria que las claves estén bien indentadas, usaria jq para formateo automático, y revisar que los valores por defecto y descripciones sean claros. También que los commits tengan mensajes específicos explicando los cambios de infraestructura, y que no se modifiquen directamente los JSON generados, solo las plantillas o el generador Python.

* ¿Cómo gestionarías secretos en producción (sin Vault)?

   Usaría variables sensibles en Terraform ("sensitive": true) y pasaría los secretos mediante variables de entorno (TF_VAR_*) o archivos .tfvars que no se suban a git, nunca los pondría en los JSON ni en el código.

* ¿Qué workflows de revisión aplicarías a los JSON generados?

   Para los JSON generados, revisaría siempre el generador Python y las plantillas, no los JSON directamente, porque en este caso son artefactos dependientes. Se puede usar hooks de pre-commit que corran jq para formatearlos automáticamente y que verifiquen que no se cambien valores sensibles accidentalmente.
