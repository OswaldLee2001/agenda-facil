#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi.testclient import TestClient

from main import app
from app.models import Professional

client = TestClient(app)

LOGIN_DATA = {
    "email": "teste@teste.com",
    "password": "SenhaTeste123!",
}


def get_auth_headers():
    response = client.post(
        "/auth/login",
        json=LOGIN_DATA,
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def get_admin_headers():
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@teste.com",
            "password": "AdminTeste123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def get_professional_headers():
    response = client.post(
        "/auth/login",
        json={
            "email": "profissional@teste.com",
            "password": "ProfissionalTeste123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_list_working_hours():
    response = client.get("/professionals/2/working-hours/")

    assert response.status_code == 200

    working_hours = response.json()

    assert isinstance(working_hours, list)

    if working_hours:
        working_hour = working_hours[0]

        assert "id" in working_hour
        assert "professional_id" in working_hour
        assert "weekday" in working_hour
        assert "start_time" in working_hour
        assert "end_time" in working_hour


def test_list_working_hours_professional_not_found():
    response = client.get("/professionals/999999/working-hours/")

    assert response.status_code == 404


def test_create_working_hour_requires_authentication():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "08:00",
            "end_time": "09:00",
        },
    )

    assert response.status_code == 401


def test_create_working_hour_rejects_overlap():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 0,
            "start_time": "15:00",
            "end_time": "17:00",
        },
        headers=get_professional_headers(),
    )

    assert response.status_code == 409
    assert "sobrepõe" in response.json()["detail"]


def test_create_working_hour_rejects_invalid_interval():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 0,
            "start_time": "17:00",
            "end_time": "15:00",
        },
        headers=get_professional_headers(),
    )

    assert response.status_code == 409
    assert "horário inicial" in response.json()["detail"].lower()


def test_create_working_hour_professional_not_found():
    response = client.post(
        "/professionals/999999/working-hours/",
        json={
            "weekday": 0,
            "start_time": "08:00",
            "end_time": "09:00",
        },
        headers=get_professional_headers(),
    )

    assert response.status_code == 404


def test_create_and_delete_working_hour():
    headers = get_professional_headers()

    create_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "08:00",
            "end_time": "09:00",
        },
        headers=headers,
    )

    assert create_response.status_code == 200

    working_hour = create_response.json()

    assert working_hour["professional_id"] == 2
    assert working_hour["weekday"] == 6
    assert working_hour["start_time"] == "08:00"
    assert working_hour["end_time"] == "09:00"

    working_hour_id = working_hour["id"]

    delete_response = client.delete(
        f"/professionals/2/working-hours/{working_hour_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert "excluído com sucesso" in delete_response.json()["message"]


def test_delete_working_hour_requires_authentication():
    response = client.delete(
        "/professionals/2/working-hours/999999"
    )

    assert response.status_code == 401


def test_delete_working_hour_not_found():
    response = client.delete(
        "/professionals/2/working-hours/999999",
        headers=get_professional_headers(),
    )

    assert response.status_code == 404


def test_create_working_hour_rejects_client():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 1,
            "start_time": "09:00",
            "end_time": "18:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


def test_update_working_hour_rejects_client():
    response = client.put(
        "/professionals/2/working-hours/1",
        json={
            "weekday": 1,
            "start_time": "10:00",
            "end_time": "17:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


def test_delete_working_hour_rejects_client():
    response = client.delete(
        "/professionals/2/working-hours/1",
        headers=get_auth_headers(),
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


def test_create_working_hour_allows_admin():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "10:00",
            "end_time": "11:00",
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200


def test_update_working_hour_allows_admin():
    create_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "10:00",
            "end_time": "11:00",
        },
        headers=get_admin_headers(),
    )

    assert create_response.status_code == 200

    working_hour_id = create_response.json()["id"]

    update_response = client.put(
        f"/professionals/2/working-hours/{working_hour_id}",
        json={
            "weekday": 6,
            "start_time": "10:00",
            "end_time": "12:00",
        },
        headers=get_admin_headers(),
    )

    assert update_response.status_code == 200

def test_update_working_hour_rejects_overlap():
    headers = get_admin_headers()

    first_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "08:00",
            "end_time": "10:00",
        },
        headers=headers,
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "10:00",
            "end_time": "12:00",
        },
        headers=headers,
    )
    assert second_response.status_code == 200

    second_id = second_response.json()["id"]

    update_response = client.put(
        f"/professionals/2/working-hours/{second_id}",
        json={
            "weekday": 6,
            "start_time": "09:00",
            "end_time": "11:00",
        },
        headers=headers,
    )

    assert update_response.status_code == 409
    assert "sobrepõe" in update_response.json()["detail"]

def test_delete_working_hour_allows_admin():
    create_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "13:00",
            "end_time": "14:00",
        },
        headers=get_admin_headers(),
    )

    assert create_response.status_code == 200

    working_hour_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/professionals/2/working-hours/{working_hour_id}",
        headers=get_admin_headers(),
    )

    assert delete_response.status_code == 200
    assert "excluído com sucesso" in delete_response.json()["message"]


def test_create_working_hour_allows_professional():
    response = client.post(
        "/professionals/2/working-hours",
        json={
            "weekday": 6,
            "start_time": "15:00",
            "end_time": "16:00",
        },
        headers=get_professional_headers(),
    )

    assert response.status_code == 200


def test_update_working_hour_allows_professional():
    create_response = client.post(
        "/professionals/2/working-hours",
        json={
            "weekday": 6,
            "start_time": "15:00",
            "end_time": "16:00",
        },
        headers=get_professional_headers(),
    )

    assert create_response.status_code == 200

    working_hour_id = create_response.json()["id"]

    update_response = client.put(
        f"/professionals/2/working-hours/{working_hour_id}",
        json={
            "weekday": 6,
            "start_time": "15:00",
            "end_time": "17:00",
        },
        headers=get_professional_headers(),
    )

    assert update_response.status_code == 200


def test_delete_working_hour_allows_professional():
    create_response = client.post(
        "/professionals/2/working-hours",
        json={
            "weekday": 6,
            "start_time": "15:00",
            "end_time": "16:00",
        },
        headers=get_professional_headers(),
    )

    assert create_response.status_code == 200

    working_hour_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/professionals/2/working-hours/{working_hour_id}",
        headers=get_professional_headers(),
    )

    assert delete_response.status_code == 200
    assert "excluído com sucesso" in delete_response.json()["message"]

def test_professional_cannot_create_working_hours_for_another_professional():
    from app.database import get_db
    from app.models import Professional

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    try:
        other_professional = (
            db.query(Professional)
            .filter(
                Professional.email == "maria.oliveira@teste.com"
            )
            .first()
        )

        assert other_professional is not None

        response = client.post(
            f"/professionals/{other_professional.id}/working-hours/",
            json={
                "weekday": 6,
                "start_time": "08:00",
                "end_time": "09:00",
            },
            headers=get_professional_headers(),
        )

        assert response.status_code == 403

    finally:
        db_generator.close()
