# medibook/main.py
"""
Entry point de la aplicacion MediBook.

Configura la instancia de FastAPI, monta los routers,
sirve archivos estaticos y define los metadatos de la documentacion.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from medibook.config.logging_config import setup_logging
from medibook.api.middleware import RequestLoggingMiddleware

from medibook.api.routes import appointments, doctors, health, patients
from medibook.api.routes import auth
from medibook.web.routes import router as web_router

# Carga variables de entorno al inicio
load_dotenv()

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

# CORS — orígenes permitidos desde variable de entorno
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# SessionMiddleware — necesario para sesiones server-side (p. ej. flash messages)
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    raise RuntimeError("SECRET_KEY no está definida en las variables de entorno")
app.add_middleware(
    SessionMiddleware,
    secret_key=_secret_key,
    session_cookie="medibook_session",
    max_age=3600,          # 1 hora
    https_only=False,      # Cambiar a True en producción con HTTPS
    same_site="lax",
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
