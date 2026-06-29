import pytest


class TestMaterias:
    def test_create_materia(self, client, auth_headers):
        response = client.post(
            "/api/materias",
            headers=auth_headers,
            json={"nombre": "Física I", "objetivo_nota": 7.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Física I"
        assert data["objetivo_nota"] == 7.0
        assert "id" in data

    def test_get_all_materias(self, client, auth_headers, test_materia):
        response = client.get("/api/materias", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_materia_by_id(self, client, auth_headers, test_materia):
        response = client.get(f"/api/materias/{test_materia.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == test_materia.nombre

    def test_update_materia(self, client, auth_headers, test_materia):
        response = client.put(
            f"/api/materias/{test_materia.id}",
            headers=auth_headers,
            json={"nombre": "Física Actualizada", "objetivo_nota": 8.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Física Actualizada"
        assert data["objetivo_nota"] == 8.0

    def test_delete_materia(self, client, auth_headers, test_materia):
        response = client.delete(f"/api/materias/{test_materia.id}", headers=auth_headers)
        assert response.status_code == 200
        
        response = client.get(f"/api/materias/{test_materia.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_create_materia_unauthorized(self, client):
        response = client.post(
            "/api/materias",
            json={"nombre": "Física I", "objetivo_nota": 7.0}
        )
        assert response.status_code == 401

    def test_get_materias_unauthorized(self, client):
        response = client.get("/api/materias")
        assert response.status_code == 401

    def test_materias_only_user_specific(self, client, auth_headers, test_materia, db_session):
        from app.models.models import Materia
        other_materia = Materia(
            usuario_id=999,
            nombre="Materia de Otro Usuario",
            objetivo_nota=7.0
        )
        db_session.add(other_materia)
        db_session.commit()
        
        response = client.get("/api/materias", headers=auth_headers)
        data = response.json()
        
        materia_ids = [m["id"] for m in data]
        assert other_materia.id not in materia_ids
