# medibook/api/schemas/patient.py
"""
Schemas Pydantic para la entidad Patient.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Request Schemas ----------

class PatientCreate(BaseModel):
    """Datos requeridos para registrar un paciente."""
    full_name: str = Field(
        ..., min_length=2, max_length=150, examples=["María García López"]
    )
    email: Optional[EmailStr] = Field(default=None, examples=["maria@email.com"])
    phone: Optional[str] = Field(
        default=None, max_length=20, examples=["+52 55 1234 5678"]
    )
    date_of_birth: Optional[date] = Field(default=None, examples=["1990-05-15"])
    notes: Optional[str] = Field(default=None, max_length=255)


class PatientUpdate(BaseModel):
    """Campos opcionales para actualizar un paciente."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=255)


# ---------- Response Schemas ----------

class PatientResponse(BaseModel):
    """Representación de un paciente en las respuestas de la API."""
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
