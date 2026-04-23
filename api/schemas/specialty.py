# medibook/api/schemas/specialty.py
"""
Schemas Pydantic para la entidad Specialty.
"""

from typing import Optional

from pydantic import BaseModel, Field


# ---------- Request Schemas ----------

class SpecialtyCreate(BaseModel):
    """Datos requeridos para crear una especialidad."""
    name: str = Field(..., min_length=2, max_length=100, examples=["Cardiología"])
    description: Optional[str] = Field(
        default=None, max_length=255, examples=["Especialidad del corazón"]
    )


# ---------- Response Schemas ----------

class SpecialtyResponse(BaseModel):
    """Representación de una especialidad en las respuestas de la API."""
    id: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
