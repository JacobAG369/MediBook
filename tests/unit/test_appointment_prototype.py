# tests/unit/test_appointment_prototype.py
"""
Tests unitarios para el patrón Prototype.
Verifica la clonación correcta de citas.
"""

from datetime import datetime

from medibook.domain.appointment import Appointment
from medibook.services.appointment_prototype import AppointmentPrototype


class TestAppointmentPrototype:
    """Pruebas para AppointmentPrototype.clone()."""

    def _make_base_appointment(self) -> Appointment:
        """Helper: crea una cita base para clonar."""
        return Appointment(
            patient_id=1,
            doctor_id=2,
            start_time=datetime(2026, 5, 1, 10, 0),
            duration_minutes=30,
            status="SCHEDULED",
            notes="Cita original",
            meeting_link=None,
        )

    def test_clone_copies_all_fields(self):
        """El clon debe copiar todos los campos de la cita base."""
        base = self._make_base_appointment()
        prototype = AppointmentPrototype(base)

        cloned = prototype.clone()

        assert cloned.patient_id == base.patient_id
        assert cloned.doctor_id == base.doctor_id
        assert cloned.start_time == base.start_time
        assert cloned.duration_minutes == base.duration_minutes
        assert cloned.status == base.status
        assert cloned.notes == base.notes
        assert cloned.meeting_link == base.meeting_link

    def test_clone_creates_new_instance(self):
        """El clon debe ser un objeto diferente al original."""
        base = self._make_base_appointment()
        prototype = AppointmentPrototype(base)

        cloned = prototype.clone()

        assert cloned is not base

    def test_clone_with_overrides(self):
        """El clon debe aplicar los overrides correctamente."""
        base = self._make_base_appointment()
        prototype = AppointmentPrototype(base)
        new_time = datetime(2026, 5, 2, 14, 0)

        cloned = prototype.clone(overrides={
            "start_time": new_time,
            "notes": "Cita de seguimiento",
            "status": "FOLLOW_UP",
        })

        # Campos sobrescritos
        assert cloned.start_time == new_time
        assert cloned.notes == "Cita de seguimiento"
        assert cloned.status == "FOLLOW_UP"

        # Campos heredados del original
        assert cloned.patient_id == base.patient_id
        assert cloned.doctor_id == base.doctor_id
        assert cloned.duration_minutes == base.duration_minutes

    def test_clone_does_not_copy_id(self):
        """El clon NO debe copiar el id (SQLAlchemy lo asigna)."""
        base = self._make_base_appointment()
        base.id = 99
        prototype = AppointmentPrototype(base)

        cloned = prototype.clone()

        assert cloned.id is None

    def test_clone_with_empty_overrides(self):
        """Overrides vacíos deben producir una copia idéntica."""
        base = self._make_base_appointment()
        prototype = AppointmentPrototype(base)

        cloned = prototype.clone(overrides={})

        assert cloned.patient_id == base.patient_id
        assert cloned.doctor_id == base.doctor_id

    def test_clone_with_none_overrides(self):
        """None como overrides debe producir una copia idéntica."""
        base = self._make_base_appointment()
        prototype = AppointmentPrototype(base)

        cloned = prototype.clone(overrides=None)

        assert cloned.patient_id == base.patient_id
