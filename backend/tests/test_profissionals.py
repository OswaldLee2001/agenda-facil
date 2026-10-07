#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

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
