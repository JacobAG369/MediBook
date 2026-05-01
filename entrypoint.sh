#!/bin/sh
# ===========================
# MediBook — Entrypoint
# ===========================
# Ejecuta las migraciones de Alembic y luego arranca la API.

set -e

echo "🏥 MediBook — Iniciando..."

# 1. Ejecutar migraciones pendientes
echo "📦 Aplicando migraciones de base de datos..."
python -m alembic upgrade head

echo "✅ Migraciones aplicadas."

# 2. Crear usuario admin si no existe
echo "👤 Verificando usuario administrador..."
python -m medibook.scripts.seed_admin

# 3. Arrancar la API con Uvicorn
echo "🚀 Iniciando servidor en puerto 8000..."
exec uvicorn medibook.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "${UVICORN_WORKERS:-2}" \
    --log-level info
