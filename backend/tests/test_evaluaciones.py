import pytest


class TestEvaluaciones:
    def test_create_evaluacion(self, client, auth_headers, test_materia):
        response = client.post(
            "/api/evaluaciones",
            headers=auth_headers,
            json={
                "materia_id": test_materia.id,
                "tipo": "examen",
                "nota": 7.5,
                "ponderacion": 1.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "examen"
        assert data["nota"] == 7.5
        assert "id" in data

    def test_get_all_evaluaciones(self, client, auth_headers, test_evaluacion):
        response = client.get("/api/evaluaciones", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_evaluaciones_by_materia(self, client, auth_headers, test_evaluacion):
        response = client.get(f"/api/evaluaciones?materia_id={test_evaluacion.materia_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(e["materia_id"] == test_evaluacion.materia_id for e in data)

    def test_delete_evaluacion(self, client, auth_headers, test_evaluacion):
        response = client.delete(f"/api/evaluaciones/{test_evaluacion.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_create_evaluacion_unauthorized(self, client):
        response = client.post(
            "/api/evaluaciones",
            json={"materia_id": 1, "tipo": "examen", "nota": 7.0}
        )
        assert response.status_code == 401

    def test_evaluaciones_tipos_validos(self, client, auth_headers, test_materia):
        for tipo in ["examen", "tarea", "proyecto", "quiz"]:
            response = client.post(
                "/api/evaluaciones",
                headers=auth_headers,
                json={"materia_id": test_materia.id, "tipo": tipo, "nota": 7.0}
            )
            assert response.status_code == 200

    def test_evaluacion_nota_rango_valido(self, client, auth_headers, test_materia):
        for nota in [1.0, 5.0, 10.0]:
            response = client.post(
                "/api/evaluaciones",
                headers=auth_headers,
                json={"materia_id": test_materia.id, "tipo": "examen", "nota": nota}
            )
            assert response.status_code == 200

    def test_evaluaciones_solo_usuario_propio(self, client, auth_headers, test_evaluacion, db_session):
        from app.models.models import Evaluacion
        other_evaluacion = Evaluacion(
            usuario_id=999,
            materia_id=test_evaluacion.materia_id,
            tipo="examen",
            nota=8.0,
            ponderacion=1.0
        )
        db_session.add(other_evaluacion)
        db_session.commit()
        
        response = client.get("/api/evaluaciones", headers=auth_headers)
        data = response.json()
        
        evaluacion_ids = [e["id"] for e in data]
        assert other_evaluacion.id not in evaluacion_ids
