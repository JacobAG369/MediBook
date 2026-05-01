# tests/unit/test_appointment_decorators.py
"""
Tests unitarios para el patrón Decorator.
Verifica que los decoradores enriquecen el resumen correctamente.
"""

from datetime import datetime

from medibook.domain.appointment import Appointment
from medibook.services.appointment_decorators import (
    SimpleAppointmentComponent,
    OnlineAppointmentDecorator,
    FollowUpAppointmentDecorator,
    UrgentAppointmentDecorator,
)


class TestAppointmentDecorators:
    """Pruebas para los decoradores de citas."""

    def _make_appointment(self, **kwargs) -> Appointment:
        """Helper: crea una cita con valores por defecto."""
        defaults = {
            "id": 10,
            "patient_id": 1,
            "doctor_id": 2,
            "start_time": datetime(2026, 5, 1, 10, 0),
            "duration_minutes": 30,
            "status": "SCHEDULED",
            "notes": None,
            "meeting_link": None,
        }
        defaults.update(kwargs)
        appt = Appointment(**{k: v for k, v in defaults.items() if k != "id"})
        appt.id = defaults["id"]
        return appt

    def test_simple_component_summary(self):
        """SimpleAppointmentComponent debe generar un resumen base."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)

        summary = component.get_summary()

        assert "Cita #10" in summary
        assert "Doctor: 2" in summary
        assert "Paciente: 1" in summary
        assert "Estado: SCHEDULED" in summary

    def test_online_decorator(self):
        """OnlineAppointmentDecorator debe agregar prefijo [ONLINE]."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)
        decorated = OnlineAppointmentDecorator(component)

        summary = decorated.get_summary()

        assert summary.startswith("[ONLINE]")
        assert "Cita #10" in summary

    def test_follow_up_decorator(self):
        """FollowUpAppointmentDecorator debe agregar prefijo [SEGUIMIENTO]."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)
        decorated = FollowUpAppointmentDecorator(component)

        summary = decorated.get_summary()

        assert summary.startswith("[SEGUIMIENTO]")
        assert "Cita #10" in summary

    def test_urgent_decorator(self):
        """UrgentAppointmentDecorator debe agregar prefijo [URGENTE]."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)
        decorated = UrgentAppointmentDecorator(component)

        summary = decorated.get_summary()

        assert summary.startswith("[URGENTE]")

    def test_multiple_decorators_stacked(self):
        """Múltiples decoradores deben apilarse correctamente."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)

        # Apilamos: Online + Seguimiento
        decorated = OnlineAppointmentDecorator(component)
        decorated = FollowUpAppointmentDecorator(decorated)

        summary = decorated.get_summary()

        assert "[SEGUIMIENTO]" in summary
        assert "[ONLINE]" in summary
        assert "Cita #10" in summary

    def test_decorator_preserves_base_content(self):
        """Los decoradores no deben modificar el contenido base."""
        appt = self._make_appointment()
        component = SimpleAppointmentComponent(appt)

        base_summary = component.get_summary()
        decorated = UrgentAppointmentDecorator(component)
        decorated_summary = decorated.get_summary()

        # El resumen decorado debe contener todo el base
        assert base_summary in decorated_summary.replace("[URGENTE] ", "")
