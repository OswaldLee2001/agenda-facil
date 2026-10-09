#!/usr/bin/env python3
#!-*-coding:utf-8-*-

import os
import sys
from datetime import date, time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT_DIR))

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(autouse=True)
def override_database():
    from main import app
    from app.core.security import hash_password
    from app.database import get_db
    from app.models import (
        Service,
        Professional,
        Appointments,
        ProfessionalWorkingHour,
        User,
    )

    db = TestSessionLocal()

    # Limpa os dados dos testes anteriores.
    db.query(Appointments).delete()
    db.query(ProfessionalWorkingHour).delete()
    db.query(Professional).delete()
    db.query(Service).delete()
    db.query(User).delete()

    # Usuário cliente usado pelos testes de autenticação.
    user = User(
        name="Usuário de Teste",
        email="teste@teste.com",
        hashed_password=hash_password("SenhaTeste123!"),
        is_active=True,
        role="client",
    )

    # Usuário administrador usado pelos testes de autorização.
    admin_user = User(
        name="Administrador de Teste",
        email="admin@teste.com",
        hashed_password=hash_password("AdminTeste123!"),
        is_active=True,
        role="admin",
    )

    # Usuário profissional usado pelos testes de autorização.
    professional_user = User(
        name="Profissional de Teste",
        email="profissional@teste.com",
        hashed_password=hash_password("ProfissionalTeste123!"),
        is_active=True,
        role="professional",
    )

    # Serviço usado pelos testes.
    service = Service(
        id=1,
        name="Corte de cabelo",
        description="Corte masculino",
        duration_minutes=45,
        price_cents=5000,
        available=True,
    )

    db.add(user)
    db.add(admin_user)
    db.add(professional_user)
    db.add(service)
    db.flush()

    # Profissional associado à sua conta de acesso.
    professional = Professional(
        id=2,
        name="João Silva Santos",
        email="joao.santos@teste.com",
        phone="61999998888",
        available=True,
        user_id=professional_user.id,
    )

    db.add(professional)
    db.flush()

    # Segunda-feira: 09:00 às 18:30.
    working_hour = ProfessionalWorkingHour(
        professional_id=2,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 30),
    )

    db.add(working_hour)

    db.flush()

    # Agendamento existente para testar conflito.
    appointment = Appointments(
        professional_id=2,
        service_id=1,
        client_name="Cliente de teste",
        client_phone="61988888888",
        appointment_date=date(2026, 10, 12),
        appointment_time=time(17, 0),
        status="scheduled",
        client_user_id=user.id,
    )

    db.add(appointment)

    db.commit()

    # Como os IDs iniciais foram definidos manualmente,
    # sincronizamos as sequences do PostgreSQL.
    db.execute(
        text(
            "SELECT setval('services_id_seq', "
            "(SELECT MAX(id) FROM services))"
        )
    )

    db.execute(
        text(
            "SELECT setval('professionals_id_seq', "
            "(SELECT MAX(id) FROM professionals))"
        )
    )

    db.execute(
        text(
            "SELECT setval('professional_working_hours_id_seq', "
            "(SELECT MAX(id) FROM professional_working_hours))"
        )
    )

    db.execute(
        text(
            'SELECT setval(\'"Appointments_id_seq"\', '
            '(SELECT MAX(id) FROM "Appointments"))'
        )
    )

    db.commit()

    def get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = get_test_db

    yield

    app.dependency_overrides.clear()

    db.close()

