#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from app.core.jwt import create_access_token
from app.database import get_db
from app.models import User

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
        json={
			"email": "admin@teste.com",
			"password": "AdminTeste123!",
		},
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


def test_protected_endpoint_with_token_without_sub():
    token = create_access_token(
        {
            "email": "teste@teste.com",
        }
    )

    response = client.post(
        "/professionals/",
        json={
            "name": "Token Sem Sub",
            "email": "token.sem.sub@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Token inválido."


def test_protected_endpoint_with_invalid_sub():
    token = create_access_token(
        {
            "sub": "nao-e-um-id",
        }
    )

    response = client.post(
        "/professionals/",
        json={
            "name": "Token Sub Inválido",
            "email": "token.sub.invalido@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Token inválido."


def test_protected_endpoint_with_nonexistent_user():
    token = create_access_token(
        {
            "sub": "999999",
        }
    )

    response = client.post(
        "/professionals/",
        json={
            "name": "Usuário Inexistente",
            "email": "usuario.inexistente@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Usuário não encontrado."


def test_protected_endpoint_with_inactive_user():
    db = next(app.dependency_overrides[get_db]())

    try:
        user = db.scalar(
            select(User).where(
                User.email == LOGIN_DATA["email"]
            )
        )

        assert user is not None

        user.is_active = False
        db.commit()

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
            }
        )

        response = client.post(
            "/professionals/",
            json={
                "name": "Usuário Inativo",
                "email": "usuario.inativo@teste.com",
                "phone": "61999999999",
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 401

        data = response.json()

        assert data["detail"] == "Usuário inativo."

    finally:
        db.close()


def test_protected_endpoint_with_expired_token():
    token = create_access_token(
        {
            "sub": "1",
        }
    )

    # Cria um token explicitamente expirado.
    from app.core.config import settings
    import jwt

    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.post(
        "/professionals/",
        json={
            "name": "Token Expirado",
            "email": "token.expirado@teste.com",
            "phone": "61999999999",
        },
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Token inválido ou expirado"

