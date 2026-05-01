# tests/unit/test_appointment_factory.py
"""
Tests unitarios para el patrón Factory Method.
Verifica que AppointmentFactory selecciona el workflow correcto.
"""

import pytest

from medibook.services.appointment_factory import AppointmentFactory
from medibook.services.appointment_workflow import (
    InPersonAppointmentWorkflow,
    OnlineAppointmentWorkflow,
)


class TestAppointmentFactory:
    """Pruebas para AppointmentFactory.create_workflow()."""

    def test_create_in_person_workflow(self):
        """Debe retornar InPersonAppointmentWorkflow para 'in_person'."""
        workflow = AppointmentFactory.create_workflow("in_person")
        assert isinstance(workflow, InPersonAppointmentWorkflow)

    def test_create_online_workflow(self):
        """Debe retornar OnlineAppointmentWorkflow para 'online'."""
        workflow = AppointmentFactory.create_workflow("online")
        assert isinstance(workflow, OnlineAppointmentWorkflow)

    def test_create_teleconsulta_workflow(self):
        """Debe retornar OnlineAppointmentWorkflow para 'teleconsulta'."""
        workflow = AppointmentFactory.create_workflow("teleconsulta")
        assert isinstance(workflow, OnlineAppointmentWorkflow)

    def test_create_telemedicine_workflow(self):
        """Debe retornar OnlineAppointmentWorkflow para 'telemedicine'."""
        workflow = AppointmentFactory.create_workflow("telemedicine")
        assert isinstance(workflow, OnlineAppointmentWorkflow)

    def test_case_insensitive(self):
        """La Factory debe ser case-insensitive."""
        workflow = AppointmentFactory.create_workflow("IN_PERSON")
        assert isinstance(workflow, InPersonAppointmentWorkflow)

    def test_invalid_type_raises_error(self):
        """Debe lanzar ValueError para tipos no soportados."""
        with pytest.raises(ValueError, match="no soportado"):
            AppointmentFactory.create_workflow("invalid_type")

    def test_empty_type_raises_error(self):
        """Debe lanzar ValueError para string vacío."""
        with pytest.raises(ValueError):
            AppointmentFactory.create_workflow("")
