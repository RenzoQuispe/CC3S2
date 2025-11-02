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