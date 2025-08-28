## Actividad 2:  HTTP, DNS, TLS y 12-Factor (port binding, configuración, logs)

**Objetivo:** practicar despliegues **seguros y reproducibles** combinando aplicación (HTTP), resolución de nombres (DNS), cifrado en tránsito (TLS) y buenas prácticas**12-Factor** (variables de entorno, port binding y logs a stdout).

#### Comando a utilizar

* **HTTP:** `curl -v/-i/-X`, `httpie` (opcional).
* **Puertos/Red:** `ss -ltnp`, `lsof -i`, `ip a`, `ip route`.
* **DNS:** `dig +short`, `dig @1.1.1.1 example.com`, `getent hosts`.
* **TLS:** `openssl s_client -connect host:443 -servername host -brief`.
* **Logs/Servicios:** `journalctl -u nginx`, `tail -f /var/log/nginx/error.log`, `systemctl status` / `service status`.;

#### Resultado esperado

* Acceso **HTTP** en `127.0.0.1:8080` (port binding por entorno). Respuesta JSON con `message` y `release`. **Logs** en stdout.;
* Resolución de `miapp.local` vía *hosts* para pruebas.;
* Acceso **HTTPS** en `miapp.local:443` con Nginx como *reverse proxy* a `127.0.0.1:8080`. *Handshake* válido y evidencia de cabeceras `X-Forwarded-*`.;

### 1) HTTP: Fundamentos y herramientas

**Meta:** ver anatomía petición/respuesta, métodos y códigos.

1. **Levanta la app** con variables de entorno (12-Factor):
   `PORT=8080 MESSAGE="Hola CC3S2" RELEASE="v1" python3 app.py` (usa tu *venv*). La app **escucha** en el puerto indicado y **loggea en stdout**. Incluye extracto de salida (stdout) en el reporte.

   ![](./img/1.1.png)

3. **Inspección con `curl`:**

   * `curl -v http://127.0.0.1:8080/` (cabeceras, código de estado, cuerpo JSON).

      ![](./img/1.2.1.png)
   
   * `curl -i -X POST http://127.0.0.1:8080/` (explica qué ocurre si no hay ruta/método).

      ![](./img/1.2.2.png)

      No hay ruta o método definido, entonces responde 405

   * **Pregunta guía:** ¿Qué campos de respuesta cambian si actualizas `MESSAGE`/`RELEASE` sin reiniciar el proceso? Explica por qué.

      Las variables de entorno se leen al momento de iniciar el proceso, Si no reiniciamos, la app sigue usando los valores que leyó al arrancar, el JSON de respuesta no cambia.

4. **Puertos abiertos con `ss`:**

   * `ss -ltnp | grep :8080` (evidencia del proceso y socket).

      ![](./img/1.3.png)

      La aplicacion python3 esta corriendo en el puerto 8080, el puerto es modo LISTEN(esperando conexiones), pero solo accesible desde la misma máquina.

5. **Logs como flujo:** Demuestra que los logs salen por stdout (pega 2–3 líneas). Explica por qué **no** se escriben en archivo (12-Factor). Herramientas: `curl`, `ss`, `lsof` (opcional para PID/FD), `journalctl` (si corres como servicio).

   ![](./img/1.4.png)

   No hay archivo porque la app sigue la práctica 12-Factor: los logs van a stdout/stderr, y el entorno decide si los redirige a fichero, syslog, journald u otro.


### 2) DNS: nombres, registros y caché

**Meta:** resolver `miapp.local` y observar TTL/caché.

1. **Hosts local:** agrega `127.0.0.1 miapp.local` (Linux y/o Windows según tu entorno). Usa el *target* de la guía si está disponible (`make hosts-setup`).

   ![](./img/2.1.png)

2. **Comprueba resolución:**

   * `dig +short miapp.local` (debe devolver `127.0.0.1`).
   * `getent hosts miapp.local` (muestra la base de resolución del sistema).

      ![](./img/2.2.png)

      - Prueba con dig: error (porque no hay zona DNS que conozca miapp.local). 
      - Prueba con getent: éxito (127.0.0.1 miapp.local) gracias a que consulta directamente al archivo etc/hosts

3. **TTL/caché (conceptual):** con `dig example.com A +ttlunits` explica cómo el TTL afecta respuestas repetidas (no cambies DNS público, solo observa).

   ![](./img/2.3.1.png)

   Preguntamos al DNS configurado en el sistema la dirección IPv4 de example.com y muestra cuánto tiempo se puede cachear cada respuesta. En mi salida, los registros A de example.com tienen un TTL de 5m. Esto significa que durante ese tiempo las respuestas se sirven desde caché y el TTL va disminuyendo en consultas repetidas. Una vez que expira, el resolver vuelve a consultar al servidor DNS para obtener datos frescos.

   ![](./img/2.3.2.png)

4. **Pregunta guía:** ¿Qué diferencia hay entre **/etc/hosts** y una zona DNS autoritativa? ¿Por qué el *hosts* sirve para laboratorio? Explica en 3–4 líneas. Herramientas: `dig`, `getent`, `resolv.conf`/`resolvectl` (si aplica).

   - /etc/hosts es un archivo local, las entradas están solo en mi máquina, tienen prioridad inmediata y no es escalable.
   - Una DNS autoritativa es distribuida: un servidor administra nombres de un dominio y responde consultas de todo Internet, con TTL y caché.
   - El hosts es útil en laboratorio porque permite simular un nombre de dominio sin montar infraestructura DNS real.

### 3) TLS: seguridad en tránsito con Nginx como *reverse proxy*

**Meta:** terminar TLS en Nginx `:443` y *proxyear* a Flask en `127.0.0.1:8080`.

1. **Certificado de laboratorio:** genera autofirmado (usa el *target* `make tls-cert` si existe) y coloca crt/key donde lo espera Nginx (ver guía).

   ![](./img/3.1.png)

2. **Configura Nginx:** usa el ejemplo provisto para **terminación TLS** y **proxy\_pass** a `http://127.0.0.1:8080;` con cabeceras `X-Forwarded-*`. Luego `nginx -t` y **reinicia** el servicio.
   Incluye el *snippet* clave de tu `server` en el reporte.

   ![](./img/3.2.png)

3. **Valida el *handshake*:**

   * `openssl s_client -connect miapp.local:443 -servername miapp.local -brief` (muestra TLSv1.2/1.3, cadena, SNI).

      Validacion de handshake:

      ![](./img/3.3.1.png)

   * `curl -k https://miapp.local/` (explica el uso de `-k` con certificados autofirmados).

      La opción -k se usa porque el certificado es autofirmado, no está en la lista de autoridades de confianza del sistema, así que curl lo rechazaría si no usamos -k

      ![](./img/3.3.2.png)

5. **Puertos y logs:**

   * `ss -ltnp | grep -E ':(443|8080)'` (evidencia de ambos sockets).

      ![](./img/3.4.1.png)

   * `journalctl -u nginx -n 50 --no-pager` **o** `tail -n 50 /var/log/nginx/error.log` (pega 3–5 líneas relevantes).

      - sudo journalctl -u nginx -n 50 --no-pager

         ![](./img/3.4.2.2.png)

      - cat /var/log/nginx/access.log

         ![](./img/3.4.2.1.png)

> Nota: el *vínculo*  Nginx->Flask es **HTTP interno** en `127.0.0.1:8080`, tu cliente entra por **HTTPS** en `:443`.

### 4) 12-Factor App: port binding, configuración y logs

**Meta:** demostrar tres principios clave en tu app.

1. **Port binding:** muestra que la app **escucha** en el puerto indicado por `PORT` (evidencia `ss`).

   ![](./img/4.1.png)

2. **Config por entorno:** ejecuta dos veces con distintos `MESSAGE`/`RELEASE` y documenta el efecto en la respuesta JSON.

   ```Makefile
   # Variables (12-Factor)
   APP_NAME ?= miapp
   DOMAIN   ?= miapp.local
   PORT     ?= 8080
   MESSAGE  ?= Hola CC3S2
   RELEASE  ?= v1
   ```

   ```Python
   # 12-Factor: configuración vía variables de entorno (sin valores codificados)
   PORT = int(os.environ.get("PORT", "8080"))
   MESSAGE = os.environ.get("MESSAGE", "Hola CC3S2")
   RELEASE = os.environ.get("RELEASE", "v1")
   ```

   ![](./img/4.2.1.png)

   ```Makefile
   # Variables (12-Factor)
   APP_NAME ?= miapp
   DOMAIN   ?= miapp.local
   PORT     ?= 8080
   MESSAGE  ?= hola CC3S2 2025-2
   RELEASE  ?= v2
   ```

   ```Python
   # 12-Factor: configuración vía variables de entorno (sin valores codificados)
   PORT = int(os.environ.get("PORT", "8080"))
   MESSAGE = os.environ.get("MESSAGE", "Hola CC3S2 2025-2")
   RELEASE = os.environ.get("RELEASE", "v2")
   ```

   ![](./img/4.2.2.png)


3. **Logs a stdout:** redirige a archivo mediante *pipeline* de shell y adjunta 5 líneas representativas. Explica por qué **no** se configura *log file* en la app.

   ![](./img/4.3.1.png)

   ![](./img/4.3.2.png)

### 5) Operación reproducible (Make/WSL/Linux)

**Meta:** empaquetar tu flujo en `make` o scripts para repetirlo en otra máquina.

* Sigue la guía paso a paso (Linux/WSL) y **documenta divergencias** (p.ej. `systemctl` vs `service` en WSL, *hosts* de Windows vs WSL).
  Incluye una tabla "Comando -> Resultado esperado".
* Si tienes *targets* como `make prepare`, `make run`, `make nginx`, `make check-http`, `make check-tls`, `make dns-demo`, úsalos y pega su salida resumida.

   Flask:

   ![](./img/5.1.png)

   Flask - Nginx:

   ![](./img/5.2.png)

   Pruebas:

   ![](./img/5.3.png)
  

### Mejora incremental 

* **Logs estructurados** (JSON por línea) en stdout. Muestra un ejemplo y por qué facilita *parsing*.

   ![](./img/6.1.1.png)

   ![](./img/6.1.2.png)

   Ahora varios programas pueden parsear automáticamente los eventos de la app sin depender de expresiones regulares.

* **Script `make`** que haga *end-to-end*: preparar venv -> levantar app -> cert TLS -> Nginx -> chequeos `curl/dig/ss`.;

   El Makefile proporcionado cumple lo pedido:

   ![](./img/6.2.png)

* **`systemd`** (si aplica): define unidad para la app y valida con `systemctl status` y `journalctl -u`. (Adjunta *snippet* clave y evidencia).

   La idea es que se registre la app como servicio del sistema, para que ya no dependas de tener la terminal abierta ni de make run. Esta automatizado en el Makefile, para conseguir esto:

   ```
   make prepare
   make systemd-install
   ```
   ![](./img/6.3.1.png)

   ![](./img/6.3.2.png)

   Pruebas:

   ![](./img/6.3.3.png)

### Preguntas guía

1. **HTTP:** explica **idempotencia** de métodos y su impacto en *retries*/*health checks*. Da un ejemplo con `curl -X PUT` vs `POST`.

   La idempotencia significa que ejecutar un mismo método varias veces produce siempre el mismo resultado, si un cliente hace un PUT /usuario/1 con un JSON que cambia el nombre a “Renzo”, si lo ejecuta una vez o diez veces el estado final del recurso sera el mismo, en cambio, un POST no es idempotente porque cada petición puede generar un nuevo recurso(si no agrega restricciones). Esta diferencia impacta en los retries y health checks, ya que reintentar un GET o un PUT es seguro, reintentar un POST puede generar errores en la app.

2. **DNS:** ¿por qué `hosts` es útil para laboratorio pero no para producción? ¿Cómo influye el **TTL** en latencia y uso de caché?;

   El archivo /etc/hosts es útil en laboratorio porque permite traducir nombres como miapp.local a 127.0.0.1 de forma rápida y sin necesidad de levantar usar un servidor DNS. Sin embargo, en producción no es viable porque no escala: cada máquina tendría que configurarse manualmente, lo cual dificulta las posibles actualizaciones de direcciones IP; en un entorno real, la resolución debe delegarse a servidores DNS. El valor de TTL en DNS influye en la latencia y el caché ya que un TTL bajo permite propagar cambios de IP rápidamente, pero aumenta la carga de consultas al DNS y un TTL alto mejora el rendimiento por caché, aunque retrasa la visibilidad de cambios.

3. **TLS:** ¿qué rol cumple **SNI** en el *handshake* y cómo lo demostraste con `openssl s_client`?

   El SNI es una extensión de TLS que permite al cliente indicar en el handshake el nombre del dominio al que quiere conectarse, esto es importante cuando un mismo servidor o IP aloja múltiples sitios con certificados distintos, ya que sin SNI el servidor no sabría qué certificado devolver, se puede demostrar con un comando como openssl s_client -connect miapp.local:443 -servername miapp.local, donde el parámetro -servername envía el SNI y el servidor responde con el certificado correcto asociado a ese dominio.

   ![](./img/3.3.1.png)

4. **12-Factor:** ¿por qué **logs a stdout** y **config por entorno** simplifican contenedores y CI/CD?

   Uno de los principios de las aplicaciones 12-Factor es que los logs deben emitirse a stdout como un flujo continuo de eventos, entonces el sistema donde corre la app (systemd, Docker, etc) captura la salida estándar y la integra con sistemas de monitoreo o centralización de logs, sin necesidad de que la aplicación gestione archivos, ademas es importante que la configuración debe obtenerse de variables de entorno y no estar incrustada en el código, esto simplifica los despliegues en CI/CD porque la misma imagen de la aplicación puede usarse en desarrollo, pruebas o producción, cambiando únicamente las variables de entorno.

5. **Operación:** ¿qué muestra `ss -ltnp` que no ves con `curl`? ¿Cómo triangulas problemas con `journalctl`/logs de Nginx?;

   El comando curl sirve para comprobar si un servicio responde correctamente, pero no muestra si el proceso está realmente escuchando en el puerto, en cambio ss -ltnp revela los sockets abiertos, el puerto y el proceso asociado, permitiendo saber si la aplicación está vinculada a la dirección correcta, esto ayuda a diferenciar entre un problema de red-aplicación o de configuración del servicio. La idea de diagnosticar problemas es que si curl falla, se revisa con ss si el puerto está escuchando, y si lo está, entonces se consultan los logs con journalctl -u miapp.service o los registros de Nginx para identificar errores en la aplicación.
