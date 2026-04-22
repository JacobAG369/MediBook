# medibook/services/observers.py

from abc import ABC, abstractmethod
from typing import List

from medibook.domain.appointment import Appointment

class AppointmentObserver(ABC):
    """
    Observer: define la interfaz para objetos que reaccionan
    cuando ocurre un evento sobre citas (creadas, canceladas, etc.).
    """

    @abstractmethod
    def on_appointment_created(self, appointment: Appointment) -> None:
        pass

    # En el futuro podrías agregar:
    # def on_appointment_cancelled(self, appointment: Appointment) -> None: ...
    # def on_appointment_rescheduled(self, appointment: Appointment) -> None: ...
    

class BookingNotifier:
    """
    Subject (Observable) del patrón Observer.
    Mantiene una lista de observadores y los notifica cuando
    se crea una nueva cita.
    """

    def __init__(self) -> None:
        self._observers: List[AppointmentObserver] = []

    def register(self, observer: AppointmentObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: AppointmentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_appointment_created(self, appointment: Appointment) -> None:
        for observer in self._observers:
            observer.on_appointment_created(appointment)


# -------- Observadores concretos (implementaciones de AppointmentObserver) --------


class ConsoleLogObserver(AppointmentObserver):
    """
    Observer simple que avisa cuando se crea una cita.
    
    """

    def on_appointment_created(self, appointment: Appointment) -> None:
        print(
            f"[ConsoleLogObserver] Nueva cita creada: "
            f"id={appointment.id}, doctor_id={appointment.doctor_id}, "
            f"patient_id={appointment.patient_id}, start={appointment.start_time}"
        )


class DoctorNotificationObserver(AppointmentObserver):
   

    def on_appointment_created(self, appointment: Appointment) -> None:
        print(
            f"[DoctorNotificationObserver] Notificar al doctor {appointment.doctor_id} "
            f"de nueva cita (id={appointment.id})."
        )
