# medibook/api/schemas/appointment.py
"""
Schemas Pydantic para la entidad Appointment.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# ---------- Request Schemas ----------

class AppointmentCreate(BaseModel):
    """Datos requeridos para crear una cita médica."""
    patient_id: int = Field(..., gt=0, examples=[1])
    doctor_id: int = Field(..., gt=0, examples=[1])
    start_time: datetime = Field(..., examples=["2026-05-01T10:00:00"])
    duration_minutes: int = Field(default=30, ge=15, le=120, examples=[30])
    appointment_type: str = Field(
        default="in_person",
        pattern=r"^(in_person|online|teleconsulta|telemedicine)$",
        description="Tipo de cita. Determina el workflow (Factory Method).",
        examples=["in_person"],
    )
    notes: Optional[str] = Field(default=None, max_length=255)
    meeting_link: Optional[str] = Field(
        default=None, max_length=255,
        description="Link de videollamada (solo para citas online). Se genera automáticamente si no se provee.",
    )


class AppointmentUpdate(BaseModel):
    """Campos opcionales para actualizar una cita."""
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=15, le=120)
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(SCHEDULED|CONFIRMED|CANCELLED|COMPLETED|FOLLOW_UP|URGENT)$",
    )
    notes: Optional[str] = Field(default=None, max_length=255)


class AppointmentClone(BaseModel):
    """Campos opcionales para sobrescribir al clonar una cita (Prototype)."""
    overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Campos a sobrescribir en la cita clonada.",
        examples=[{"start_time": "2026-05-02T14:00:00", "notes": "Cita de seguimiento"}],
    )


# ---------- Response Schemas ----------

class AppointmentResponse(BaseModel):
    """Representación de una cita en las respuestas de la API."""
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int
    status: str
    notes: Optional[str] = None
    meeting_link: Optional[str] = None

    model_config = {"from_attributes": True}


class AppointmentSummaryResponse(BaseModel):
    """Resumen enriquecido con Decorators."""
    appointment_id: int
    summary: str
