# medibook/services/appointment_factory.py

from medibook.services.appointment_workflow import (InPersonAppointmentWorkflow, OnlineAppointmentWorkflow, BaseAppointmentWorkflow,)


class AppointmentFactory:

    @staticmethod
    def create_workflow(appointment_type: str) -> BaseAppointmentWorkflow:
        appointment_type = appointment_type.lower()

        if appointment_type == "in_person":
            return InPersonAppointmentWorkflow()

        if appointment_type in ("online", "teleconsulta", "telemedicine"):
            return OnlineAppointmentWorkflow()

        raise ValueError(f"Tipo de cita no soportado por la Factory: {appointment_type}")
