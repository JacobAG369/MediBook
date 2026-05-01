# tests/integration/test_api_auth.py
"""
Tests de integración para los endpoints de Autenticación.
Cubre registro, login, /me y validaciones de seguridad.
"""


class TestAuthRegister:
    """Pruebas para POST /api/v1/auth/register."""

    def test_register_success(self, client):
        """Debe registrar un nuevo usuario y retornar 201."""
        response = client.post("/api/v1/auth/register", json={
            "username": "nuevo_usuario",
            "email": "nuevo@medibook.com",
            "password": "SecureP@ss123",
            "role": "DOCTOR",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "nuevo_usuario"
        assert data["role"] == "DOCTOR"
        assert data["is_active"] is True
        # Nunca debe exponer la contraseña
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client):
        """Registrar un username duplicado debe retornar 409."""
        payload = {
            "username": "duplicado",
            "email": "dup1@medibook.com",
            "password": "SecureP@ss123",
        }
        client.post("/api/v1/auth/register", json=payload)

        payload["email"] = "dup2@medibook.com"
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 409

    def test_register_short_password(self, client):
        """Contraseña menor a 8 caracteres debe retornar 422."""
        response = client.post("/api/v1/auth/register", json={
            "username": "short_pass",
            "email": "short@medibook.com",
            "password": "123",
        })

        assert response.status_code == 422

    def test_register_invalid_role(self, client):
        """Rol no permitido debe retornar 422."""
        response = client.post("/api/v1/auth/register", json={
            "username": "bad_role",
            "email": "bad@medibook.com",
            "password": "SecureP@ss123",
            "role": "SUPERADMIN",
        })

        assert response.status_code == 422


class TestAuthLogin:
    """Pruebas para POST /api/v1/auth/login."""

    def test_login_success(self, client):
        """Login con credenciales correctas debe retornar token JWT."""
        # Primero registrar
        client.post("/api/v1/auth/register", json={
            "username": "login_user",
            "email": "login@medibook.com",
            "password": "SecureP@ss123",
        })

        # Luego login (OAuth2PasswordRequestForm usa form-data)
        response = client.post("/api/v1/auth/login", data={
            "username": "login_user",
            "password": "SecureP@ss123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Login con contraseña incorrecta debe retornar 401."""
        client.post("/api/v1/auth/register", json={
            "username": "wrong_pass",
            "email": "wrong@medibook.com",
            "password": "SecureP@ss123",
        })

        response = client.post("/api/v1/auth/login", data={
            "username": "wrong_pass",
            "password": "IncorrectPassword",
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login con usuario inexistente debe retornar 401."""
        response = client.post("/api/v1/auth/login", data={
            "username": "no_existe",
            "password": "SomePass123",
        })

        assert response.status_code == 401


class TestAuthMe:
    """Pruebas para GET /api/v1/auth/me."""

    def test_me_authenticated(self, client):
        """GET /me con token válido debe retornar datos del usuario."""
        # Registrar y login
        client.post("/api/v1/auth/register", json={
            "username": "me_user",
            "email": "me@medibook.com",
            "password": "SecureP@ss123",
            "role": "DOCTOR",
        })
        login_resp = client.post("/api/v1/auth/login", data={
            "username": "me_user",
            "password": "SecureP@ss123",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "me_user"
        assert data["role"] == "DOCTOR"

    def test_me_unauthenticated(self, client):
        """GET /me sin token debe retornar 401."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        """GET /me con token inválido debe retornar 401."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer token-invalido-falso",
        })

        assert response.status_code == 401
