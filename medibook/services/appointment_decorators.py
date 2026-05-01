# medibook/services/appointment_decorators.py

from abc import ABC, abstractmethod
from medibook.domain.appointment import Appointment


class AppointmentComponent(ABC):
    """
    Componente base del patrón Decorator.
    Define la interfaz para representar una cita como un resumen de texto.
    """

    @abstractmethod
    def get_summary(self) -> str:
        pass


class SimpleAppointmentComponent(AppointmentComponent):
    """
    Implementación base: usa directamente el objeto Appointment
    y genera un resumen sencillo.
    """

    def __init__(self, appointment: Appointment) -> None:
        self._appointment = appointment

    def get_summary(self) -> str:
        return (
            f"Cita #{self._appointment.id} | "
            f"Doctor: {self._appointment.doctor_id} | "
            f"Paciente: {self._appointment.patient_id} | "
            f"Fecha: {self._appointment.start_time} | "
            f"Estado: {self._appointment.status}"
        )


class AppointmentDecorator(AppointmentComponent):
    """
    Clase base para los decoradores.
    Envuelve a otro AppointmentComponent y delega la llamada.
    """

    def __init__(self, component: AppointmentComponent) -> None:
        self._component = component

    @abstractmethod
    def get_summary(self) -> str:
        return self._component.get_summary()


class OnlineAppointmentDecorator(AppointmentDecorator):
    """
    Decorador que agrega información para citas ONLINE.
    """

    def get_summary(self) -> str:
        base = self._component.get_summary()
        # Nota: asumimos que el component interno tiene acceso al appointment
        # a través de SimpleAppointmentComponent o de otro decorator.
        # Para simplicidad, obtenemos el appointment desde el más interno
        
        return f"[ONLINE] {base}"


class FollowUpAppointmentDecorator(AppointmentDecorator):
   

    def get_summary(self) -> str:
        base = self._component.get_summary()
        return f"[SEGUIMIENTO] {base}"


class UrgentAppointmentDecorator(AppointmentDecorator):
    """
    Decorador para citas URGENTES.
    """

    def get_summary(self) -> str:
        base = self._component.get_summary()
        return f"[URGENTE] {base}"
