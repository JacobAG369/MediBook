# medibook/api/routes/appointments.py
"""
Endpoints para la gestión de citas médicas.

Integra los siguientes patrones de diseño:
  - Factory Method → selección del workflow según tipo de cita
  - Template Method → flujo de creación paso a paso
  - Observer → notificaciones al crear/clonar citas
  - Prototype → clonación de citas existentes
  - Decorator → resúmenes enriquecidos dinámicamente
"""

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db
from medibook.api.schemas.appointment import (
    AppointmentClone,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentSummaryResponse,
    AppointmentUpdate,
)
from medibook.domain.appointment import Appointment
from medibook.services.appointment_factory import AppointmentFactory
from medibook.services.appointment_prototype import AppointmentPrototype
from medibook.services.appointment_decorators import (
    SimpleAppointmentComponent,
    OnlineAppointmentDecorator,
    FollowUpAppointmentDecorator,
    UrgentAppointmentDecorator,
)
from medibook.services.observers import BookingNotifier, ConsoleLogObserver, DoctorNotificationObserver
from medibook.domain.user import User
from medibook.api.auth.dependencies import get_current_user, require_receptionist, require_doctor

router = APIRouter(prefix="/appointments", tags=["Citas Médicas"])

# Observer: notificador con observers registrados
_notifier = BookingNotifier()
_notifier.register(ConsoleLogObserver())
_notifier.register(DoctorNotificationObserver())


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cita médica",
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """
    Crea una nueva cita médica.

    - **in_person**: Cita presencial estándar.
    - **online / teleconsulta / telemedicine**: Cita con videollamada
      (se genera un meeting_link automáticamente si no se provee).

    Patrones utilizados:
    - **Factory Method**: selecciona el workflow correcto.
    - **Observer**: notifica a los observers registrados.
    """
    try:
        data = payload.model_dump()
        appointment_type = data.pop("appointment_type")

        # Factory Method: validar que el tipo es soportado
        AppointmentFactory.create_workflow(appointment_type)

        # Convertir start_time si es string
        if isinstance(data.get("start_time"), str):
            data["start_time"] = datetime.fromisoformat(data["start_time"])

        # Construir la cita según el tipo
        meeting_link = data.get("meeting_link")
        if appointment_type in ("online", "teleconsulta", "telemedicine") and not meeting_link:
            meeting_link = f"https://meet.medibook.com/session/{uuid4().hex}"

        appointment = Appointment(
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            start_time=data["start_time"],
            duration_minutes=data.get("duration_minutes", 30),
            status="SCHEDULED",
            notes=data.get("notes"),
            meeting_link=meeting_link if appointment_type != "in_person" else None,
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        # Observer: notificar
        _notifier.notify_appointment_created(appointment)

        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=List[AppointmentResponse],
    summary="Listar citas",
)
def list_appointments(
    skip: int = 0,
    limit: int = 50,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    appointment_status: str | None = None,
    db: Session = Depends(get_db),
):
    """Devuelve una lista paginada de citas con filtros opcionales."""
    query = db.query(Appointment)

    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if appointment_status:
        query = query.filter(Appointment.status == appointment_status.upper())

    appointments = (
        query.order_by(Appointment.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return appointments


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Obtener cita por ID",
)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Devuelve los datos de una cita específica."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id={appointment_id} no encontrada",
        )
    return appointment


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Actualizar cita",
)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """Actualiza parcialmente los datos de una cita."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id={appointment_id} no encontrada",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar cita",
)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """
    Cancela una cita cambiando su estado a CANCELLED.
    No se elimina físicamente para preservar el historial.
    """
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id={appointment_id} no encontrada",
        )

    appointment.status = "CANCELLED"
    db.commit()


# ---------- Endpoints de Patrones de Diseño ----------


@router.post(
    "/{appointment_id}/clone",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clonar cita (Prototype)",
)
def clone_appointment(
    appointment_id: int,
    payload: AppointmentClone,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_doctor),
):
    """
    Clona una cita existente usando el patrón **Prototype**.

    Copia todos los campos de la cita original y permite
    sobrescribir valores específicos mediante el campo `overrides`.
    """
    base_appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not base_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita base con id={appointment_id} no encontrada",
        )

    prototype = AppointmentPrototype(base_appointment)
    cloned = prototype.clone(payload.overrides)

    db.add(cloned)
    db.commit()
    db.refresh(cloned)

    _notifier.notify_appointment_created(cloned)

    return cloned


@router.get(
    "/{appointment_id}/summary",
    response_model=AppointmentSummaryResponse,
    summary="Resumen decorado (Decorator)",
)
def get_appointment_summary(appointment_id: int, db: Session = Depends(get_db)):
    """
    Genera un resumen enriquecido de la cita usando el patrón **Decorator**.

    Aplica etiquetas dinámicas según el estado de la cita:
    - `[ONLINE]` si tiene meeting_link.
    - `[SEGUIMIENTO]` si el estado es FOLLOW_UP.
    - `[URGENTE]` si el estado es URGENT.
    """
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id={appointment_id} no encontrada",
        )

    # Decorator pattern
    component = SimpleAppointmentComponent(appointment)
    decorated = component

    if appointment.meeting_link:
        decorated = OnlineAppointmentDecorator(decorated)
    if appointment.status.upper() == "FOLLOW_UP":
        decorated = FollowUpAppointmentDecorator(decorated)
    if appointment.status.upper() == "URGENT":
        decorated = UrgentAppointmentDecorator(decorated)

    return AppointmentSummaryResponse(
        appointment_id=appointment_id,
        summary=decorated.get_summary(),
    )
