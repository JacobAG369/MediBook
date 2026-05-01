# tests/integration/test_api_appointments.py
"""
Tests de integración para los endpoints de Citas Médicas.
Incluye pruebas de RBAC y los patrones Factory, Prototype y Decorator vía API.
"""


class TestAppointmentEndpoints:
    """Pruebas de integración para /api/v1/appointments."""

    def _create_doctor_and_patient(self, client, admin_headers, receptionist_headers):
        """Helper: crea un doctor y un paciente para poder crear citas."""
        doc_resp = client.post("/api/v1/doctors/", json={
            "name": "Dr. Citas",
            "specialty_name": "General Citas",
        }, headers=admin_headers)
        pat_resp = client.post("/api/v1/patients/", json={
            "full_name": "Paciente Citas",
        }, headers=receptionist_headers)
        return doc_resp.json()["id"], pat_resp.json()["id"]

    def test_create_in_person_appointment(
        self, client, admin_headers, receptionist_headers
    ):
        """POST /appointments con tipo in_person (Factory → InPersonWorkflow)."""
        doctor_id, patient_id = self._create_doctor_and_patient(
            client, admin_headers, receptionist_headers
        )

        response = client.post("/api/v1/appointments/", json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_time": "2026-05-01T10:00:00",
            "appointment_type": "in_person",
        }, headers=receptionist_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SCHEDULED"
        assert data["meeting_link"] is None

    def test_create_online_appointment(
        self, client, admin_headers, receptionist_headers
    ):
        """POST /appointments con tipo online (Factory → OnlineWorkflow)."""
        doctor_id, patient_id = self._create_doctor_and_patient(
            client, admin_headers, receptionist_headers
        )

        response = client.post("/api/v1/appointments/", json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_time": "2026-05-01T14:00:00",
            "appointment_type": "online",
        }, headers=receptionist_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["meeting_link"] is not None
        assert "meet.medibook.com" in data["meeting_link"]

    def test_create_appointment_unauthorized(self, client):
        """POST /appointments sin token debe retornar 401."""
        response = client.post("/api/v1/appointments/", json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": "2026-05-01T10:00:00",
            "appointment_type": "in_person",
        })

        assert response.status_code == 401

    def test_create_appointment_invalid_type(self, client, receptionist_headers):
        """POST /appointments con tipo inválido debe retornar 422."""
        response = client.post("/api/v1/appointments/", json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": "2026-05-01T10:00:00",
            "appointment_type": "invalid",
        }, headers=receptionist_headers)

        assert response.status_code == 422

    def test_list_appointments(self, client):
        """GET /appointments es público."""
        response = client.get("/api/v1/appointments/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_appointment_not_found(self, client):
        """GET /appointments/{id} con ID inexistente debe retornar 404."""
        response = client.get("/api/v1/appointments/99999")

        assert response.status_code == 404

    def test_update_appointment_status(
        self, client, admin_headers, receptionist_headers
    ):
        """PATCH /appointments/{id} requiere RECEPTIONIST+."""
        doctor_id, patient_id = self._create_doctor_and_patient(
            client, admin_headers, receptionist_headers
        )
        create_resp = client.post("/api/v1/appointments/", json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_time": "2026-05-01T10:00:00",
            "appointment_type": "in_person",
        }, headers=receptionist_headers)
        appt_id = create_resp.json()["id"]

        response = client.patch(f"/api/v1/appointments/{appt_id}", json={
            "status": "CONFIRMED",
        }, headers=receptionist_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "CONFIRMED"

    def test_cancel_appointment(
        self, client, admin_headers, receptionist_headers
    ):
        """DELETE /appointments/{id} requiere RECEPTIONIST+."""
        doctor_id, patient_id = self._create_doctor_and_patient(
            client, admin_headers, receptionist_headers
        )
        create_resp = client.post("/api/v1/appointments/", json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_time": "2026-05-01T16:00:00",
            "appointment_type": "in_person",
        }, headers=receptionist_headers)
        appt_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/v1/appointments/{appt_id}",
            headers=receptionist_headers,
        )

        assert response.status_code == 204


class TestAppointmentHealthCheck:
    """Pruebas para el endpoint de health check."""

    def test_health_check(self, client):
        """GET /health es público y debe retornar status healthy."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
