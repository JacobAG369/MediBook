# medibook/api/dependencies.py
"""
Inyección de dependencias para FastAPI.

Provee la sesión de base de datos como dependencia inyectable
en los endpoints, garantizando que cada request tenga su propia
sesión y que esta se cierre correctamente al finalizar.
"""

from typing import Generator

from sqlalchemy.orm import Session

from medibook.infra.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Generador que provee una sesión de BD por request.
    FastAPI se encarga de llamar a .close() automáticamente
    al finalizar el request (gracias al yield).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
