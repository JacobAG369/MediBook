# medibook/api/schemas/doctor.py
"""
Schemas Pydantic para la entidad Doctor.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from medibook.api.schemas.specialty import SpecialtyResponse


# ---------- Request Schemas ----------

class DoctorCreate(BaseModel):
    """Datos requeridos para registrar un doctor con su especialidad."""
    name: str = Field(
        ..., min_length=2, max_length=120, examples=["Dr. Carlos Mendoza"]
    )
    email: Optional[EmailStr] = Field(default=None, examples=["carlos@medibook.com"])
    phone: Optional[str] = Field(
        default=None, max_length=20, examples=["+52 55 9876 5432"]
    )
    specialty_name: str = Field(
        ..., min_length=2, max_length=100, examples=["Cardiología"],
        description="Nombre de la especialidad. Se reutiliza si ya existe (Flyweight)."
    )
    specialty_description: Optional[str] = Field(
        default=None, max_length=255, examples=["Especialidad del corazón"]
    )


class DoctorUpdate(BaseModel):
    """Campos opcionales para actualizar un doctor."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    active: Optional[bool] = None


# ---------- Response Schemas ----------

class DoctorResponse(BaseModel):
    """Representación de un doctor en las respuestas de la API."""
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty_id: int
    active: bool
    specialty: Optional[SpecialtyResponse] = None

    model_config = {"from_attributes": True}
