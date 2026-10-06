#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

LOGIN_DATA = {
    "email": "teste@teste.com",
    "password": "SenhaTeste123!",
}


def test_login_success():
    response = client.post(
        "/auth/login",
        json=LOGIN_DATA,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_invalid_email():
    response = client.post(
        "/auth/login",
        json={
            "email": "naoexiste@teste.com",
            "password": "SenhaTeste123!",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Email ou senha inválidos."


def test_login_invalid_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "teste@teste.com",
            "password": "SenhaErrada123!",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Email ou senha inválidos."


def test_protected_endpoint_without_token():
    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Sem Token",
            "email": "sem.token@teste.com",
            "phone": "61999999999",
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token():
    login_response = client.post(
        "/auth/login",
        json=LOGIN_DATA,
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Autenticado",
            "email": "autenticado@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


def test_protected_endpoint_with_invalid_token():
    response = client.post(
        "/professionals/",
        json={
            "name": "Profissional Token Inválido",
            "email": "token.invalido@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": "Bearer token-invalido",
        },
    )

    assert response.status_code == 401
