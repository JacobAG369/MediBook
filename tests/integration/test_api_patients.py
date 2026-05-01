# tests/integration/test_api_patients.py
"""
Tests de integración para los endpoints de Pacientes.
Incluye tests de RBAC (autenticación y autorización).
"""


class TestPatientEndpoints:
    """Pruebas de integración para /api/v1/patients."""

    def test_create_patient(self, client, receptionist_headers):
        """POST /patients debe crear un paciente (requiere RECEPTIONIST+)."""
        response = client.post("/api/v1/patients/", json={
            "full_name": "Ana García",
            "email": "ana@test.com",
            "phone": "+52 55 1234 5678",
        }, headers=receptionist_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Ana García"
        assert data["email"] == "ana@test.com"
        assert "id" in data

    def test_create_patient_unauthorized(self, client):
        """POST /patients sin token debe retornar 401."""
        response = client.post("/api/v1/patients/", json={
            "full_name": "Sin Auth",
        })

        assert response.status_code == 401

    def test_create_patient_forbidden(self, client, patient_headers):
        """POST /patients con rol PATIENT debe retornar 403."""
        response = client.post("/api/v1/patients/", json={
            "full_name": "Paciente Bajo Nivel",
        }, headers=patient_headers)

        assert response.status_code == 403

    def test_create_patient_minimal(self, client, admin_headers):
        """POST /patients con solo full_name debe funcionar."""
        response = client.post("/api/v1/patients/", json={
            "full_name": "Solo Nombre",
        }, headers=admin_headers)

        assert response.status_code == 201

    def test_create_patient_invalid_email(self, client, receptionist_headers):
        """POST /patients con email inválido debe retornar 422."""
        response = client.post("/api/v1/patients/", json={
            "full_name": "Test",
            "email": "no-es-email",
        }, headers=receptionist_headers)

        assert response.status_code == 422

    def test_list_patients(self, client):
        """GET /patients es público (sin auth)."""
        response = client.get("/api/v1/patients/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_patient_by_id(self, client, receptionist_headers):
        """GET /patients/{id} debe retornar el paciente correcto."""
        create_resp = client.post("/api/v1/patients/", json={
            "full_name": "Paciente Específico"
        }, headers=receptionist_headers)
        patient_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 200
        assert response.json()["full_name"] == "Paciente Específico"

    def test_get_patient_not_found(self, client):
        """GET /patients/{id} con ID inexistente debe retornar 404."""
        response = client.get("/api/v1/patients/99999")

        assert response.status_code == 404

    def test_update_patient(self, client, receptionist_headers):
        """PATCH /patients/{id} requiere RECEPTIONIST+."""
        create_resp = client.post("/api/v1/patients/", json={
            "full_name": "Nombre Original"
        }, headers=receptionist_headers)
        patient_id = create_resp.json()["id"]

        response = client.patch(f"/api/v1/patients/{patient_id}", json={
            "full_name": "Nombre Actualizado",
        }, headers=receptionist_headers)

        assert response.status_code == 200
        assert response.json()["full_name"] == "Nombre Actualizado"

    def test_delete_patient(self, client, admin_headers, receptionist_headers):
        """DELETE /patients/{id} requiere ADMIN."""
        create_resp = client.post("/api/v1/patients/", json={
            "full_name": "Para Eliminar"
        }, headers=receptionist_headers)
        patient_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/v1/patients/{patient_id}",
            headers=admin_headers,
        )

        assert response.status_code == 204

    def test_delete_patient_forbidden(self, client, receptionist_headers):
        """DELETE /patients/{id} con RECEPTIONIST debe retornar 403."""
        create_resp = client.post("/api/v1/patients/", json={
            "full_name": "No Borrar"
        }, headers=receptionist_headers)
        patient_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/v1/patients/{patient_id}",
            headers=receptionist_headers,
        )

        assert response.status_code == 403
