#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime as real_datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

LOGIN_DATA = {
    "email": "teste@teste.com",
    "password": "SenhaTeste123!",
}


def post_with_future_clock(client, *args, **kwargs):
    fixed_now = real_datetime(2026, 10, 11, 12, 0, 0)

    with patch("app.routers.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.combine.side_effect = real_datetime.combine
        return client.post(*args, **kwargs)


def put_with_future_clock(client, *args, **kwargs):
    fixed_now = real_datetime(2026, 10, 11, 12, 0, 0)

    with patch("app.routers.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.combine.side_effect = real_datetime.combine
        return client.put(*args, **kwargs)


def get_headers_for(email, password):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200, response.json()

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


def get_auth_headers():
    return get_headers_for(
        LOGIN_DATA["email"],
        LOGIN_DATA["password"],
    )


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
    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste Fora do Horário",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "19:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert "horário de trabalho" in response.json()["detail"]


def test_create_appointment_rejects_conflict():
    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste de Conflito",
            "client_phone": "61988888888",
            "appointment_date": "2026-10-12",
            "appointment_time": "17:30",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert "agendamento nesse intervalo" in response.json()["detail"].lower()


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
        headers=get_auth_headers(),
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
    assert response.json()["id"] == appointment_id


def test_client_cannot_get_another_clients_appointment():
    from app.core.security import hash_password
    from app.database import get_db
    from app.models import Appointments, User

    db = next(app.dependency_overrides[get_db]())

    other_user = User(
        name="Outro Cliente",
        email="outro.cliente@teste.com",
        hashed_password=hash_password("OutroCliente123!"),
        is_active=True,
        role="client",
    )

    db.add(other_user)
    db.commit()

    appointment = db.query(Appointments).first()
    assert appointment is not None

    response = client.get(
        f"/appointments/{appointment.id}",
        headers=get_headers_for(
            "outro.cliente@teste.com",
            "OutroCliente123!",
        ),
    )

    assert response.status_code == 404


def test_professional_cannot_get_another_professionals_appointment():
    from app.database import get_db
    from app.models import Appointments, User

    db = next(app.dependency_overrides[get_db]())

    appointment = db.query(Appointments).first()
    assert appointment is not None

    other_professional_user = db.query(User).filter(
        User.email == "outro.profissional@teste.com"
    ).first()

    assert other_professional_user is not None

    response = client.get(
        f"/appointments/{appointment.id}",
        headers=get_headers_for(
            "outro.profissional@teste.com",
            "OutroProfissional123!",
        ),
    )

    assert response.status_code == 404


def test_professional_cannot_update_another_professionals_appointment():
    from app.database import get_db
    from app.models import Appointments, User

    db = next(app.dependency_overrides[get_db]())

    appointment = db.query(Appointments).first()
    assert appointment is not None

    other_professional_user = db.query(User).filter(
        User.email == "outro.profissional@teste.com"
    ).first()

    assert other_professional_user is not None

    response = client.put(
        f"/appointments/{appointment.id}",
        headers=get_headers_for(
            "outro.profissional@teste.com",
            "OutroProfissional123!",
        ),
        json={
            "professional_id": appointment.professional_id,
            "service_id": appointment.service_id,
            "client_name": appointment.client_name,
            "client_phone": appointment.client_phone,
            "appointment_date": str(appointment.appointment_date),
            "appointment_time": appointment.appointment_time.strftime("%H:%M"),
            "status": "confirmed",
        },
    )

    assert response.status_code == 404


def test_update_appointment_client_cannot_change_reservation_details():
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

    assert response.status_code == 403
    assert "dados da reserva não podem ser modificados" in (
        response.json()["detail"]
    )


def test_delete_appointment_client_cannot_delete_appointment():
    headers = get_auth_headers()

    create_response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Cliente para exclusão",
            "client_phone": "61966666666",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=headers,
    )

    assert create_response.status_code == 200, create_response.json()

    appointment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/appointments/{appointment_id}",
        headers=headers,
    )

    assert delete_response.status_code == 403


def test_admin_can_update_appointment():
    headers = get_headers_for(
        "admin@teste.com",
        "AdminTeste123!",
    )

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]

    response = put_with_future_clock(
        client,
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "confirmed",
        },
    )

    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "confirmed"


def test_admin_can_delete_appointment():
    headers = get_headers_for(
        "admin@teste.com",
        "AdminTeste123!",
    )

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment_id = appointments[0]["id"]

    response = client.delete(
        f"/appointments/{appointment_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Agendamento excluído com sucesso."

    get_response = client.get(
        f"/appointments/{appointment_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_client_can_cancel_own_appointment():
    headers = get_auth_headers()

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]

    response = client.put(
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "cancelled",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_client_can_cancel_appointment_with_status_only():
    headers = get_auth_headers()

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]
    response = client.patch(
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={"status": "cancelled"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_client_cannot_cancel_another_clients_appointment_with_patch():
    from app.core.security import hash_password
    from app.database import get_db
    from app.models import Appointments, User

    db = next(app.dependency_overrides[get_db]())

    other_user = User(
        name="Outro Cliente",
        email="outro.cliente.patch@teste.com",
        hashed_password=hash_password("OutroCliente123!"),
        is_active=True,
        role="client",
    )

    db.add(other_user)
    db.commit()

    appointment = db.query(Appointments).first()
    assert appointment is not None

    response = client.patch(
        f"/appointments/{appointment.id}",
        headers=get_headers_for(
            "outro.cliente.patch@teste.com",
            "OutroCliente123!",
        ),
        json={"status": "cancelled"},
    )

    assert response.status_code == 404


def test_client_cannot_confirm_own_appointment():
    headers = get_auth_headers()

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]

    response = client.put(
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "confirmed",
        },
    )

    assert response.status_code == 403
    assert "só podem cancelar" in response.json()["detail"]


def test_admin_cannot_complete_scheduled_appointment_directly():
    headers = get_headers_for(
        "admin@teste.com",
        "AdminTeste123!",
    )

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]

    response = client.put(
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "completed",
        },
    )

    assert response.status_code == 409
    assert "Não é possível alterar o status" in response.json()["detail"]


def test_admin_cannot_reopen_cancelled_appointment():
    headers = get_headers_for(
        "admin@teste.com",
        "AdminTeste123!",
    )

    list_response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert list_response.status_code == 200
    appointments = list_response.json()
    assert appointments

    appointment = appointments[0]

    cancel_response = put_with_future_clock(
        client,
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "cancelled",
        },
    )

    assert cancel_response.status_code == 200, cancel_response.json()
    assert cancel_response.json()["status"] == "cancelled"

    reopen_response = client.put(
        f"/appointments/{appointment['id']}",
        headers=headers,
        json={
            "professional_id": appointment["professional_id"],
            "service_id": appointment["service_id"],
            "client_name": appointment["client_name"],
            "client_phone": appointment["client_phone"],
            "appointment_date": appointment["appointment_date"],
            "appointment_time": appointment["appointment_time"],
            "status": "confirmed",
        },
    )

    assert reopen_response.status_code == 409
    assert "Não é possível alterar o status" in (
        reopen_response.json()["detail"]
    )


def test_create_appointment_rejects_nonexistent_professional():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 99999,
            "service_id": 1,
            "client_name": "Teste Profissional Inexistente",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profissional não encontrado."


def test_create_appointment_rejects_nonexistent_service():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 99999,
            "client_name": "Teste Serviço Inexistente",
            "client_phone": "619999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Serviço não encontrado."


def test_create_appointment_rejects_past_date():
    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste Data Passada",
            "client_phone": "61999999999",
            "appointment_date": "2020-01-01",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert "data passada" in response.json()["detail"].lower()


def test_cancelled_appointment_does_not_block_time():
    from datetime import date, time

    from app.database import get_db
    from app.models import Appointments

    db = next(app.dependency_overrides[get_db]())

    appointment = db.query(Appointments).filter(
        Appointments.professional_id == 2,
        Appointments.appointment_date == date(2026, 10, 12),
        Appointments.appointment_time == time(17, 0),
    ).first()

    assert appointment is not None

    appointment.status = "cancelled"
    db.commit()

    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Cliente após cancelamento",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "17:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 200, response.json()


def test_schedule_conflict_ignores_appointment_with_missing_service():
    from datetime import date, time
    from unittest.mock import MagicMock, patch

    from app.database import get_db
    from app.models import Appointments
    from app.routers.appointments import has_schedule_conflict

    db = next(app.dependency_overrides[get_db]())

    appointment = db.query(Appointments).filter(
        Appointments.professional_id == 2,
        Appointments.appointment_date == date(2026, 10, 12),
        Appointments.appointment_time == time(17, 0),
    ).first()

    assert appointment is not None

    appointments_query = MagicMock()
    appointments_query.filter.return_value.all.return_value = [
        appointment
    ]

    service_query = MagicMock()
    service_query.filter.return_value.first.return_value = None

    with patch.object(
        db,
        "query",
        side_effect=[appointments_query, service_query],
    ):
        result = has_schedule_conflict(
            db=db,
            professional_id=2,
            appointment_date=date(2026, 10, 12),
            appointment_time=time(17, 0),
            service_duration=45,
        )

    assert result is False


def test_create_appointment_without_working_hours():
    from app.database import get_db
    from app.models import ProfessionalWorkingHour

    db = next(app.dependency_overrides[get_db]())

    db.query(ProfessionalWorkingHour).filter(
        ProfessionalWorkingHour.professional_id == 2,
        ProfessionalWorkingHour.weekday == 0,
    ).delete(synchronize_session=False)
    db.commit()

    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste sem horário",
            "client_phone": "619999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "O profissional não trabalha nesse dia."
    )


def test_create_appointment_does_not_fit_any_working_period():
    from datetime import time

    from app.database import get_db
    from app.models import ProfessionalWorkingHour

    db = next(app.dependency_overrides[get_db]())

    db.query(ProfessionalWorkingHour).filter(
        ProfessionalWorkingHour.professional_id == 2,
        ProfessionalWorkingHour.weekday == 0,
    ).delete(synchronize_session=False)

    db.add_all([
        ProfessionalWorkingHour(
            professional_id=2,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        ),
        ProfessionalWorkingHour(
            professional_id=2,
            weekday=0,
            start_time=time(13, 0),
            end_time=time(18, 30),
        ),
    ])
    db.commit()

    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste entre períodos",
            "client_phone": "619999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "12:30",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "O agendamento não cabe em nenhum período "
        "de trabalho do profissional."
    )


def test_create_appointment_starts_before_working_hours():
    response = post_with_future_clock(
        client,
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste antes do expediente",
            "client_phone": "619999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "08:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "O agendamento começa antes do horário "
        "de trabalho do profissional."
    )


def test_create_appointment_rejects_past_time_today():
    from app.routers import appointments

    fixed_now = real_datetime(2026, 10, 12, 15, 0, 0)

    with patch.object(appointments, "datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.combine.side_effect = real_datetime.combine

        response = client.post(
            "/appointments/",
            json={
                "professional_id": 2,
                "service_id": 1,
                "client_name": "Teste horário passado",
                "client_phone": "61999999999",
                "appointment_date": "2026-10-12",
                "appointment_time": "10:00",
            },
            headers=get_auth_headers(),
        )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Não é possível criar ou alterar um agendamento "
        "para um horário passado."
    )


def test_professional_without_linked_profile_cannot_list_appointments():
    from app.core.security import hash_password
    from app.database import get_db
    from app.models import User

    db = next(app.dependency_overrides[get_db]())

    password = "SemVinculo123!"

    professional_user = User(
        name="Profissional sem Vínculo",
        email="sem.vinculo@teste.com",
        hashed_password=hash_password(password),
        is_active=True,
        role="professional",
    )

    db.add(professional_user)
    db.commit()

    response = client.get(
        "/appointments/",
        headers=get_headers_for(
            "sem.vinculo@teste.com",
            password,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Sua conta não está vinculada a um perfil profissional."
    )


def test_create_appointment_rejects_unavailable_professional():
    from app.database import get_db
    from app.models import Professional

    db = next(app.dependency_overrides[get_db]())

    professional = db.query(Professional).filter(
        Professional.id == 2
    ).first()

    assert professional is not None

    professional.available = False
    db.commit()

    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste Profissional Indisponível",
            "client_phone": "61999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "O profissional não está disponível para agendamentos."
    )


def test_create_appointment_rejects_unavailable_service():
    from app.database import get_db
    from app.models import Service

    db = next(app.dependency_overrides[get_db]())

    service = db.query(Service).filter(
        Service.id == 1
    ).first()

    assert service is not None

    service.available = False
    db.commit()

    response = client.post(
        "/appointments/",
        json={
            "professional_id": 2,
            "service_id": 1,
            "client_name": "Teste Serviço Indisponível",
            "client_phone": "619999999999",
            "appointment_date": "2026-10-12",
            "appointment_time": "10:00",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "O serviço não está disponível para agendamento."
    )


def test_update_appointment_returns_500_when_commit_fails():
    from unittest.mock import patch

    from sqlalchemy.exc import SQLAlchemyError

    from app.database import get_db
    from app.models import Appointments

    db = next(app.dependency_overrides[get_db]())

    appointment = db.query(Appointments).first()
    assert appointment is not None

    appointment_id = appointment.id

    with patch.object(
        db,
        "commit",
        side_effect=SQLAlchemyError("Falha simulada no commit"),
    ) as mocked_commit:
        response = client.put(
            f"/appointments/{appointment_id}",
            json={
                "professional_id": appointment.professional_id,
                "service_id": appointment.service_id,
                "client_name": appointment.client_name,
                "client_phone": appointment.client_phone,
                "appointment_date": str(appointment.appointment_date),
                "appointment_time": appointment.appointment_time.strftime("%H:%M"),
                "status": "cancelled",
            },
            headers=get_auth_headers(),
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Erro ao atualizar o agendamento."
    mocked_commit.assert_called_once()


def test_create_appointment_returns_500_when_commit_fails():
    from unittest.mock import patch

    from sqlalchemy.exc import SQLAlchemyError

    from app.database import get_db

    db = next(app.dependency_overrides[get_db]())

    with patch.object(
        db,
        "commit",
        side_effect=SQLAlchemyError("Falha simulada no commit"),
    ) as mocked_commit:
        response = post_with_future_clock(
            client,
            "/appointments/",
            json={
                "professional_id": 2,
                "service_id": 1,
                "client_name": "Cliente de teste",
                "client_phone": "619999999999",
                "appointment_date": "2026-10-12",
                "appointment_time": "10:00",
            },
            headers=get_auth_headers(),
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Erro ao salvar o agendamento."
    mocked_commit.assert_called_once()


def test_professional_can_list_own_appointments():
    headers = get_headers_for(
        "profissional@teste.com",
        "ProfissionalTeste123!",
    )

    response = client.get(
        "/appointments/",
        headers=headers,
    )

    assert response.status_code == 200

    appointments = response.json()
    assert len(appointments) > 0
    assert all(
        appointment["professional_id"] == 2
        for appointment in appointments
    )


def test_concurrent_bookings_reject_duplicate_slot():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from conftest import TestSessionLocal
    from app.database import get_db

    headers = get_auth_headers()
    barrier = Barrier(2)

    def get_independent_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    had_override = get_db in app.dependency_overrides
    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = get_independent_db

    def submit_booking(client_name):
        barrier.wait(timeout=10)

        return client.post(
            "/appointments/",
            json={
                "professional_id": 2,
                "service_id": 1,
                "client_name": client_name,
                "client_phone": "61999999999",
                "appointment_date": "2026-10-12",
                "appointment_time": "10:00",
            },
            headers=headers,
        )

    try:
        with patch(
            "app.routers.appointments.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = real_datetime(
                2026, 10, 11, 12, 0, 0
            )
            mock_datetime.combine.side_effect = real_datetime.combine

            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(
                        submit_booking,
                        "Cliente Concorrente A",
                    ),
                    executor.submit(
                        submit_booking,
                        "Cliente Concorrente B",
                    ),
                ]

                responses = [
                    future.result(timeout=30)
                    for future in futures
                ]

        status_codes = sorted(
            response.status_code for response in responses
        )

        assert status_codes == [200, 409], [
            (response.status_code, response.json())
            for response in responses
        ]

    finally:
        if had_override:
            app.dependency_overrides[get_db] = previous_override
        else:
            app.dependency_overrides.pop(get_db, None)

