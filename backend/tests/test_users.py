#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_user_success():
	response = client.post(
		"/users/",
		json={
			"name": "Novo Usuário",
			"email": "novo.usuario@teste.com",
			"password": "SenhaNova123!",
		},
	)

	assert response.status_code == 201

	data = response.json()

	assert data["name"] == "Novo Usuário"
	assert data["email"] == "novo.usuario@teste.com"
	assert data["role"] == "client"
	assert data["is_active"] is True
	assert "hashed_password" not in data
	assert "password" not in data

def test_create_user_duplicate_email():
	response = client.post(
		"/users/",
		json={
			"name": "Usuário Duplicado",
			"email": "teste@teste.com",
			"password": "OutraSenha123!",
		},
	)

	assert response.status_code == 409
	assert response.json()["detail"] == "Email já cadastrado."

def test_create_user_invalid_email():
	response = client.post(
		"/users/",
		json={
			"name": "Email Inválido",
			"email": "nao-e-um-email",
			"password": "SenhaNova123!",
		},
	)

	assert response.status_code == 422
	
def test_create_user_missing_password():
	response = client.post(
		"/users/",
		json={
			"name": "Sem senha",
			"email": "sem.senha@teste.com",
		},
	)

	assert response.status_code == 422

def test_create_user_blank_name():
	response = client.post(
		"/users/",
		json={
			"name": "  ",
			"email": "nome.vazio@teste.com",
			"password": "SenhaNova123!",
		},
	)

	assert response.status_code == 422


def test_create_user_short_password():
	response = client.post(
		"/users/",
		json={
			"name": "Senha Curta",
			"email": "senha.curta@teste.com",
			"password": "abc123",
		},
	)

	assert response.status_code == 422
