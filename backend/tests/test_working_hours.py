#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_list_working_hours():
    response = client.get(
        "/professionals/2/working-hours/"
    )

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
    response = client.get(
        "/professionals/999999/working-hours/"
    )

    assert response.status_code == 404


def test_create_working_hour_rejects_overlap():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 0,
            "start_time": "15:00",
            "end_time": "17:00",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert "sobrepõe" in data["detail"]


def test_create_working_hour_rejects_invalid_interval():
    response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 0,
            "start_time": "17:00",
            "end_time": "15:00",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert "horário inicial" in data["detail"].lower()


def test_create_working_hour_professional_not_found():
    response = client.post(
        "/professionals/999999/working-hours/",
        json={
            "weekday": 0,
            "start_time": "08:00",
            "end_time": "09:00",
        },
    )

    assert response.status_code == 404


def test_create_and_delete_working_hour():
    create_response = client.post(
        "/professionals/2/working-hours/",
        json={
            "weekday": 6,
            "start_time": "08:00",
            "end_time": "09:00",
        },
    )

    assert create_response.status_code == 200

    working_hour = create_response.json()

    assert working_hour["professional_id"] == 2
    assert working_hour["weekday"] == 6
    assert working_hour["start_time"] == "08:00"
    assert working_hour["end_time"] == "09:00"

    working_hour_id = working_hour["id"]

    delete_response = client.delete(
        f"/professionals/2/working-hours/{working_hour_id}"
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert "excluído com sucesso" in data["message"]


def test_delete_working_hour_not_found():
    response = client.delete(
        "/professionals/2/working-hours/999999"
    )

    assert response.status_code == 404
