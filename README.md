# 🏥 MediBook

Sistema de gestión de citas médicas desarrollado en Python, con énfasis en la implementación de **Patrones de Diseño (GoF)** y una arquitectura limpia por capas.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.12+ | Lenguaje principal |
| SQLAlchemy 2.x | ORM para persistencia relacional |
| FastAPI | Framework web y API REST |
| Alembic | Migraciones de base de datos |
| PostgreSQL | Base de datos en producción |
| Pytest | Testing |

## Patrones de Diseño Implementados

- **Singleton** — Configuración global (`BookingConfig`)
- **Factory Method** — Selección de flujo de citas (`AppointmentFactory`)
- **Template Method** — Algoritmo de creación de citas (`BaseAppointmentWorkflow`)
- **Prototype** — Clonación de citas existentes (`AppointmentPrototype`)
- **Decorator** — Enriquecimiento dinámico de resúmenes de citas
- **Flyweight** — Caché compartido de especialidades médicas
- **Observer** — Notificaciones desacopladas ante eventos de citas

## Estructura del Proyecto

```
medibook/
├── config/          # Configuración global (Singleton)
├── domain/          # Modelos de dominio (ORM / Entidades)
├── infra/           # Infraestructura (conexión a BD, sesiones)
├── services/        # Lógica de negocio y patrones de diseño
├── scripts/         # Utilidades (inicialización de BD, seeds)
└── web/             # Capa web (API REST / Frontend)
```

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd medibook-pattern

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores reales

# 5. Inicializar la base de datos
python -m medibook.scripts.init_db
```

## Ejecución

```bash
# Servidor de desarrollo
uvicorn medibook.main:app --reload --port 8000

# Documentación automática de la API
# http://localhost:8000/docs
```

## Testing

```bash
pytest --cov=medibook
```

## Licencia

Uso académico.
