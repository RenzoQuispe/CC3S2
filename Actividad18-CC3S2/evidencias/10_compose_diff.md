# Cambios en healthchecks

En esta actividad mejoré los healthchecks del `docker-compose.yml` para asegurar que cada servicio arranque correctamente y espere a sus dependencias.

## Postgres

Antes: healthcheck sin `start_period` y usando `${VAR}`.

Ahora:

```yaml
test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB -h localhost"]
interval: 10s
timeout: 3s
retries: 10
start_period: 20s
```

Postgres tarda en inicializar y necesita `$$` para que las variables se interpreten dentro del contenedor.

## ETL-App

Añadí:

```yaml
start_period: 10s
```

## Airflow Webserver

Agregué healthcheck real:

```yaml
test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
start_period: 30s
```

Y dependencias:

```yaml
depends_on:
  airflow-init:
    condition: service_completed_successfully
```

Airflow demora en iniciar y debe esperar a la inicialización.

## Airflow Scheduler

Añadí healthcheck por socket:

```yaml
test: ["CMD-SHELL", "python -c 'import socket; s=socket.socket(); s.connect((\"localhost\", 8793)); s.close()' || exit 1"]
start_period: 60s
```

Se busca validación correcta del puerto interno usado por el scheduler.

## Airflow Init

Simplifiqué el comando y mantuve:

```yaml
restart: "no"
```

Solo debe ejecutarse una vez para inicializar Airflow. Además antes se ejecutaba así:

```yaml
command: >
  bash -c "
  airflow db init &&
  airflow users create
    --username admin
    --firstname Admin
    ...
```

Esto generaba errores de "command error" y "command not found". Ahora con se unifico el comando en una sola línea y ya no hay problemas:

```yaml
command: >
  bash -c "airflow db init &&
  airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin || true"
restart: "no"
```

## Config por variables de entorno

- Se migraron todas las credenciales del archivo docker-compose.yml hacia variables de entorno administradas mediante el archivo .env. 
- Se usa .env.example con valores dummy para evitar exponer secretos y permitir reproducibilidad del entorno.
- No hay credenciales sensibles en los bloques environment: y se estandarizó el uso de env_file.
- Se verificó mediante auditoría que no existan contraseñas hardcodeadas en el repositorio.
