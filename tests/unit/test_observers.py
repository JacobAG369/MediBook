# tests/unit/test_observers.py
"""
Tests unitarios para el patrón Observer.
Verifica registro, desregistro y notificación de observers.
"""

from datetime import datetime
from unittest.mock import MagicMock

from medibook.domain.appointment import Appointment
from medibook.services.observers import (
    AppointmentObserver,
    BookingNotifier,
    ConsoleLogObserver,
    DoctorNotificationObserver,
)


class TestBookingNotifier:
    """Pruebas para el Subject (BookingNotifier)."""

    def _make_appointment(self) -> Appointment:
        appt = Appointment(
            patient_id=1,
            doctor_id=2,
            start_time=datetime(2026, 5, 1, 10, 0),
            duration_minutes=30,
            status="SCHEDULED",
        )
        appt.id = 1
        return appt

    def test_register_observer(self):
        """Debe poder registrar un observer."""
        notifier = BookingNotifier()
        observer = ConsoleLogObserver()

        notifier.register(observer)

        assert observer in notifier._observers

    def test_register_duplicate_observer(self):
        """Registrar el mismo observer dos veces no debe duplicarlo."""
        notifier = BookingNotifier()
        observer = ConsoleLogObserver()

        notifier.register(observer)
        notifier.register(observer)

        assert notifier._observers.count(observer) == 1

    def test_unregister_observer(self):
        """Debe poder desregistrar un observer."""
        notifier = BookingNotifier()
        observer = ConsoleLogObserver()

        notifier.register(observer)
        notifier.unregister(observer)

        assert observer not in notifier._observers

    def test_unregister_nonexistent_observer(self):
        """Desregistrar un observer que no existe no debe fallar."""
        notifier = BookingNotifier()
        observer = ConsoleLogObserver()

        # No debe lanzar excepción
        notifier.unregister(observer)

    def test_notify_calls_all_observers(self):
        """notify_appointment_created debe llamar a todos los observers."""
        notifier = BookingNotifier()
        mock_obs_1 = MagicMock(spec=AppointmentObserver)
        mock_obs_2 = MagicMock(spec=AppointmentObserver)

        notifier.register(mock_obs_1)
        notifier.register(mock_obs_2)

        appt = self._make_appointment()
        notifier.notify_appointment_created(appt)

        mock_obs_1.on_appointment_created.assert_called_once_with(appt)
        mock_obs_2.on_appointment_created.assert_called_once_with(appt)

    def test_notify_with_no_observers(self):
        """Notificar sin observers registrados no debe fallar."""
        notifier = BookingNotifier()
        appt = self._make_appointment()

        # No debe lanzar excepción
        notifier.notify_appointment_created(appt)


class TestConcreteObservers:
    """Pruebas para los observers concretos."""

    def _make_appointment(self) -> Appointment:
        appt = Appointment(
            patient_id=1,
            doctor_id=2,
            start_time=datetime(2026, 5, 1, 10, 0),
            duration_minutes=30,
            status="SCHEDULED",
        )
        appt.id = 5
        return appt

    def test_console_log_observer_runs(self):
        """ConsoleLogObserver debe loggear cuando se crea una cita."""
        from unittest.mock import patch

        observer = ConsoleLogObserver()
        appt = self._make_appointment()

        with patch("medibook.services.observers.logger") as mock_logger:
            observer.on_appointment_created(appt)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "Nueva cita creada" in call_args[0][0]

    def test_doctor_notification_observer_runs(self):
        """DoctorNotificationObserver debe loggear notificación."""
        from unittest.mock import patch

        observer = DoctorNotificationObserver()
        appt = self._make_appointment()

        with patch("medibook.services.observers.logger") as mock_logger:
            observer.on_appointment_created(appt)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "Notificar al doctor" in call_args[0][0]
