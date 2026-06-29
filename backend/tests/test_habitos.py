import pytest


class TestHabitos:
    def test_create_habito(self, client, auth_headers):
        response = client.post(
            "/api/habitos",
            headers=auth_headers,
            json={"tipo": "descanso", "duracion_minutos": 45, "notas": "Descanso adecuado"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "descanso"
        assert data["duracion_minutos"] == 45
        assert "id" in data

    def test_get_all_habitos(self, client, auth_headers, test_habito):
        response = client.get("/api/habitos", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_habitos_by_tipo(self, client, auth_headers, test_habito):
        response = client.get("/api/habitos?tipo=descanso", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(h["tipo"] == "descanso" for h in data)

    def test_delete_habito(self, client, auth_headers, test_habito):
        response = client.delete(f"/api/habitos/{test_habito.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_create_habito_unauthorized(self, client):
        response = client.post(
            "/api/habitos",
            json={"tipo": "descanso", "duracion_minutos": 30}
        )
        assert response.status_code == 401

    def test_get_habitos_unauthorized(self, client):
        response = client.get("/api/habitos")
        assert response.status_code == 401

    def test_habitos_tipos_validos(self, client, auth_headers):
        for tipo in ["descanso", "distraccion", "ejercicio", "sueno"]:
            response = client.post(
                "/api/habitos",
                headers=auth_headers,
                json={"tipo": tipo, "duracion_minutos": 30}
            )
            assert response.status_code == 200

    def test_habitos_duracion_minima(self, client, auth_headers):
        response = client.post(
            "/api/habitos",
            headers=auth_headers,
            json={"tipo": "descanso", "duracion_minutos": 0}
        )
        assert response.status_code in [200, 422]

    def test_habitos_solo_usuario_propio(self, client, auth_headers, test_habito, db_session):
        from app.models.models import DatoHabitual
        other_habito = DatoHabitual(
            usuario_id=999,
            tipo="descanso",
            duracion_minutos=30
        )
        db_session.add(other_habito)
        db_session.commit()
        
        response = client.get("/api/habitos", headers=auth_headers)
        data = response.json()
        
        habito_ids = [h["id"] for h in data]
        assert other_habito.id not in habito_ids
