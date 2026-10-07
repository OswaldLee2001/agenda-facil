#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

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


def test_list_appointment():
    response = client.get(
        "/appointments/",
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    appointments = response.json()

    assert isinstance(appointments, list)

    if appointments:
        appointment = appointments[0]

        assert "id" in appointment
        assert "professional_id" in appointment
        assert "service_id" in appointment
        assert "client_name" in appointment
        assert "client_phone" in appointment
        assert "appointment_date" in appointment
        assert "appointment_time" in appointment
        assert "status" in appointment


def test_list_appointment_requires_authentication():
    response = client.get("/appointments/")

    assert response.status_code == 401


def test_get_appointment_requires_authentication():
    response = client.get("/appointments/1")

    assert response.status_code == 401


def test_update_appointment_requires_authentication():
    response = client.put(
        "/appointments/1",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Cliente atualizado",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
            "status": "scheduled",
        },
    )

    assert response.status_code == 401


def test_delete_appointment_requires_authentication():
    response = client.delete("/appointments/1")

    assert response.status_code == 401


def test_create_appointment_outside_working_hours():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste Fora do Horário",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "19:00",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert "horário de trabalho" in data["detail"]


def test_create_appointment_rejects_conflict():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste de Conflito",
            "client_phone": "61988888888",
            "appointment_date": "2026-10-12",
            "appointment_time": "17:30",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert "agendamento nesse intervalo" in data["detail"].lower()


def test_create_appointment_rejects_blank_client_name():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "  ",
            "client_phone": "6199999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
    )

    assert response.status_code == 422


def test_get_appointment_authenticated():
    headers = get_auth_headers()

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200

    appointments = list_response.json()

    assert appointments

    appointment_id = appointments[0]["id"]

    response = client.get(
        f"/appointments/{appointment_id}",
        headers=headers,
    )

    assert response.status_code == 200

    appointment = response.json()

    assert appointment["id"] == appointment_id


def test_update_appointment_authenticated():
    headers = get_auth_headers()

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200

    appointments = list_response.json()

    assert appointments

    appointment_id = appointments[0]["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Cliente atualizado",
            "client_phone": "61977777777",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
            "status": "scheduled",
        },
        headers=headers,
    )

    assert response.status_code == 200

    appointment = response.json()

    assert appointment["id"] == appointment_id
    assert appointment["client_name"] == "Cliente atualizado"
    assert appointment["client_phone"] == "61977777777"


def test_delete_appointment_authenticated():
    headers = get_auth_headers()

    create_response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Cliente para exclusão",
            "client_phone": "61966666666",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
    )

    assert create_response.status_code == 200

    appointment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/appointments/{appointment_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert "excluído com sucesso" in data["message"]
