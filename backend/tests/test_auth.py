import pytest


class TestAuth:
    def test_register_success(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "nombre": "New User",
                "carrera": "Ingenieria",
                "semestre": 1,
                "objetivo_promedio": 7.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["nombre"] == "New User"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "nombre": "Duplicate",
                "carrera": "Ingenieria",
                "semestre": 1,
                "objetivo_promedio": 7.0
            }
        )
        assert response.status_code == 400
        assert "ya registrado" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["usuario"]["email"] == "test@example.com"

    def test_login_invalid_password(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"]

    def test_login_invalid_email(self, client):
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401

    def test_get_me(self, client, auth_headers, test_user):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["nombre"] == "Test User"

    def test_get_me_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_update_me(self, client, auth_headers):
        response = client.put(
            "/api/auth/me",
            headers=auth_headers,
            json={"nombre": "Updated Name", "carrera": "Medicina"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated Name"
        assert data["carrera"] == "Medicina"
