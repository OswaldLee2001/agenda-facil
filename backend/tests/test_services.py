#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def get_user_headers(email, password):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def get_admin_headers():
    return get_user_headers(
        "admin@teste.com",
        "AdminTeste123!",
    )


def test_list_services():
    response = client.get("/services/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_service():
    response = client.get("/services/1")

    assert response.status_code == 200

    service = response.json()

    assert service["id"] == 1
    assert "name" in service
    assert "description" in service
    assert "duration_minutes" in service
    assert "price_cents" in service
    assert "available" in service


def test_get_service_not_found():
    response = client.get("/services/999999")

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


def test_create_service():
    response = client.post(
        "/services/",
        json={
            "name": "Serviço de teste automatizado",
            "description": "Criado pelo pytest",
            "duration_minutes": 30,
            "price_cents": 5000,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200

    service = response.json()

    assert service["name"] == "Serviço de teste automatizado"
    assert service["description"] == "Criado pelo pytest"
    assert service["duration_minutes"] == 30
    assert service["price_cents"] == 5000
    assert "id" in service


def test_update_service():
    response = client.put(
        "/services/1",
        json={
            "name": "Corte de cabelo atualizado",
            "description": "Descrição atualizada",
            "duration_minutes": 50,
            "price_cents": 6000,
            "available": True,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 200

    service = response.json()

    assert service["id"] == 1
    assert service["name"] == "Corte de cabelo atualizado"
    assert service["duration_minutes"] == 50
    assert service["price_cents"] == 6000
    assert service["available"] is True


def test_update_service_not_found():
    response = client.put(
        "/services/999999",
        json={
            "name": "Serviço inexistente",
            "description": "Teste",
            "duration_minutes": 30,
            "price_cents": 5000,
            "available": True,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 404


def test_delete_service_not_found():
    response = client.delete(
        "/services/999999",
        headers=get_admin_headers(),
    )

    assert response.status_code == 404


def test_create_service_rejects_blank_name():
    response = client.post(
        "/services/",
        json={
            "name": "   ",
            "description": "Teste",
            "duration_minutes": 30,
            "price_cents": 5000,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 422


def test_create_service_rejects_zero_duration():
    response = client.post(
        "/services/",
        json={
            "name": "Serviço inválido",
            "description": "Teste",
            "duration_minutes": 0,
            "price_cents": 5000,
        },
        headers=get_admin_headers(),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("method", "url", "payload"),
    [
        (
            "POST",
            "/services/",
            {
                "name": "Serviço de teste",
                "description": "Teste",
                "duration_minutes": 30,
                "price_cents": 5000,
            },
        ),
        (
            "PUT",
            "/services/1",
            {
                "name": "Serviço atualizado",
                "description": "Teste",
                "duration_minutes": 30,
                "price_cents": 5000,
                "available": True,
            },
        ),
        ("DELETE", "/services/1", None),
    ],
)
def test_service_mutations_require_authentication(
    method, url, payload
):
    response = client.request(
        method,
        url,
        json=payload,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("teste@teste.com", "SenhaTeste123!"),
        ("profissional@teste.com", "ProfissionalTeste123!"),
    ],
)
@pytest.mark.parametrize(
    ("method", "url", "payload"),
    [
        (
            "POST",
            "/services/",
            {
                "name": "Serviço de teste",
                "description": "Teste",
                "duration_minutes": 30,
                "price_cents": 5000,
            },
        ),
        (
            "PUT",
            "/services/1",
            {
                "name": "Serviço atualizado",
                "description": "Teste",
                "duration_minutes": 30,
                "price_cents": 5000,
                "available": True,
            },
        ),
        ("DELETE", "/services/1", None),
    ],
)
def test_non_admin_cannot_mutate_services(
    email, password, method, url, payload
):
    headers = get_user_headers(email, password)

    response = client.request(
        method,
        url,
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403

