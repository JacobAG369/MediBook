# medibook/api/routes/health.py
"""
Endpoint de salud del sistema.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Verificar salud del sistema")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica que la API y la conexión a la base de datos
    estén funcionando correctamente.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "detail": str(e),
        }
