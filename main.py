# medibook/main.py
"""
Entry point de la aplicación MediBook.

Configura la instancia de FastAPI, monta los routers
y define los metadatos de la documentación.
"""

from fastapi import FastAPI

from medibook.config.logging_config import setup_logging
from medibook.api.middleware import RequestLoggingMiddleware

from medibook.api.routes import appointments, doctors, health, patients

# ---------- Metadata de la API ----------

DESCRIPTION = """
## 🏥 MediBook API

Sistema de gestión de citas médicas construido con patrones de diseño GoF.

### Patrones de Diseño Integrados

| Patrón | Uso en la API |
|---|---|
| **Factory Method** | `POST /appointments` — selecciona el workflow |
| **Template Method** | Flujo de creación de citas paso a paso |
| **Observer** | Notificaciones automáticas al crear citas |
| **Prototype** | `POST /appointments/{id}/clone` — clona citas |
| **Decorator** | `GET /appointments/{id}/summary` — resumen dinámico |
| **Flyweight** | `POST /doctors` — reutiliza especialidades existentes |
| **Singleton** | Configuración global de la clínica |
"""

TAGS_METADATA = [
    {
        "name": "Citas Médicas",
        "description": "Operaciones CRUD y patrones de diseño sobre citas.",
    },
    {
        "name": "Doctores",
        "description": "Gestión de doctores y sus especialidades.",
    },
    {
        "name": "Pacientes",
        "description": "Registro y gestión de pacientes.",
    },
    {
        "name": "Health",
        "description": "Verificación de salud del sistema.",
    },
]

# ---------- Instancia de FastAPI ----------

app = FastAPI(
    title="MediBook API",
    version="1.0.0",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------- Logging y Middleware ----------

setup_logging(level="INFO")
app.add_middleware(RequestLoggingMiddleware)

# ---------- Registrar Routers ----------

API_PREFIX = "/api/v1"

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(appointments.router, prefix=API_PREFIX)
app.include_router(doctors.router, prefix=API_PREFIX)
app.include_router(patients.router, prefix=API_PREFIX)


# ---------- Root ----------

@app.get("/", tags=["Root"], include_in_schema=False)
def root():
    """Redirige a la documentación de la API."""
    return {
        "app": "MediBook API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
