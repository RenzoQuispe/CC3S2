## Topología y superficie expuesta

En este laboratorio utilizo tres servicios principales: `airflow-webserver`, `airflow-scheduler` y `postgres`. Todos ellos están conectados a una la red `laboratorio_backend` que fue creada automáticamente por Docker Compose. Esta red es de tipo bridge y actúa como un segmento LAN interno donde los contenedores se comunican usando el DNS incorporado de Docker. Gracias a esto, no necesito direcciones IP fijas: basta con usar el nombre del servicio como hostname. Lo comprobé ejecutando un contenedor temporal de Alpine dentro de la red y verificando:
-  airflow-webserver responde en 172.18.0.3
-  postgres responde en 172.18.0.2

También probé resolución DNS y reachability mediante curl, verificando que la comunicación interna funciona correctamente.

### Servicios y puertos expuestos

- airflow-webserver publica el puerto 8080 hacia el host (0.0.0.0:8080->8080), permitiendo acceso desde el navegador.
- airflow-scheduler no expone puertos al host (solo se comunica internamente).
- postgres tampoco expone puertos externos; solo escucha en 5432/tcp dentro de la red interna.

Este diseño es intencional: Postgres y el scheduler no deberían exponerse al host, ya que solo Airflow Webserver necesita recibir conexiones externas. Reducir la superficie expuesta disminuye riesgos y evita accesos indebidos.

### Consideración adicional

Dado que el laboratorio funciona con varios servicios que solo deben comunicarse entre sí, sería recomendable mover la topología a una user-defined bridge exclusiva, tal como laboratorio_backend, para garantizar aislamiento de tráfico, control de IPs y un mejor manejo de DNS interno, en lugar de depender de la red bridge por defecto.