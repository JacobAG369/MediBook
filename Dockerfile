# ===========================
# MediBook — Dockerfile
# ===========================
# Multi-stage build para una imagen de producción optimizada.
#
# Uso:
#   docker build -t medibook:latest .
#   docker run -p 8000:8000 --env-file .env medibook:latest

# ---------- Stage 1: Builder ----------
FROM python:3.13-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema para compilar psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar solo requirements primero (cache de Docker layers)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:3.13-slim AS runtime

# Metadata
LABEL maintainer="MediBook Team"
LABEL description="MediBook API — Sistema de gestión de citas médicas"
LABEL version="1.0.0"

# Instalar solo libpq (runtime, sin compilador)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copiar dependencias pre-instaladas del builder
COPY --from=builder /install /usr/local

# Crear usuario no-root por seguridad
RUN groupadd -r medibook && \
    useradd -r -g medibook -d /app -s /sbin/nologin medibook

WORKDIR /app

# Copiar el código fuente
COPY medibook/ ./medibook/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Copiar el entrypoint
COPY docker/entrypoint.sh .
RUN chmod +x entrypoint.sh

# Cambiar al usuario no-root
USER medibook

# Puerto de la API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Entrypoint: ejecuta migraciones y arranca la API
ENTRYPOINT ["./entrypoint.sh"]
