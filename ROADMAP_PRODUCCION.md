# 🏥 MediBook — Roadmap de Producción

> **Documento de Arquitectura e Ingeniería**
> Ruta por fases para llevar el proyecto MediBook desde su estado actual de prototipo académico a un sistema de producción robusto, escalable y seguro.

---

## 📊 Diagnóstico del Estado Actual

| Aspecto | Estado | Veredicto |
|---|---|---|
| Modelos de dominio (ORM) | ✅ Implementados | Funcional |
| Patrones de diseño (GoF) | ✅ 7 patrones implementados | Sólido |
| API / Capa Web | ❌ Vacía (`web/` sin rutas) | **Crítico** |
| Testing | ❌ Inexistente | **Crítico** |
| Autenticación / Autorización | ❌ No implementada | **Crítico** |
| Gestión de dependencias | ❌ Sin `requirements.txt` | **Crítico** |
| Variables de entorno | ⚠️ Usa `.env` pero sin `.env.example` ni `.gitignore` | Riesgo |
| Migraciones de BD | ❌ Solo `create_all()` manual | Deficiente |
| Logging | ❌ Solo `print()` en consola | Deficiente |
| Documentación | ⚠️ README con conflictos de merge | Deficiente |
| CI/CD | ❌ Inexistente | Pendiente |
| Contenedorización | ❌ Inexistente | Pendiente |
| Monitoreo / Observabilidad | ❌ Inexistente | Pendiente |

### Deuda Técnica Identificada

1. **Conflictos de merge sin resolver** en `README.md` (marcas `<<<<<<<` visibles).
2. **`__init__.py` de `services/`** tiene imports duplicados y doble declaración de `__all__`.
3. **Sesiones de BD desacopladas:** cada método crea su propia `SessionLocal()` sin inyección de dependencias. Esto dificulta el testing y puede causar *session leaks*.
4. **`check_availability()` es un stub vacío** — sin lógica real de validación de horarios.
5. **Flyweight cache (`SpecialtyFlyweightFactory`)** usa un `Dict` de clase que puede causar problemas de *thread-safety* en entornos concurrentes.
6. **Sin validación de datos de entrada** más allá de campos requeridos mínimos.

---

## 🗺️ Visión General de Fases

```mermaid
gantt
    title Roadmap MediBook → Producción
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Fase 0 - Fundamentos
    Higiene del repo y dependencias       :f0a, 2026-04-23, 2d
    Configuración de entorno              :f0b, after f0a, 1d

    section Fase 1 - API REST
    Diseño de endpoints                   :f1a, after f0b, 2d
    Implementación con FastAPI            :f1b, after f1a, 5d
    Validación con Pydantic               :f1c, after f1a, 3d

    section Fase 2 - Calidad
    Testing unitario e integración        :f2a, after f1b, 5d
    Logging estructurado                  :f2b, after f1b, 2d
    Migraciones con Alembic               :f2c, after f1b, 3d

    section Fase 3 - Seguridad
    Autenticación JWT                     :f3a, after f2a, 4d
    Autorización por roles                :f3b, after f3a, 3d
    Rate limiting y hardening             :f3c, after f3b, 2d

    section Fase 4 - Infraestructura
    Dockerización                         :f4a, after f3c, 3d
    CI/CD pipeline                        :f4b, after f4a, 3d
    Despliegue staging                    :f4c, after f4b, 2d

    section Fase 5 - Producción
    Monitoreo y observabilidad            :f5a, after f4c, 3d
    Despliegue producción                 :f5b, after f5a, 2d
    Documentación final                   :f5c, after f5b, 2d
```

---

## Fase 0 — Fundamentos e Higiene del Repositorio

> **Objetivo:** Establecer las bases mínimas para que el proyecto sea reproducible, seguro y colaborativo.

### 0.1 Gestión de Dependencias

- [ ] Crear `requirements.txt` con versiones fijas (*pinned*):
  ```txt
  sqlalchemy==2.0.*
  python-dotenv==1.0.*
  fastapi==0.115.*
  uvicorn[standard]==0.34.*
  pydantic==2.*
  alembic==1.14.*
  pytest==8.*
  httpx==0.28.*
  ```
- [ ] Crear `pyproject.toml` (alternativa moderna con sección `[project.dependencies]`).

### 0.2 Seguridad del Repositorio

- [ ] Crear `.gitignore` completo:
  ```gitignore
  __pycache__/
  *.pyc
  .env
  *.db
  *.sqlite3
  .venv/
  venv/
  dist/
  *.egg-info/
  .pytest_cache/
  ```
- [ ] Crear `.env.example` con placeholders:
  ```env
  DATABASE_URL=postgresql://usuario:password@localhost:5432/medibook_db
  SECRET_KEY=cambiar-esta-clave-secreta
  DEBUG=true
  ```
- [ ] **Verificar que `.env` NO esté en el historial de Git.** Si lo está, rotear credenciales y purgar con `git filter-branch` o BFG.

### 0.3 Limpieza de Deuda Técnica

- [ ] Resolver conflictos de merge en `README.md`.
- [ ] Limpiar imports duplicados en `services/__init__.py`.
- [ ] Escribir un `README.md` profesional con:
  - Descripción del proyecto.
  - Instrucciones de instalación y ejecución.
  - Estructura del proyecto.
  - Patrones de diseño documentados.

### 0.4 Estructura de Proyecto Propuesta

```
medibook-pattern/
├── medibook/
│   ├── __init__.py
│   ├── main.py                  ← [NUEVO] Entry point FastAPI
│   ├── config/
│   │   ├── __init__.py
│   │   ├── booking_config.py    ← Singleton (mantener)
│   │   └── settings.py          ← [NUEVO] Pydantic Settings
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── appointment.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── specialty.py
│   ├── infra/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── repositories/       ← [NUEVO] Patrón Repository
│   │       ├── __init__.py
│   │       ├── appointment_repo.py
│   │       ├── doctor_repo.py
│   │       └── patient_repo.py
│   ├── services/                ← Lógica de negocio (mantener)
│   │   └── ...
│   ├── api/                     ← [NUEVO] Capa de API
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── appointments.py
│   │   │   ├── doctors.py
│   │   │   ├── patients.py
│   │   │   └── auth.py
│   │   ├── schemas/             ← DTOs con Pydantic
│   │   │   ├── appointment.py
│   │   │   ├── doctor.py
│   │   │   └── patient.py
│   │   ├── dependencies.py      ← Inyección de dependencias
│   │   └── middleware.py
│   ├── scripts/
│   │   └── init_db.py
│   └── web/                     ← Frontend (fase posterior)
├── tests/                       ← [NUEVO]
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/                     ← [NUEVO] Migraciones
├── docker/                      ← [NUEVO]
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## Fase 1 — API REST con FastAPI

> **Objetivo:** Exponer toda la lógica de negocio existente a través de endpoints HTTP seguros y documentados.

### 1.1 Diseño de Endpoints

| Método | Ruta | Descripción | Servicio Interno |
|---|---|---|---|
| `POST` | `/api/v1/appointments` | Crear cita (presencial u online) | `BookingService.create_appointment()` |
| `POST` | `/api/v1/appointments/{id}/clone` | Clonar cita (Prototype) | `BookingService.clone_appointment()` |
| `GET` | `/api/v1/appointments/{id}/summary` | Resumen decorado | `BookingService.get_decorated_summary()` |
| `GET` | `/api/v1/appointments` | Listar citas con filtros | Nuevo |
| `GET` | `/api/v1/appointments/{id}` | Detalle de cita | Nuevo |
| `PATCH` | `/api/v1/appointments/{id}` | Actualizar cita | Nuevo |
| `DELETE` | `/api/v1/appointments/{id}` | Cancelar cita | Nuevo |
| `POST` | `/api/v1/doctors` | Crear doctor con especialidad | `BookingService.create_doctor_with_specialty()` |
| `GET` | `/api/v1/doctors` | Listar doctores | Nuevo |
| `POST` | `/api/v1/patients` | Crear paciente | Nuevo |
| `GET` | `/api/v1/patients` | Listar pacientes | Nuevo |
| `POST` | `/api/v1/auth/login` | Autenticación (Fase 3) | Nuevo |
| `GET` | `/api/v1/health` | Health check | Nuevo |

### 1.2 Schemas (DTOs) con Pydantic

```python
# medibook/api/schemas/appointment.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    appointment_type: str = Field(default="in_person", pattern="^(in_person|online|teleconsulta)$")
    notes: Optional[str] = Field(default=None, max_length=255)
    meeting_link: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int
    status: str
    notes: Optional[str]
    meeting_link: Optional[str]

    model_config = {"from_attributes": True}
```

### 1.3 Inyección de Dependencias (Refactor Clave)

> **Problema actual:** `SessionLocal()` se instancia directamente dentro de cada método del servicio. Esto hace imposible testear con una BD de prueba o mockear la sesión.

**Solución:** Usar el sistema de `Depends()` de FastAPI:

```python
# medibook/api/dependencies.py
from medibook.infra.db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Refactorear `BookingService` para recibir `session` como parámetro en lugar de crear sesiones internamente.

### 1.4 Entry Point

```python
# medibook/main.py
from fastapi import FastAPI
from medibook.api.routes import appointments, doctors, patients

app = FastAPI(
    title="MediBook API",
    version="1.0.0",
    description="Sistema de gestión de citas médicas",
)

app.include_router(appointments.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
```

---

## Fase 2 — Calidad, Testing y Observabilidad

> **Objetivo:** Garantizar la estabilidad del sistema con pruebas automatizadas, logging profesional y migraciones controladas.

### 2.1 Testing

#### Estructura de Tests

```
tests/
├── conftest.py              ← Fixtures globales (BD de prueba en SQLite)
├── unit/
│   ├── test_appointment_factory.py
│   ├── test_appointment_prototype.py
│   ├── test_appointment_decorators.py
│   ├── test_observers.py
│   └── test_specialty_flyweight.py
└── integration/
    ├── test_booking_service.py
    └── test_api_appointments.py
```

#### Fixture Global para BD de Prueba

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from medibook.infra.db import Base

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

#### Cobertura Mínima Requerida

| Componente | Tipo de Test | Cobertura Mínima |
|---|---|---|
| `AppointmentFactory` | Unitario | 100% |
| `AppointmentPrototype.clone()` | Unitario | 100% |
| `Decorators (get_summary)` | Unitario | 100% |
| `Observers` | Unitario | 90% |
| `BookingService.create_appointment()` | Integración | 90% |
| Endpoints API | Integración | 85% |
| **Global** | **Todos** | **≥ 80%** |

### 2.2 Logging Estructurado

Reemplazar todos los `print()` por logging profesional:

```python
import logging
import json

logger = logging.getLogger("medibook")

# En vez de:
#   print(f">>> Cita PRESENCIAL creada con id={appointment.id}")

# Usar:
logger.info(
    "Cita creada exitosamente",
    extra={
        "appointment_id": appointment.id,
        "type": "in_person",
        "doctor_id": appointment.doctor_id,
    }
)
```

- [ ] Configurar `logging` con formato JSON para producción.
- [ ] Usar niveles adecuados: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- [ ] Integrar con middleware de FastAPI para loggear requests/responses.

### 2.3 Migraciones con Alembic

```bash
# Inicializar
alembic init alembic

# Generar migración automática
alembic revision --autogenerate -m "tablas iniciales"

# Aplicar
alembic upgrade head
```

- [ ] Configurar `alembic.ini` con la `DATABASE_URL` desde variables de entorno.
- [ ] **Eliminar `Base.metadata.create_all()`** de `init_db.py` (reemplazado por Alembic).
- [ ] Cada cambio en modelos = nueva migración versionada.

---

## Fase 3 — Seguridad

> **Objetivo:** Proteger el sistema contra accesos no autorizados y ataques comunes.

### 3.1 Autenticación con JWT

```python
# Esquema de autenticación
# POST /api/v1/auth/login → devuelve access_token + refresh_token
# Headers: Authorization: Bearer <token>
```

| Decisión | Elección | Justificación |
|---|---|---|
| Librería | `python-jose[cryptography]` + `passlib[bcrypt]` | Estándar de la industria, compatible con FastAPI |
| Tipo de token | JWT (RS256 o HS256) | Stateless, escalable |
| Expiración access | 30 minutos | Balance seguridad/UX |
| Expiración refresh | 7 días | Sesiones persistentes |

### 3.2 Autorización Basada en Roles (RBAC)

| Rol | Permisos |
|---|---|
| `ADMIN` | CRUD completo, gestión de usuarios, reportes |
| `DOCTOR` | Ver/modificar sus propias citas, ver pacientes asignados |
| `RECEPTIONIST` | Crear/modificar citas, crear pacientes |
| `PATIENT` | Ver sus propias citas, solicitar citas |

### 3.3 Hardening

- [ ] **Rate Limiting:** `slowapi` o middleware personalizado (100 req/min por IP).
- [ ] **CORS:** Configurar orígenes permitidos explícitamente.
- [ ] **Validación de entrada:** Pydantic ya cubre esto (Fase 1), pero añadir sanitización extra.
- [ ] **Cabeceras de seguridad:** `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`.
- [ ] **Secrets:** `SECRET_KEY` y `DATABASE_URL` **NUNCA** en código fuente. Solo `.env` y/o secret managers.

---

## Fase 4 — Infraestructura y CI/CD

> **Objetivo:** Contenedorizar la aplicación y automatizar el pipeline de build, test y deploy.

### 4.1 Docker

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "medibook.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker/docker-compose.yml
services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: medibook_db
      POSTGRES_USER: medibook
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U medibook"]
      interval: 5s
      retries: 5

volumes:
  pgdata:
```

### 4.2 Pipeline CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: medibook_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest --cov=medibook --cov-report=xml
      - run: ruff check medibook/  # Linter

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -f docker/Dockerfile -t medibook:${{ github.sha }} .
```

### 4.3 Entornos

| Entorno | Base de Datos | Propósito |
|---|---|---|
| `development` | SQLite local o PostgreSQL Docker | Desarrollo rápido |
| `staging` | PostgreSQL (cloud) | Validación pre-producción |
| `production` | PostgreSQL (cloud, managed) | Producción real |

---

## Fase 5 — Producción y Observabilidad

> **Objetivo:** Desplegar con confianza, monitorear la salud del sistema y responder rápidamente a incidentes.

### 5.1 Monitoreo y Observabilidad

| Pilar | Herramienta Recomendada | Propósito |
|---|---|---|
| **Logs** | ELK Stack o Loki + Grafana | Logs centralizados y buscables |
| **Métricas** | Prometheus + Grafana | CPU, memoria, latencia, requests/s |
| **Trazabilidad** | OpenTelemetry | Traces distribuidos entre servicios |
| **Alertas** | Grafana Alerts o PagerDuty | Notificaciones ante anomalías |
| **Health Check** | `/api/v1/health` | Verificar disponibilidad de API + BD |

### 5.2 Endpoint de Health Check

```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"}
        )
```

### 5.3 Opciones de Despliegue

| Plataforma | Costo | Complejidad | Ideal Para |
|---|---|---|---|
| **Railway** | Bajo | ⭐ Baja | MVP rápido, staging |
| **Render** | Bajo | ⭐ Baja | Apps pequeñas-medianas |
| **AWS ECS + RDS** | Medio-Alto | ⭐⭐⭐ Alta | Producción enterprise |
| **Google Cloud Run** | Medio | ⭐⭐ Media | Serverless, auto-scaling |
| **DigitalOcean App Platform** | Bajo-Medio | ⭐⭐ Media | Balance costo/control |

### 5.4 Checklist Pre-Producción

- [ ] `DEBUG=false` en producción.
- [ ] `DATABASE_URL` apunta a BD de producción (managed PostgreSQL).
- [ ] `SECRET_KEY` es un valor aleatorio seguro (≥ 64 caracteres).
- [ ] HTTPS forzado (TLS/SSL).
- [ ] CORS configurado solo para dominios autorizados.
- [ ] Rate limiting activo.
- [ ] Backups automáticos de BD configurados.
- [ ] Logging en formato JSON hacia sistema centralizado.
- [ ] Health check responde correctamente.
- [ ] Migraciones aplicadas (`alembic upgrade head`).
- [ ] Tests pasando al 100% en CI.
- [ ] Cobertura ≥ 80%.
- [ ] Sin secrets hardcodeados (auditoría con `gitleaks` o `trufflehog`).
- [ ] Documentación API disponible en `/docs` (Swagger automático de FastAPI).

---

## 📋 Resumen Ejecutivo

| Fase | Duración Estimada | Prioridad | Entregable |
|---|---|---|---|
| **Fase 0** — Fundamentos | 3 días | 🔴 Crítica | Repo limpio, dependencias, `.env.example` |
| **Fase 1** — API REST | 7 días | 🔴 Crítica | FastAPI funcionando, endpoints documentados |
| **Fase 2** — Calidad | 7 días | 🟠 Alta | Tests ≥80%, Alembic, logging profesional |
| **Fase 3** — Seguridad | 7 días | 🟠 Alta | JWT, RBAC, rate limiting |
| **Fase 4** — Infraestructura | 6 días | 🟡 Media | Docker, CI/CD, staging desplegado |
| **Fase 5** — Producción | 5 días | 🟡 Media | Sistema en producción, monitoreado |
| **Total** | **~5 semanas** | | Sistema production-ready |

> [!IMPORTANT]
> Las fases son **secuenciales y acumulativas**. No se debe avanzar a la siguiente fase sin haber completado la anterior. Cada fase produce un entregable verificable y un incremento funcional del sistema.

> [!WARNING]
> El sistema actual **NO debe desplegarse en producción** en su estado actual. No cuenta con autenticación, validación de datos robusta, ni manejo adecuado de sesiones de BD. Seguir este roadmap asegura que cada brecha se cierre antes del despliegue final.

---

*Documento generado el 22 de abril de 2026.*
*Autor: Ingeniería de Software — Arquitectura MediBook.*
