# medibook/services/appointment_workflow.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import uuid4

from medibook.config.logging_config import get_logger

logger = get_logger("services.workflow")

from medibook.infra.db import SessionLocal
from medibook.domain.appointment import Appointment

class BaseAppointmentWorkflow(ABC):
    """
    Template Method para el flujo de creación de una cita médica.

    El método 'create' define el ALGORITMO GENERAL:
      1) validar datos
      2) verificar disponibilidad
      3) construir la cita
      4) guardar en BD
      5) ejecutar acciones posteriores
    """
#METODO CREATE
    def create(self, data: Dict[str, Any]) -> Appointment:
       
        # 1) validar datos de entrada
        self.validate_input(data)

        # 2) verificar disponibilidad del doctor, horarios, etc.
        self.check_availability(data)

        # 3) construir el objeto Appointment (cada subclase decide cómo)
        appointment = self.build_appointment(data)

        # 4) guardar en la base de datos
        self.save_appointment(appointment)

        # 5) acciones posteriores: notificaciones, logs, etc.
        self.after_save(appointment)

        return appointment



    def validate_input(self, data: Dict[str, Any]) -> None:
        """
        Validación genérica de datos mínimos.
        Las subclases pueden sobreescribir este método si necesitan reglas extra.
        """
        required_fields = ["patient_id", "doctor_id", "start_time"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Faltan campos requeridos: {missing}")

    def check_availability(self, data: Dict[str, Any]) -> None:
       
        # TODO: 
        pass

    @abstractmethod
    def build_appointment(self, data: Dict[str, Any]) -> Appointment:
        """
        Paso ABSTRACTO: cada subclase debe construir la cita a su manera.
        """
        raise NotImplementedError

    def save_appointment(self, appointment: Appointment) -> None:
        """
        Guardar la cita en la base de datos usando SessionLocal.
        Este paso es común para todos los flujos.
        """
        session = SessionLocal()
        try:
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def after_save(self, appointment: Appointment) -> None:
        """
        Hook opcional: subclases pueden sobreescribirlo para
        enviar notificaciones, actualizar un dashboard, etc.
        """
        # Por defecto no hace nada.
        pass


class InPersonAppointmentWorkflow(BaseAppointmentWorkflow):
    """
    Flujo concreto para crear una cita PRESENCIAL estándar.
    Utiliza el Template Method de la clase base, pero define
    cómo se construye el Appointment.
    """

    def build_appointment(self, data: Dict[str, Any]) -> Appointment:
        duration = data.get("duration_minutes", 30)
        status = data.get("status", "SCHEDULED")
        notes = data.get("notes")

        appointment = Appointment(
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            start_time=data["start_time"],
            duration_minutes=duration,
            status=status,
            notes=notes,
            meeting_link=None,  # cita presencial, sin link
        )
        return appointment

    def after_save(self, appointment: Appointment) -> None:
        logger.info("Cita PRESENCIAL creada con id=%s", appointment.id)


class OnlineAppointmentWorkflow(BaseAppointmentWorkflow):
    """
    Flujo concreto para crear una cita EN LÍNEA (teleconsulta).
    Aquí reutilizamos el mismo Template Method, pero:
      - la cita incluye un meeting_link
      - podemos aplicar reglas específicas en after_save
    """

    def build_appointment(self, data: Dict[str, Any]) -> Appointment:
        duration = data.get("duration_minutes", 30)
        status = data.get("status", "SCHEDULED")
        notes = data.get("notes")

     #POR LOS TIEMPOS TAN APRESURADOS JEJE UN LINK GENERICO
        meeting_link = data.get("meeting_link")
        if not meeting_link:
            meeting_link = f"https://meet.medibook.com/session/{uuid4().hex}"

        appointment = Appointment(
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            start_time=data["start_time"],
            duration_minutes=duration,
            status=status,
            notes=notes,
            meeting_link=meeting_link,
        )
        return appointment

    def after_save(self, appointment: Appointment) -> None:
        """
        Aquí podríamos:
          - enviar correo con el link
          - programar recordatorios
          - notificar a un Observer
        Por ahora solo mostramos el link en consola.
        """
        logger.info(
            "Cita ONLINE creada con id=%s, link=%s",
            appointment.id,
            appointment.meeting_link,
        )