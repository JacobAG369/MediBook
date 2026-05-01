# medibook/services/appointment_prototype.py

from typing import Any, Dict

from medibook.domain.appointment import Appointment


class AppointmentPrototype:
    """
    Implementación del patrón Prototype para Appointment.

    Toma una cita base y permite clonar sus datos,.
    """

    def __init__(self, base_appointment: Appointment) -> None:
        self._base = base_appointment

    def clone(self, overrides: Dict[str, Any] | None = None) -> Appointment:
        """
        Crea una nueva instancia de Appointment copiando los campos
        de la cita base, y aplicando los cambios'.
        """
        overrides = overrides or {}

        data: Dict[str, Any] = {
            "patient_id": overrides.get("patient_id", self._base.patient_id),
            "doctor_id": overrides.get("doctor_id", self._base.doctor_id),
            "start_time": overrides.get("start_time", self._base.start_time),
            "duration_minutes": overrides.get(
                "duration_minutes", self._base.duration_minutes
            ),
            "status": overrides.get("status", self._base.status),
            "notes": overrides.get("notes", self._base.notes),
            "meeting_link": overrides.get("meeting_link", self._base.meeting_link),
        }

        # Importante: no copiamos el id, SQLAlchemy le asignará uno nuevo
        new_appointment = Appointment(**data)
        return new_appointment
