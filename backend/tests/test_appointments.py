#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_list_appointment():
	response = client.get("/appointments/")

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


def test_create_appointment_outside_working_hours():
	response = client.post(
		"/appointments/",
		json={
			"professional_id": 2,
			"service_id": 1,
			"client_name": "Teste Fora do Horário",
			"client_phone": "61999999999",
			"appointment_date": "2026-10-05",
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
			"appointment_date": "2026-10-05",
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
			"appointment_date": "2026-10-05",
			"appointment_time": "10:00",
		},
	)

	assert response.status_code == 422
