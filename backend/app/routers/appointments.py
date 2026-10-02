#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Appointments,
    Professional,
    ProfessionalWorkingHour,
    Service,
)
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


def has_schedule_conflict(
    db: Session,
    professional_id: int,
    appointment_date,
    appointment_time,
    service_duration: int,
    exclude_appointment_id: int | None = None,
):
    new_start = datetime.combine(
        appointment_date,
        appointment_time,
    )

    new_end = new_start + timedelta(minutes=service_duration)

    query = db.query(Appointments).filter(
        Appointments.professional_id == professional_id,
        Appointments.appointment_date == appointment_date,
    )

    if exclude_appointment_id is not None:
        query = query.filter(
            Appointments.id != exclude_appointment_id
        )

    existing_appointments = query.all()

    for existing in existing_appointments:
        if existing.status == "cancelled":
            continue

        existing_service = db.query(Service).filter(
            Service.id == existing.service_id
        ).first()

        if not existing_service:
            continue

        existing_start = datetime.combine(
            existing.appointment_date,
            existing.appointment_time,
        )

        existing_end = existing_start + timedelta(
            minutes=existing_service.duration_minutes
        )

        if new_start < existing_end and new_end > existing_start:
            return True

    return False


def validate_professional_working_hours(
    db: Session,
    professional_id: int,
    appointment_date,
    appointment_time,
    service_duration: int,
):
    weekday = appointment_date.weekday()

    working_hours = db.query(
        ProfessionalWorkingHour
    ).filter(
        ProfessionalWorkingHour.professional_id == professional_id,
        ProfessionalWorkingHour.weekday == weekday,
    ).order_by(
        ProfessionalWorkingHour.start_time
    ).all()

    if not working_hours:
        raise HTTPException(
            status_code=409,
            detail="O profissional não trabalha nesse dia.",
        )

    appointment_start = datetime.combine(
        appointment_date,
        appointment_time,
    )

    appointment_end = appointment_start + timedelta(
        minutes=service_duration
    )

    starts_before_any_period = True
    ends_after_all_periods = True

    for working_hour in working_hours:
        working_start = datetime.combine(
            appointment_date,
            working_hour.start_time,
        )

        working_end = datetime.combine(
            appointment_date,
            working_hour.end_time,
        )

        if appointment_start >= working_start:
            starts_before_any_period = False

        if appointment_end <= working_end:
            ends_after_all_periods = False

        if (
            appointment_start >= working_start
            and appointment_end <= working_end
        ):
            return

    if starts_before_any_period:
        raise HTTPException(
            status_code=409,
            detail=(
                "O agendamento começa antes do horário "
                "de trabalho do profissional."
            ),
        )

    if ends_after_all_periods:
        raise HTTPException(
            status_code=409,
            detail=(
                "O agendamento termina após o horário "
                "de trabalho do profissional."
            ),
        )

    raise HTTPException(
        status_code=409,
        detail=(
            "O agendamento não cabe em nenhum período "
            "de trabalho do profissional."
        ),
    )


def validate_appointment_datetime(
    appointment_date,
    appointment_time,
):
    now = datetime.now()

    current_date = now.date()
    current_time = now.time()

    if appointment_date < current_date:
        raise HTTPException(
            status_code=409,
            detail=(
                "Não é possível criar ou alterar um agendamento "
                "para uma data passada."
            ),
        )

    if (
        appointment_date == current_date
        and appointment_time < current_time
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Não é possível criar ou alterar um agendamento "
                "para um horário passado."
            ),
        )


def validate_status_transition(
    current_status: str,
    new_status: str,
):
    allowed_transitions = {
        "scheduled": {
            "confirmed",
            "cancelled",
        },
        "confirmed": {
            "completed",
            "cancelled",
        },
        "completed": set(),
        "cancelled": set(),
    }

    if current_status == new_status:
        return

    allowed_statuses = allowed_transitions.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Não é possível alterar o status de "
                f"'{current_status}' para '{new_status}'."
            ),
        )


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    db: Session = Depends(get_db),
):
    appointments = db.query(Appointments).all()
    return appointments


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    professional = db.query(Professional).filter(
        Professional.id == appointment_data.professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    if not professional.available:
        raise HTTPException(
            status_code=409,
            detail="O profissional não está disponível para agendamentos.",
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    if not service.available:
        raise HTTPException(
            status_code=409,
            detail="O serviço não está disponível para agendamento.",
        )

    validate_appointment_datetime(
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )

    validate_professional_working_hours(
        db=db,
        professional_id=appointment_data.professional_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        service_duration=service.duration_minutes,
    )

    if has_schedule_conflict(
        db=db,
        professional_id=appointment_data.professional_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        service_duration=service.duration_minutes,
    ):
        raise HTTPException(
            status_code=409,
            detail="O profissional já possui um agendamento nesse intervalo.",
        )

    appointment = Appointments(
        professional_id=appointment_data.professional_id,
        service_id=appointment_data.service_id,
        client_name=appointment_data.client_name,
        client_phone=appointment_data.client_phone,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )

    db.add(appointment)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar o agendamento.",
        )

    db.refresh(appointment)

    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado",
        )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado."
        )

    validate_status_transition(
        current_status=appointment.status,
        new_status=appointment_data.status,
    )

    professional = db.query(Professional).filter(
        Professional.id == appointment_data.professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    if not professional.available:
        raise HTTPException(
            status_code=409,
            detail="O profissional não está disponível para agendamentos.",
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    if not service.available:
        raise HTTPException(
            status_code=409,
            detail="O serviço não está disponível para agendamento.",
        )

    validate_appointment_datetime(
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )

    validate_professional_working_hours(
        db=db,
        professional_id=appointment_data.professional_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        service_duration=service.duration_minutes,
    )

    if has_schedule_conflict(
        db=db,
        professional_id=appointment_data.professional_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        service_duration=service.duration_minutes,
        exclude_appointment_id=appointment_id,
    ):
        raise HTTPException(
            status_code=409,
            detail="O profissional já possui um agendamento nesse intervalo.",
        )

    appointment.professional_id = appointment_data.professional_id
    appointment.service_id = appointment_data.service_id
    appointment.client_name = appointment_data.client_name
    appointment.client_phone = appointment_data.client_phone
    appointment.appointment_date = appointment_data.appointment_date
    appointment.appointment_time = appointment_data.appointment_time
    appointment.status = appointment_data.status

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar o agendamento.",
        )

    db.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}", response_model=MessageResponse)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado."
        )

    db.delete(appointment)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir o agendamento.",
        )

    return {
        "message": "Agendamento excluído com sucesso."
    }
