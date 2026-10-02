#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_list_services():
    response = client.get("/services/")

    assert response.status_code == 200

    services = response.json()

    assert isinstance(services, list)


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

    data = response.json()

    assert "não encontrado" in data["detail"].lower()


def test_create_service():
    response = client.post(
        "/services/",
        json={
            "name": "Serviço de teste automatizado",
            "description": "Criado pelo pytest",
            "duration_minutes": 30,
            "price_cents": 5000,
        },
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
    )

    assert response.status_code == 404


def test_delete_service_not_found():
    response = client.delete("/services/999999")

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
	)

	assert response.status_code == 422
	
