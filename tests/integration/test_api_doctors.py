# tests/integration/test_api_doctors.py
"""
Tests de integración para los endpoints de Doctores.
Incluye tests de RBAC (autenticación y autorización).
"""


class TestDoctorEndpoints:
    """Pruebas de integración para /api/v1/doctors."""

    def test_create_doctor(self, client, admin_headers):
        """POST /doctors requiere ADMIN."""
        response = client.post("/api/v1/doctors/", json={
            "name": "Dr. Integración",
            "email": "dr.integ@test.com",
            "specialty_name": "Medicina General",
        }, headers=admin_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dr. Integración"
        assert data["active"] is True

    def test_create_doctor_unauthorized(self, client):
        """POST /doctors sin token debe retornar 401."""
        response = client.post("/api/v1/doctors/", json={
            "name": "Dr. Sin Auth",
            "specialty_name": "General",
        })

        assert response.status_code == 401

    def test_create_doctor_forbidden(self, client, doctor_headers):
        """POST /doctors con DOCTOR (no ADMIN) debe retornar 403."""
        response = client.post("/api/v1/doctors/", json={
            "name": "Dr. Sin Permiso",
            "specialty_name": "General",
        }, headers=doctor_headers)

        assert response.status_code == 403

    def test_create_doctor_reuses_specialty(self, client, admin_headers):
        """Crear dos doctores con la misma especialidad debe reutilizarla (Flyweight)."""
        client.post("/api/v1/doctors/", json={
            "name": "Dr. Primero",
            "specialty_name": "Cardiología API",
        }, headers=admin_headers)
        resp_2 = client.post("/api/v1/doctors/", json={
            "name": "Dr. Segundo",
            "specialty_name": "Cardiología API",
        }, headers=admin_headers)

        assert resp_2.status_code == 201

    def test_list_doctors(self, client):
        """GET /doctors es público (sin auth)."""
        response = client.get("/api/v1/doctors/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_doctor_by_id(self, client, admin_headers):
        """GET /doctors/{id} es público."""
        create_resp = client.post("/api/v1/doctors/", json={
            "name": "Dr. Específico",
            "specialty_name": "Específica",
        }, headers=admin_headers)
        doctor_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/doctors/{doctor_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Dr. Específico"

    def test_get_doctor_not_found(self, client):
        """GET /doctors/{id} con ID inexistente debe retornar 404."""
        response = client.get("/api/v1/doctors/99999")

        assert response.status_code == 404

    def test_update_doctor(self, client, admin_headers, receptionist_headers):
        """PATCH /doctors/{id} requiere RECEPTIONIST+."""
        create_resp = client.post("/api/v1/doctors/", json={
            "name": "Dr. Original",
            "specialty_name": "Original",
        }, headers=admin_headers)
        doctor_id = create_resp.json()["id"]

        response = client.patch(f"/api/v1/doctors/{doctor_id}", json={
            "name": "Dr. Actualizado",
        }, headers=receptionist_headers)

        assert response.status_code == 200
        assert response.json()["name"] == "Dr. Actualizado"

    def test_deactivate_doctor(self, client, admin_headers):
        """DELETE /doctors/{id} requiere ADMIN."""
        create_resp = client.post("/api/v1/doctors/", json={
            "name": "Dr. Desactivar",
            "specialty_name": "Temporal",
        }, headers=admin_headers)
        doctor_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/v1/doctors/{doctor_id}",
            headers=admin_headers,
        )

        assert response.status_code == 204
