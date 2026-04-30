# medibook/main.py
"""
Entry point de la aplicacion MediBook.

Configura la instancia de FastAPI, monta los routers,
sirve archivos estaticos y define los metadatos de la documentacion.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from medibook.config.logging_config import setup_logging
from medibook.api.middleware import RequestLoggingMiddleware

from medibook.api.routes import appointments, doctors, health, patients
from medibook.api.routes import auth
from medibook.web.routes import router as web_router

# ---------- Metadata de la API ----------

DESCRIPTION = """
## MediBook API

Sistema de gestion de citas medicas construido con patrones de diseno GoF
y principios SOLID.

### Patrones de Diseno Integrados

| Patron | Uso en la API |
|---|---|
| **Factory Method** | `POST /appointments` — selecciona el workflow |
| **Template Method** | Flujo de creacion de citas paso a paso |
| **Observer** | Notificaciones automaticas al crear citas |
| **Prototype** | `POST /appointments/{id}/clone` — clona citas |
| **Decorator** | `GET /appointments/{id}/summary` — resumen dinamico |
| **Flyweight** | `POST /doctors` — reutiliza especialidades existentes |
| **Singleton** | Configuracion global de la clinica |

### Seguridad

- Autenticacion JWT (Bearer Token)
- RBAC con roles: ADMIN, DOCTOR, RECEPTIONIST, PATIENT
- Hash bcrypt para contrasenas
- Usa el boton **Authorize** arriba para autenticarte
"""

TAGS_METADATA = [
    {
        "name": "Autenticacion",
        "description": "Registro, login y gestion de sesiones JWT.",
    },
    {
        "name": "Citas Medicas",
        "description": "Operaciones CRUD y patrones de diseno sobre citas.",
    },
    {
        "name": "Doctores",
        "description": "Gestion de doctores y sus especialidades.",
    },
    {
        "name": "Pacientes",
        "description": "Registro y gestion de pacientes.",
    },
    {
        "name": "Health",
        "description": "Verificacion de salud del sistema.",
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

# ---------- Archivos Estaticos ----------

app.mount("/static", StaticFiles(directory="medibook/web/static"), name="static")

# ---------- Logging y Middleware ----------

setup_logging(level="INFO")
app.add_middleware(RequestLoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Registrar Routers ----------

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(appointments.router, prefix=API_PREFIX)
app.include_router(doctors.router, prefix=API_PREFIX)
app.include_router(patients.router, prefix=API_PREFIX)

# Web frontend (debe ir al final para que "/" no bloquee las rutas API)
app.include_router(web_router)
