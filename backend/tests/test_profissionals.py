#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import date, time

from fastapi.testclient import TestClient

from main import app
from app.models import Appointments
from tests.conftest import TestSessionLocal

client = TestClient(app)


def get_auth_headers():
    response = client.post(
        "/auth/login",
        json={
            "email": "teste@teste.com",
            "password": "SenhaTeste123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
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
        "Authorization": f"Bearer {token}"
    }


def test_list_professionals():
    response = client.get("/professionals/")

    assert response.status_code == 200

    professionals = response.json()

    assert isinstance(professionals, list)

    if professionals:
        professional = professionals[0]

        assert "id" in professional
        assert "name" in professional
        assert "email" in professional
        assert "phone" in professional
        assert "available" in professional


def test_get_professional():
    response = client.get("/professionals/2")

    assert response.status_code == 200

    professional = response.json()

    assert professional["id"] == 2
    assert "name" in professional
    assert "email" in professional
    assert "phone" in professional
    assert "available" in professional


def test_get_professional_not_found():
    response = client.get("/professionals/999999")

    assert response.status_code == 404

    data = response.json()

    assert "não encontrado" in data["detail"].lower()


def test_create_professional_rejects_client():
    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Não Autorizado",
            "email": "nao.autorizado@example.com",
            "phone": "61977777777",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


def test_create_professional_accepts_admin():
    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Criado Pelo Admin",
            "email": "admin.profissional@example.com",
            "phone": "61966666666",
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200

    professional = response.json()

    assert professional["name"] == "Profissional Criado Pelo Admin"
    assert professional["email"] == "admin.profissional@example.com"
    assert professional["phone"] == "61966666666"


def test_create_professional():
    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional de Teste Automatizado",
            "email": "teste.automatizado.2026@example.com",
            "phone": "61977777777",
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200

    professional = response.json()

    assert professional["name"] == "Profissional de Teste Automatizado"
    assert professional["email"] == "teste.automatizado.2026@example.com"
    assert professional["phone"] == "61977777777"
    assert "id" in professional
    assert "available" in professional


def test_create_professional_rejects_duplicate_email():
    email = "teste.automatizado.2026@example.com"

    first_response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Original",
            "email": email,
            "phone": "61977777777",
        },
        headers=get_admin_headers(),
    )

    assert first_response.status_code == 200

    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Duplicado",
            "email": email,
            "phone": "61966666666",
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 409

    data = response.json()

    assert "e-mail" in data["detail"].lower()


def test_update_professional():
    response = client.put(
        "/professionals/2",
        json={
            "name": "João Silva Santos",
            "email": "joao.santos@teste.com",
            "phone": "61999999988",
            "available": True,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200

    professional = response.json()

    assert professional["id"] == 2
    assert professional["name"] == "João Silva Santos"
    assert professional["email"] == "joao.santos@teste.com"
    assert professional["phone"] == "61999999988"
    assert professional["available"] is True


def test_update_professional_not_found():
    response = client.put(
        "/professionals/999999",
        json={
            "name": "Profissional Inexistente",
            "email": "inexistente@example.com",
            "phone": "61955555555",
            "available": True,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 404


def test_delete_professional_not_found():
    response = client.delete(
        "/professionals/999999",
        headers=get_admin_headers(),
    )

    assert response.status_code == 404


def test_create_professional_rejects_invalid_email():
    response = client.post(
        "/professionals/",
        json={
            "name": "Professional com E-mail Inválido",
            "email": "email-invalido",
            "phone": "61977777777",
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 422


def test_update_professional_rejects_invalid_email():
    response = client.put(
        "/professionals/2",
        json={
            "name": "João Silva Santos",
            "email": "email-invalido",
            "phone": "619999998888",
            "available": True,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 422

def test_update_professional_rejects_client():
	response = client.put(
		"/professionals/2",
		json={
			"name": "Tentativa Não Autorizada",
			"email": "nao.autorizado.update@example.com",
			"phone": "61977777777",
			"available": True,
		},
		headers=get_auth_headers(),
	)

	
	assert response.status_code == 403
	assert "permissão" in response.json()["detail"].lower()

def test_delete_professional_rejects_client():
	response = client.delete(
		"/professionals/2",
		headers=get_auth_headers(),
	)
	
	assert response.status_code == 403
	assert "permissão" in response.json()["detail"].lower()

def test_delete_profissional_with_appointments_returns_conflict():
	response = client.delete(
		"/professionals/2",
		headers=get_admin_headers(),
	)

	assert response.status_code == 409
	assert "registros vinculados" in response.json()["detail"].lower()

	professional_response = client.get("/professionals/2")

	assert professional_response.status_code == 200

def test_available_slots_return_slots_for_working_day():
	response = client.get(
		"/professionals/2/available-slots/",
		params={
			"appointment_date": "2026-10-26",
			"service_id": 1
		},
	)

	assert response.status_code == 200

	slots = response.json()

	assert isinstance(response.json(), list)
	assert len(slots) > 0
	assert slots[0] == "09:00"
	assert slots[-1] == "17:30"

def test_available_slots_rejects_missing_professional():
	response = client.get(
		"/professionals/999999/available-slots/",
		params={
			"appointment_date": "2026-10-26",
			"service_id": 1,
		},
	)

	assert response.status_code == 404
	assert "profissional" in response.json()["detail"].lower()

def test_available_slots_reject_missing_service():
	response = client.get(
		"/professionals/2/available-slots/",
		params={
			"appointment_date": "2026-10-26",
			"service_id": 999999,
		},
	)

	assert response.status_code == 404
	assert "serviço" in response.json()["detail"].lower()

def test_available_slots_excludes_existing_appointment():
	response = client.get(
		"/professionals/2/available-slots/",
		params={
			"appointment_date": "2026-10-12",
			"service_id": 1,
		},
	)

	assert response.status_code == 200

	slots = response.json()

	assert "17:00" not in slots
	assert "17:30" not in slots

def test_available_slots_exclude_newly_created_appointment():
	db = TestSessionLocal()

	try:
		appointment = Appointments(
			professional_id=2,
			service_id=1,
			client_name="Cliente com agendamento",
			client_phone="61988888888",
			appointment_date=date(2026, 10, 26),
			appointment_time=time(10, 0),
			status="scheduled",
		)
		db.add(appointment)
		db.commit()
	finally:
		db.close()

	response = client.get(
		"/professionals/2/available-slots/",
		params={
			"appointment_date": "2026-10-26",
			"service_id": 1,
		},
	)

	assert response.status_code == 200

	slots = response.json()

	assert "09:00" in slots
	assert "10:00" not in slots
	assert "10:30" not in slots
	assert "11:00" in slots
