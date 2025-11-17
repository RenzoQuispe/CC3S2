# Stage 1: build

FROM python:3.12-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential gcc \
 && pip install --upgrade pip \
 && python -m venv /venv \
 && . /venv/bin/activate \
 && pip install -r requirements.txt \
 && apt-get purge -y build-essential gcc \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Stage 2: runtime

FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    busybox \
  && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear usuario no-root (UID estable)
RUN useradd --create-home --uid 10001 etluser

WORKDIR /app

# Copiar venv (root propiedad ok)
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copiar código con ownership NO-ROOT → CLAVE
COPY --chown=etluser:etluser pipeline.py ./pipeline.py
COPY --chown=etluser:etluser healthcheck.py ./healthcheck.py
COPY --chown=etluser:etluser data ./data

# Ahora sí bajamos privilegios
USER etluser

ENTRYPOINT ["python", "pipeline.py"]
