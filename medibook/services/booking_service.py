# medibook/services/booking_service.py

from datetime import datetime
from typing import Any, Dict

from medibook.services.appointment_factory import AppointmentFactory
from medibook.services.appointment_workflow import BaseAppointmentWorkflow
from medibook.services.observers import (BookingNotifier, ConsoleLogObserver, DoctorNotificationObserver,)
from medibook.infra.db import SessionLocal
from medibook.domain.appointment import Appointment
from medibook.services.appointment_prototype import AppointmentPrototype
from medibook.services.appointment_decorators import (SimpleAppointmentComponent, OnlineAppointmentDecorator, FollowUpAppointmentDecorator, UrgentAppointmentDecorator,)

from medibook.domain.doctor import Doctor
from medibook.services.specialty_flyweight import SpecialtyFlyweightFactory



class BookingService:
    """
    Servicio de alto nivel que orquesta la creación de citas.

    Patrones que usa:
      - Factory Method (AppointmentFactory) para seleccionar el workflow.
      - Template Method (BaseAppointmentWorkflow.create) para el flujo de creación.
      - Observer (BookingNotifier + Observers) para reaccionar a eventos de cita creada.
    """

    def __init__(self) -> None:
        # Subject del patrón Observer
        self._notifier = BookingNotifier()

        # Registramos algunos observers por defecto
        self._notifier.register(ConsoleLogObserver())
        self._notifier.register(DoctorNotificationObserver())

    def create_appointment(self, appointment_type: str, data: Dict[str, Any]):
        """
        Punto de entrada. Selecciona el workflow adecuado
        usando el Factory Method + Template Method,
        y luego dispara notificaciones usando Observer.
        """

        # Usamos la Factory para obtener el workflow correcto
        workflow: BaseAppointmentWorkflow = AppointmentFactory.create_workflow(appointment_type)

        # Convertimos start_time de string -> datetime si es necesario
        if isinstance(data.get("start_time"), str):
            data["start_time"] = datetime.fromisoformat(data["start_time"])

        # Ejecutamos el Template Method (creación de la cita)
        appointment = workflow.create(data)

        # Notificar a los observers que se ha creado una nueva cita
        self._notifier.notify_appointment_created(appointment)

        return appointment
    

    def clone_appointment(
        self,
        appointment_id: int,
        overrides: Dict[str, Any] | None = None,
    ) -> Appointment:
       

        session = SessionLocal()

        try:
            base_appointment = (
                session.query(Appointment)
                .filter(Appointment.id == appointment_id)
                .first()
            )

            if not base_appointment:
                raise ValueError(
                    f"No se encontró la cita base con id={appointment_id}"
                )

            prototype = AppointmentPrototype(base_appointment)

            # Creamos la nueva cita clonada (AÚN sin guardar)
            cloned = prototype.clone(overrides)

            # Guardamos la nueva cita
            session.add(cloned)
            session.commit()
            session.refresh(cloned)

            # Notificamos a los observers igual que con create_appointment
            self._notifier.notify_appointment_created(cloned)

            return cloned

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_decorated_summary(self, appointment_id: int) -> str:
        """
        Usa el patrón Decorator para construir un resumen enriquecido
        de una cita, aplicando decoradores según sus características.

        Ejemplo de salida:
        [ONLINE] [SEGUIMIENTO] Cita #10 | Doctor: 1 | Paciente: 1 | ...
        """

        session = SessionLocal()
        try:
            appointment = (
                session.query(Appointment)
                .filter(Appointment.id == appointment_id)
                .first()
            )

            if not appointment:
                raise ValueError(f"No se encontró la cita con id={appointment_id}")

            # Componente base
            component: SimpleAppointmentComponent = SimpleAppointmentComponent(
                appointment
            )

            # Aplicamos decoradores según la información de la cita
            decorated = component  # tipo AppointmentComponent

            # Si tiene meeting_link, asumimos que es online
            if appointment.meeting_link:
                decorated = OnlineAppointmentDecorator(decorated)

            # Si el estado indica seguimiento
            if appointment.status.upper() == "FOLLOW_UP":
                decorated = FollowUpAppointmentDecorator(decorated)

            # Si el estado indica urgencia
            if appointment.status.upper() == "URGENT":
                decorated = UrgentAppointmentDecorator(decorated)

            return decorated.get_summary()

        finally:
            session.close()


    def create_doctor_with_specialty(
        self,
        name: str,
        email: str | None,
        phone: str | None,
        specialty_name: str,
        specialty_description: str | None = None,
    ) -> Doctor:
        """
        Crea un doctor utilizando el patrón Flyweight para Specialty.

        - Obtiene la especialidad desde SpecialtyFlyweightFactory (caché).
        - Crea y guarda el doctor en la BD asociado a esa especialidad.
        """

        # Obtener la Specialty compartida (Flyweight)
        specialty = SpecialtyFlyweightFactory.get_specialty(
            name=specialty_name,
            description=specialty_description,
        )

        session = SessionLocal()
        try:
            doctor = Doctor(
                name=name,
                email=email,
                phone=phone,
                specialty_id=specialty.id,
            )
            session.add(doctor)
            session.commit()
            session.refresh(doctor)
            return doctor
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
